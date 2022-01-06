import ipaddress
import json
import logging
from urllib.parse import quote_plus

import click
import requests

CIDR_DEFAULT = '192.168.1.0/24'


def probe_ip(ip, web_password):
    try:
        credentials = f'user=admin&password={web_password}&' if web_password else ''

        res = requests.get(url=f'http://{ip}/cm?{credentials}cmnd=' 'DeviceName' '', timeout=(1, 5))
        if res.status_code >= 300:
            logging.warning(
                f'{ip} device discovery returned {res.status_code}, possibly Tasmota. WebPassword set maybe? ⚠️'
            )
            return False, ''
        device_name = res.json()["DeviceName"]
        logging.info(f'{ip} ({device_name}) found! ℹ️')
        return True, device_name

    except requests.exceptions.RequestException:
        logging.debug(f'{ip} unreachable, probably not Tasmota')
        return False, ''


def update_by_ip(ip, device_name, configs, web_password):
    try:
        credentials = f'user=admin&password={web_password}&' if web_password else ''

        config = {**configs['default'], **configs.get(device_name, {})}
        cmd = quote_plus(f'Backlog {" ".join([ f"{k} {v};" for k,v in config.items() ])}')

        res = requests.post(url=f'http://{ip}/cm?{credentials}cmnd={cmd}')

        if res.status_code == 200:
            logging.info(f'{ip} ({device_name}) updated! ✅')
        else:
            logging.error(f'{ip} ({device_name}) responded with {res.status_code} 🔥')
    except requests.exceptions.RequestException:
        logging.debug(f'{ip} unreachable, probably not Tasmota')


@click.group()
@click.option('--log-level', default='info')
def cli(log_level):
    logging.basicConfig(format='%(message)s', level=log_level.upper())


@cli.command()
@click.option('--ip', default=None, help='IP address of an individual device to update')
@click.option('--config', required=True, help='Path to configuration file')
@click.option(
    '--cidr', default=CIDR_DEFAULT, help=f'CIDR to scan for Tasmota devices to update (default {CIDR_DEFAULT})'
)
@click.option('--web-password', help='WebPassword to use when calling Tasmota API')
def update(ip, config, cidr, web_password):

    with open(config, 'r') as f:
        configs = json.loads(f.read())

    if ip:
        logging.info(f'Probing for a Tasmota device at {ip}...')
        is_tasmota, device_name = probe_ip(ip, web_password)
        if is_tasmota:
            update_by_ip(ip, device_name, configs, web_password)
    else:
        logging.info(f'Probing for Tasmota devices within CIDR {cidr}...')
        for ip in list(ipaddress.IPv4Network(cidr))[1:]:
            is_tasmota, device_name = probe_ip(ip, web_password)
            if is_tasmota:
                update_by_ip(str(ip), device_name, configs, web_password)


@cli.command()
@click.option('--cidr', default=CIDR_DEFAULT, help='CIDR to scan for Tasmota devices in (default {CIDR_DEFAULT})')
@click.option('--web-password', help='WebPassword to use when calling Tasmota API')
def discover(cidr, web_password):
    logging.info(f'Probing for Tasmota devices within CIDR {cidr}...')

    for ip in list(ipaddress.IPv4Network(cidr))[1:]:
        probe_ip(ip, web_password)


if __name__ == '__main__':
    cli()
