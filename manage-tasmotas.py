import ipaddress
import json
import logging
from urllib.parse import quote_plus

import click
import requests


def update_by_ip(ip, configs, web_password, dry_run):
    try:
        credentials = f'user=admin&password={web_password}&' if web_password else ''

        res = requests.get(url=f'http://{ip}/cm?{credentials}cmnd=' 'DeviceName' '', timeout=(1, 5))
        if res.status_code >= 300:
            logging.warning(
                f'{ip} device discovery returned {res.status_code}, possibly Tasmota. WebPassword set maybe? ⚠️'
            )
            return
        device_name = res.json()["DeviceName"]
        device_id = device_name.split(' ')[-1]

        config = {**configs['default'], **configs.get(device_id, {})}
        cmd = quote_plus(f'Backlog {" ".join([ f"{k} {v};" for k,v in config.items() ])}')

        if dry_run:
            logging.info(f'{ip} ({device_name}) found! ℹ️')
            return

        res = requests.post(url=f'http://{ip}/cm?{credentials}cmnd={cmd}')

        if res.status_code == 200:
            logging.info(f'{ip} ({device_name}) updated! ✅')
        else:
            logging.error(f'{ip} ({device_name}) responded with {res.status_code} 🔥')
    except requests.exceptions.RequestException:
        logging.debug(f'{ip} unreachable, probably not Tasmota')


@click.command()
@click.option('--ip', default=None, help='IP address of an individual device to update')
@click.option('--config', required=True, help='Path to configuration file')
@click.option('--cidr', default='192.168.1.0/24', help='CIDR to scan for Tasmota devices to update')
@click.option('--web-password', help='WebPassword to use when calling Tasmota API')
@click.option('--log-level', default='info')
@click.option(
    '--dry',
    default=False,
    is_flag=True,
    help='Dry run only, only output discovered devices, will not update their configuration',
)
def update(ip, config, cidr, web_password, log_level, dry):
    with open(config, 'r') as f:
        configs = json.loads(f.read())

    logging.basicConfig(format='%(message)s', level=log_level.upper())

    if ip:
        update_by_ip(ip, configs, web_password, dry)
    else:
        for ip in list(ipaddress.IPv4Network(cidr))[1:]:
            update_by_ip(str(ip), configs, web_password, dry)


if __name__ == '__main__':
    update()
