# pimon

Measures the PI's CPU temperature, frequency and the fan status (currently only tested with the Pimoroni fan shim) and reports them to Prometheus.

## Getting started

### Docker

Pimon can be installed in a Docker container via docker-compose:

```
version: '2'
services:
  pimon:
    image: clambin/pimon
    container_name: pimon
    volumes:
      - /sys:/host/sys:ro
    ports:
      - 8080:8080/tcp
    devices:
      - /dev/gpiomem:/dev/gpiomem
```

### Metrics

Pimom exposes the following metrics to Prometheus:

* pimon_clockspeed:  CPU clock speed (in GHz)
* pimon_temperature: CPU temperature (in ºC)
* pimon_fan:         Fan status (0: off, 1: on)

### Command line arguments:

The following command line arguments can be passed to pimon (in case of docker-compose, via a command):

```
usage: pimon.py [-h] [--wait WAIT] [--port PORT] [--sysfs SYSFS] [--debug]
                [--stub] [--version]

optional arguments:
  -h, --help     show this help message and exit
  --wait WAIT    Time to wait between measurements (default: 5 sec)
  --port PORT    Prometheus port (default: 8080)
  --sysfs SYSFS  Location of the /sys filesystem (default: /host/sys)
  --stub         Use stubs
  --debug        Set logging level to debug
  --version      show program's version number and exit

```

Example:

```
version: '2'
services:
  pimon:
    image: clambin/pimon
    container_name: pimon
    command: --wait 20
    volumes:
      - /sys:/host/sys:ro
    ports:
      - 8080:8080/tcp
    devices:
      - /dev/gpiomem:/dev/gpiomem
```

will only measure every 20 seconds.

## Authors

* **Christophe Lambin**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Uses Ben Croston's [RPI.GPOI](https://pypi.org/project/RPi.GPIO/)
