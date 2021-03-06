# Copyright 2020 by Christophe Lambin
# All rights reserved.

import logging
from prometheus_client import start_http_server
from libpimon.version import version
from libpimon.configuration import print_configuration
from libpimon.cpu import CPUTempProbe, CPUFreqProbe
from libpimon.gpio import GPIOProbe
from libpimon.openvpn import OpenVPNProbe, OpenVPNStatusProbe
from libpimon.mediacentre import TransmissionProbe, MonitorProbe
from pimetrics.scheduler import Scheduler


def initialise(config):
    scheduler = Scheduler()

    # Probes
    if config.monitor_cpu:
        try:
            scheduler.register(
                CPUFreqProbe(config.freq_filename),
                5
            )
            scheduler.register(
                CPUTempProbe(config.temp_filename, 1000),
                5
            )
        except FileNotFoundError as err:
            logging.warning(f'Could not add CPU monitor(s): {err}')
    if config.monitor_fan:
        try:
            scheduler.register(
                GPIOProbe(config.monitor_fan_pin),
                5
            )
        except RuntimeError:
            logging.warning('Could not add Fan monitor.  Possibly /dev/gpiomem isn\'t accessible?')
    if config.monitor_vpn:
        try:
            scheduler.register(
                OpenVPNProbe(config.monitor_vpn_client_status),
                5
            )
        except FileNotFoundError as err:
            logging.warning(f'Could not add OpenVPN monitor: {err}')
        if config.monitor_vpn_proxies:
            scheduler.register(
                OpenVPNStatusProbe(config.monitor_vpn_proxies),
                60
            )
        else:
            logging.warning('No VPN Proxies defined. VPN status monitoring is disabled')
    if config.monitor_mediaserver:
        if config.monitor_mediaserver_transmission:
            scheduler.register(
                TransmissionProbe(config.monitor_mediaserver_transmission),
                5
            )
        if config.monitor_mediaserver_sonarr:
            scheduler.register(
                MonitorProbe(
                    config.monitor_mediaserver_sonarr, MonitorProbe.App.sonarr,
                    config.monitor_mediaserver_sonarr_apikey),
                60
            )
        if config.monitor_mediaserver_radarr:
            scheduler.register(
                MonitorProbe(
                    config.monitor_mediaserver_radarr, MonitorProbe.App.radarr,
                    config.monitor_mediaserver_radarr_apikey),
                60
            )
    return scheduler


def pimon(config):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if config.debug else logging.INFO)
    logging.info(f'Starting pimon v{version}')
    logging.info(f'Configuration: {print_configuration(config)}')

    start_http_server(config.port)

    scheduler = initialise(config)
    if config.once:
        scheduler.run(once=True)
    else:
        while True:
            scheduler.run(duration=config.interval)
    return 0
