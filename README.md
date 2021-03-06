# pimon

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/clambin/pimon?color=green&label=Release&style=plastic)
![Codecov](https://img.shields.io/codecov/c/gh/clambin/pimon?style=plastic)
![Gitlab pipeline status (branch)](https://img.shields.io/gitlab/pipeline/clambin/pimon/master?style=plastic)
![GitHub](https://img.shields.io/github/license/clambin/pimon?style=plastic)

Collects metrics from my Raspberry PI and reports them to Prometheus.  Currently supports:

* CPU temperature & frequency
* Fan status (currently only supports the pimoroni shim fan; contact me if you use something else)
* OpenVPN status & client statistics
* Transmission, Sonarr & Radarr statistics

## Getting started

### Docker

Pimon can be installed in a Docker container via docker-compose:

```
version: '2'
services:
  pimon:
    image: clambin/pimon:latest
    container_name: pimon
    command: 
      - '--monitor-cpu-sys=/host/sys'
      - '--monitor-vpn=yes'
      - '--monitor-vpn-client-status=/data/client.status'
    volumes:
      - /sys:/host/sys:ro
      - /mnt/media/downloads/transmission-home:/data:ro
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
* openvpn_client_status
* mediaserver_active_torrent_count
* mediaserver_paused_torrent_count
* mediaserver_download_speed
* mediaserver_upload_speed
* mediaserver_calendar_count
* mediaserver_queued_count
* mediaserver_monitored_count
* mediaserver_unmonitored_count

### Command line arguments:

The following command line arguments can be passed to pimon:

```
usage: pimon.py [-h] [--version] [--interval INTERVAL] [--port PORT] [--once]
                [--stub] [--debug] [--monitor-cpu [MONITOR_CPU]]
                [--monitor-cpu-sysfs MONITOR_CPU_SYSFS]
                [--monitor-fan [MONITOR_FAN]] [--monitor-vpn [MONITOR_VPN]]
                [--monitor-vpn-client-status MONITOR_VPN_CLIENT_STATUS]
                [--monitor-vpn-proxies MONITOR_VPN_PROXIES]
                [--monitor-mediaserver [MONITOR_MEDIASERVER]]
                [--monitor-mediaserver-transmission MONITOR_MEDIASERVER_TRANSMISSION]
                [--monitor-mediaserver-sonarr MONITOR_MEDIASERVER_SONARR]
                [--monitor-mediaserver-sonarr-apikey MONITOR_MEDIASERVER_SONARR_APIKEY]
                [--monitor-mediaserver-radarr MONITOR_MEDIASERVER_RADARR]
                [--monitor-mediaserver-radarr-apikey MONITOR_MEDIASERVER_RADARR_APIKEY]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --interval INTERVAL   Time between measurements (default: 5 sec)
  --port PORT           Prometheus listener port (default: 8080)
  --once                Measure once and then terminate
  --stub                Use stubs (for debugging only
  --debug               Set logging level to debug
  --monitor-cpu [MONITOR_CPU]
                        Enable/Disable monitoring the CPU status (default: on)
  --monitor-cpu-sysfs MONITOR_CPU_SYSFS
                        Location of the /sys filesystem (default: /sys)
  --monitor-fan [MONITOR_FAN]
                        Enable/Disable monitoring the fan status (default: on)
  --monitor-vpn [MONITOR_VPN]
                        Enable/disable OpenVPN client metrics (default: off)
  --monitor-vpn-client-status MONITOR_VPN_CLIENT_STATUS
                        OpenVPN client status file
  --monitor-vpn-proxies MONITOR_VPN_PROXIES
                        Comma-separated list of OpenVPN proxies to use to
                        check connectivity. Requires running a proxy alongside
                        the openvpn server (eg haugene/transmission-openvpn)
  --monitor-mediaserver [MONITOR_MEDIASERVER]
                        Enable/disable mediaserver metrics (default: off
  --monitor-mediaserver-transmission MONITOR_MEDIASERVER_TRANSMISSION
                        Transmission address (<host>:<port>)
  --monitor-mediaserver-sonarr MONITOR_MEDIASERVER_SONARR
                        Sonarr address (<host>:<port>)
  --monitor-mediaserver-sonarr-apikey MONITOR_MEDIASERVER_SONARR_APIKEY
                        Sonarr API Key
  --monitor-mediaserver-radarr MONITOR_MEDIASERVER_RADARR
                        Radarr address (<host>:<port>)
  --monitor-mediaserver-radarr-apikey MONITOR_MEDIASERVER_RADARR_APIKEY
                        Radarr API Key
```

## Grafana

See the grafana directory for some examples of Grafana panels.

## Authors

* **Christophe Lambin**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Uses Ben Croston's [RPI.GPOI](https://pypi.org/project/RPi.GPIO/) module
* Reuses Prometheus metric names from [kumina/openvpn_exporter](https://github.com/kumina/openvpn_exporter)
