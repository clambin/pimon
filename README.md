# pimon

Measures the PI's CPU temperature, frequency and the fan status (currently only tested with the Pimoroni fan shim) and reports them to Prometheus.

## Getting started

### Docker

Pimon can be installed in a Docker container via docker-compose:

```
version: '2'
services:
  pimon:
    image: clambin/pimon:latest
    container_name: pimon
    command: --sys /host/sys --enable-monitor-fan
    volumes:
      - /sys:/host/sys:ro
    ports:
      - 8080:8080/tcp
    devices:
      - /dev/gpiomem:/dev/gpiomem
```

### Metrics

Pimom exposes the following metrics to Prometheus:

* pimon_clockspeed:  CPU clock speed (in Hz)
* pimon_temperature: CPU temperature (in ºC)
* pimon_fan:         Fan status (0: off, 1: on)

### Command line arguments:

The following command line arguments can be passed to pimon:

```
usage: pimon.py [-h] [--version] [--interval INTERVAL] [--port PORT]
                [--sys SYS] [--enable-monitor-fan] [--once] [--stub] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --interval INTERVAL   Time between measurements (default: 5 sec)
  --port PORT           Prometheus port (default: 8080)
  --sys SYS             Location of the /sys filesystem (default: /sys)
  --enable-monitor-fan  Enables monitoring the fan status
  --once                Measure once and then terminate
  --stub                Use stubs (for debugging only
  --debug               Set logging level to debug
```

## Authors

* **Christophe Lambin**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Uses Ben Croston's [RPI.GPOI](https://pypi.org/project/RPi.GPIO/)
