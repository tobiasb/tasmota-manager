import ipaddress
import json
from urllib.parse import quote_plus

import click
import requests


def update_by_ip(ip, configs):
    try:
        res = requests.get(url=f'http://{ip}/cm?cmnd=' 'DeviceName' '', timeout=(1, 5))
        if res.status_code >= 300:
            print(f'{ip} returned {res.status_code}')
            return
        device_name = res.json()["DeviceName"]
        device_id = device_name.split(' ')[-1]

        config = {**configs['default'], **configs.get(device_id, {})}
        cmd = quote_plus(f'Backlog {" ".join([ f"{k} {v};" for k,v in config.items() ])}')

        res = requests.post(url=f'http://{ip}/cm?cmnd={cmd}')

        if res.status_code == 200:
            print(f'{device_name} at {ip} updated!')
        else:
            print(f'{device_name} at {ip} responded with {res.status_code}')
    except Exception:
        print(f'{ip} unreachable')


@click.command()
@click.option('--ip', default=None, help='IP address of individual device to update')
@click.option('--config', required=True, help='Path to configuration file')
@click.option('--cidr', default='192.168.1.0/24', help='CIDR to scan for Tasmota devices to update')
def update(ip, config, cidr):
    with open(config, 'r') as f:
        configs = json.loads(f.read())

    if ip:
        update_by_ip(ip, configs)
    else:
        for ip in ipaddress.IPv4Network(cidr):
            update_by_ip(str(ip), configs)


if __name__ == '__main__':
    update()
