# Copyright 2020 by Christophe Lambin
# All rights reserved.

import time
import argparse
import logging

from metrics.probe import Probe, FileProbe, Probes
from metrics.reporter import PrometheusReporter

import version

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    # Use a stub instead
    import GPIO


class GPIOProbe(Probe):
    def __init__(self, pin):
        super().__init__()
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def measure(self):
        return GPIO.input(self.pin)


def get_config():
    default_interval = 5
    default_port = 8080
    default_sys = '/sys'

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f'%(prog)s {version.version}')
    parser.add_argument('--interval', type=int, default=default_interval,
                        help=f'Time between measurements (default: {default_interval} sec)')
    parser.add_argument('--port', type=int, default=default_port,
                        help=f'Prometheus port (default: {default_port})')
    parser.add_argument('--sys', default=default_sys,
                        help=f'Location of the /sys filesystem (default: {default_sys})')
    parser.add_argument('--enable-monitor-fan', action='store_true',
                        help='Enables monitoring the fan status')
    parser.add_argument('--once', action='store_true',
                        help='Measure once and then terminate')
    parser.add_argument('--stub', action='store_true',
                        help='Use stubs (for debugging only')
    parser.add_argument('--debug', action='store_true',
                        help='Set logging level to debug')
    args = parser.parse_args()
    setattr(args, 'temp_filename',
            'tests/temp' if args.stub else f'{args.sys}/devices/virtual/thermal/thermal_zone0/temp')
    setattr(args, 'freq_filename',
            'tests/freq' if args.stub else f'{args.sys}/devices/system/cpu/cpufreq/policy0/scaling_cur_freq')
    return args


def print_config(config):
    return ', '.join([f'{key}={val}' for key, val in vars(config).items()])


def pimon(config):
    reporter = PrometheusReporter(config.port)
    probes = Probes()

    reporter.add(probes.register(FileProbe(config.freq_filename)),
                 'pimon_clockspeed', 'CPU clock speed')
    reporter.add(probes.register(FileProbe(config.temp_filename, 1000)),
                 'pimon_temperature', 'CPU temperature')

    if config.enable_monitor_fan:
        try:
            # Pimoroni fan shim uses pin 18 of the GPIO to control the fa
            reporter.add(probes.register(GPIOProbe(18)),
                         'pimon_fan', 'RPI Fan Status')
        except RuntimeError:
            logging.warning('Could not add Fan monitor.  Possibly /dev/gpiomem isn\'t accessible?')

    try:
        reporter.start()
    except OSError as err:
        logging.fatal(f"Could not start prometheus client on port {config.port}: {err}")
        return 1

    while True:
        probes.run()
        reporter.run()
        if config.once:
            break
        time.sleep(config.interval)
    return 0


if __name__ == '__main__':
    config = get_config()
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if config.debug else logging.INFO)
    logging.info(f'Starting pimon v{version.version}')
    logging.info(f'Configuration: {print_config(config)}')

    pimon(config)
