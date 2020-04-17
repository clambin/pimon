# Copyright 2020 by Christophe Lambin
# All rights reserved.

import logging
import time

from prometheus_client import start_http_server

from pimon.version import version
from pimon.configuration import print_configuration
from pimon.cpu import *
from pimon.gpio import GPIOProbe
from pimon.openvpn import OpenVPNProbe
from metrics.probe import Probes


def initialise(config):
    probes = Probes()

    # Probes
    if config.monitor_cpu:
        try:
            probes.register(CPUFreqProbe(config.freq_filename))
            probes.register(CPUTempProbe(config.temp_filename, 1000))
        except FileNotFoundError as err:
            logging.warning(f'Could not add CPU monitor(s): {err}')
    if config.monitor_fan:
        try:
            probes.register(GPIOProbe(config.monitor_fan_pin))
        except RuntimeError:
            logging.warning('Could not add Fan monitor.  Possibly /dev/gpiomem isn\'t accessible?')
    if config.monitor_vpn:
        try:
            probes.register(OpenVPNProbe(config.monitor_vpn_client_status))
        except FileNotFoundError as err:
            logging.warning(f'Could not add OpenVPN monitor: {err}')

    return probes


def pimon(config):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if config.debug else logging.INFO)
    logging.info(f'Starting pimon v{version}')
    logging.info(f'Configuration: {print_configuration(config)}')

    probes = initialise(config)
    try:
        start_http_server(config.port)
    except:
        logging.fatal('Could not start Prometheus listener')
        return 1

    while True:
        probes.run()
        if config.once:
            break
        time.sleep(config.interval)
    return 0
