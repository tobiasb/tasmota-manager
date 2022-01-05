# Bulk configure your devices running Tasmota

Allows you to apply a configuration to your Tasmota devices without necessarily knowing their IP addresses. Supports

- Individual devices (if you do know the IP address)
- Bulk update of devices within the network (by CIDR)

__Requires the HTTP API to be enabled on the Tasmota device__

## Getting started

```
$ pipenv install
$ pipenv run python manage-tasmotas.py --help

Usage: manage-tasmotas.py [OPTIONS]

Options:
  --ip TEXT            IP address of an individual device to update
  --config TEXT        Path to configuration file  [required]
  --cidr TEXT          CIDR to scan for Tasmota devices to update
  --web-password TEXT  WebPassword to use when calling Tasmota API
  --log-level TEXT
  --dry                Dry run only, only output discovered devices, will not
                       update their configuration
  --help               Show this message and exit.
```

The config file supports default values that apply to all devices as well as device specific overrides. It looks like this:

```
{
    "default": {
        "mqtthost": "...",
        "mqttport": "1883",
        "mqttuser": "ha",
        "mqttpassword": "...",
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
        "WebPassword": "password",
        ...
    },
    "<Tasmota friendly-name>": {
        "PowerOnState": "0",
        ...
    }
}
```

Use the Tasmota friendly-name as the key when overriding configuration values for a specific device. See https://tasmota.github.io/docs/Commands/ for the list of commands.

## Housekeeping

`black --skip-string-normalization --line-length 120 . && isort .`