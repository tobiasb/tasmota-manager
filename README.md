# Bulk configure your devices running Tasmota

Allows you to discover all Tasmota running devices in your network as well as (bulk) apply a configuration to your Tasmota devices without necessarily knowing their IP addresses.

- Discover all Tasmota running devices in your network (by CIDR)
- Update individual devices (if you do know the IP address)
- Bulk update of devices within the network (by CIDR)

Note: If your Tasmota devices are protected by a HTTP API password (`WebPassword`), make sure you specify it when using the commands below. Otherwise it's not possible to determine if we're dealing with a Tasmota device from the `HTTP 401` the request returned. 

## Requirements

- Tasmota device(s) with HTTP API enabled
- Python 3 with pipenv installed

## Getting started

```
$ pipenv install
$ pipenv run python manage-tasmotas.py --help

Usage: manage-tasmotas.py [OPTIONS] COMMAND [ARGS]...

Options:
  --log-level TEXT
  --help            Show this message and exit.

Commands:
  discover
  update
  backup
```

### Discover

Finds Tasmota devices in a given network and prints their friendly-name.

```
$ pipenv run python manage-tasmotas.py discover --help
Usage: manage-tasmotas.py discover [OPTIONS]

Options:
  --cidr TEXT          CIDR to scan for Tasmota devices to update (default
                       192.168.1.0/24)
  --web-password TEXT  WebPassword to use when calling Tasmota API
  --help               Show this message and exit.
```

### Update

Updates Tasmota devices, either by specifying an individual IP or by CIDR.

```
$ pipenv run python manage-tasmotas.py update --help
Usage: manage-tasmotas.py update [OPTIONS]

Options:
  --ip TEXT            IP address of an individual device to update
  --config TEXT        Path to configuration file  [required]
  --cidr TEXT          CIDR to scan for Tasmota devices to update (default
                       192.168.1.0/24)
  --help               Show this message and exit.
```

### Backup

Backup Tasmota configurations, either by specifying an individual IP or by CIDR.

Note, when using the `--upgrade` flag, no other configuration will be applied. To apply configuration, run without flag first.

```
$ pipenv run python manage-tasmotas.py backup --help
Usage: manage-tasmotas.py backup [OPTIONS] PATH_TO_TARGET

Options:
  --ip TEXT            IP address of an individual device to update
  --cidr TEXT          CIDR to scan for Tasmota devices in (default
                       {CIDR_DEFAULT})
  --web-password TEXT  WebPassword to use when calling Tasmota API
  --upgrade            OTA upgrade device to latest firmware
  --help               Show this message and exit.
```

## Configuration format

The config file supports default values that apply to all devices as well as device specific overrides. The JSON contains dictionaries with key-value pairs of individual Tasmota commands. It looks like the following. Store it in a file and use it with the `--config` option when using this tool.

```
{ 
  "web_password": "<your tasmota admin user password>",
  "configs": {
    "default": {
        "mqtthost": "mqtt-host",
        "mqttport": "1883",
        "mqttuser": "user",
        "mqttpassword": "mqtt-password",
        "topic": "%06X",
        "fulltopic": "tasmota/%prefix%/%topic%/",
        "TelePeriod": "10",
        "latitude": "48.123",
        "longitude": "-124.123",
        "timezone": "99",
        "TimeDst": "0,0,3,1,2,-420",
        "TimeStd": "0,0,10,1,3,-480",
        "ntpserver": "pool.ntp.org",
        "SetOption65": "1",
        "WebPassword": "web-password",
        ...
    },
    "<Tasmota friendly-name>": {
        "PowerOnState": "0",
        ...
    }
  }
}
```

If you've configured your Tasmota using its console before, this would be equivalent to `Backlog mqtthost mqtt-host; mqttport 1883; mqttuser user; mqttpassword mqtt-password; topic %06X; fulltopic tasmota/%prefix%/%topic%/; TelePeriod 10; latitude 48.123; longitude -124.123; timezone -8; ...`

Use the Tasmota friendly-name as the key when overriding configuration values for a specific device.

See https://tasmota.github.io/docs/Commands/ for the full list of commands.

## Housekeeping

`black --line-length 120 . && isort .`