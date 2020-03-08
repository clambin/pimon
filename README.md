# pimon

Collects metrics from my Raspberry PI and reports them to Prometheus.  Currently supports:

* CPU temperature & frequency
* Fan status (currently only supports the pimoroni shim fan; contact me if you use something else)
* OpenVPN client statistics

## Getting started

### Docker

Pimon can be installed in a Docker container via docker-compose:

```
version: '2'
services:
  pimon:
    image: clambin/pimon:latest
    container_name: pimon
    command: --sys /host/sys --disable-monitor-fan
    volumes:
      - /sys:/host/sys:ro
    ports:
      - 8080:8080/tcp
    devices:
      - /dev/gpiomem:/dev/gpiomem
```

### Metrics

Pimon exposes the following metrics to Prometheus:

* pimon_clockspeed
* pimon_temperature
* pimon_fan
* openvpn_client_auth_read_bytes_total
* openvpn_client_pre_compress_bytes_total
* openvpn_client_pre_decompress_bytes_total
* openvpn_client_post_compress_bytes_total
* openvpn_client_post_decompress_bytes_total
* openvpn_client_tcp_udp_read_bytes_total
* openvpn_client_tcp_udp_write_bytes_total
* openvpn_client_tun_tap_read_bytes_total
* openvpn_client_tun_tap_write_bytes_total

### Command line arguments:

The following command line arguments can be passed to pimon:

```
sage: pimon.py [-h] [--interval INTERVAL] [--once] [--stub] [--debug]
                [--reporter-prometheus [REPORTER_PROMETHEUS]] [--port PORT]
                [--reporter-logfile [REPORTER_LOGFILE]] [--logfile LOGFILE]
                [--monitor-cpu [MONITOR_CPU]]
                [--monitor-cpu-sysfs MONITOR_CPU_SYSFS]
                [--monitor-fan [MONITOR_FAN]] [--monitor-vpn [MONITOR_VPN]]
                [--monitor-vpn-client-status MONITOR_VPN_CLIENT_STATUS]
                [--version]

optional arguments:
  -h, --help            show this help message and exit
  --interval INTERVAL   Time between measurements (default: 5 sec)
  --once                Measure once and then terminate
  --stub                Use stubs (for debugging only
  --debug               Set logging level to debug
  --reporter-prometheus [REPORTER_PROMETHEUS]
                        Report metrics to Prometheus
  --port PORT           Prometheus port (default: 8080)
  --reporter-logfile [REPORTER_LOGFILE]
                        Report metrics to a CSV logfile
  --logfile LOGFILE     metrics output logfile (default: logfile.csv)
  --monitor-cpu [MONITOR_CPU]
                        Enable/Disable monitoring the CPU status
  --monitor-cpu-sysfs MONITOR_CPU_SYSFS
                        Location of the /sys filesystem (default: /sys)
  --monitor-fan [MONITOR_FAN]
                        Enable/Disable monitoring the fan status
  --monitor-vpn [MONITOR_VPN]
                        Enable/disable OpenVPN client metrics
  --monitor-vpn-client-status MONITOR_VPN_CLIENT_STATUS
                        OpenVPN client status file
  --version             show program's version number and exit
```

## Authors

* **Christophe Lambin**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Uses Ben Croston's [RPI.GPOI](https://pypi.org/project/RPi.GPIO/) module
* Reuses Prometheus metric names from [kumina/openvpn_exporter](https://github.com/kumina/openvpn_exporter)
