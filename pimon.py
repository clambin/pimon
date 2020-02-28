# Copyright 2020 by Christophe Lambin
# All rights reserved.

import time
import argparse
import logging

from metrics.probe import Probe, FileProbe, Probes
from metrics.reporter import Reporters, PrometheusReporter, FileReporter

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


def get_configuration(args=None):
    default_interval = 5
    default_port = 8080
    default_sys = '/sys'
    default_log = None

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f'%(prog)s {version.version}')
    parser.add_argument('--interval', type=int, default=default_interval,
                        help=f'Time between measurements (default: {default_interval} sec)')
    parser.add_argument('--port', type=int, default=default_port,
                        help=f'Prometheus port (default: {default_port})')
    parser.add_argument('--logfile', action='store', default=default_log,
                        help=f'metrics output logfile (default: {default_log})')
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
    args = parser.parse_args(args)
    setattr(args, 'temp_filename',
            'tests/temp' if args.stub else f'{args.sys}/devices/virtual/thermal/thermal_zone0/temp')
    setattr(args, 'freq_filename',
            'tests/freq' if args.stub else f'{args.sys}/devices/system/cpu/cpufreq/policy0/scaling_cur_freq')
    return args


def print_configuration(config):
    return ', '.join([f'{key}={val}' for key, val in vars(config).items()])


def pimon(config):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if config.debug else logging.INFO)
    logging.info(f'Starting pimon v{version.version}')
    logging.info(f'Configuration: {print_configuration(config)}')

    reporters = Reporters()
    probes = Probes()

    reporters.register(PrometheusReporter(config.port))
    if config.logfile:
        reporters.register(FileReporter(config.logfile))

    reporters.add(probes.register(FileProbe(config.freq_filename)),
                  'pimon_clockspeed', 'CPU clock speed')
    reporters.add(probes.register(FileProbe(config.temp_filename, 1000)),
                  'pimon_temperature', 'CPU temperature')

    if config.enable_monitor_fan:
        try:
            # Pimoroni fan shim uses pin 18 of the GPIO to control the fan
            reporters.add(probes.register(GPIOProbe(18)),
                          'pimon_fan', 'RPI Fan Status')
        except RuntimeError:
            logging.warning('Could not add Fan monitor.  Possibly /dev/gpiomem isn\'t accessible?')

    try:
        reporters.start()
    except OSError as err:
        logging.fatal(f"Could not start prometheus client on port {config.port}: {err}")
        return 1

    while True:
        probes.run()
        reporters.run()
        if config.once:
            break
        time.sleep(config.interval)
    return 0


if __name__ == '__main__':
    pimon(get_configuration())
