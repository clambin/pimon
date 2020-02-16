# Copyright 2020 by Christophe Lambin
# All rights reserved.

import time
import argparse
import logging
from prometheus_client import start_http_server, Gauge

import version

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    # Use a stub instead
    import GPIO


# TODO: align with Pinger
class Metric:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.gauge = Gauge(name, description)

    def __str__(self):
        return ""

    def measure(self):
        return None

    def report(self):
        val = self.measure()
        logging.debug(f'{self.name}: {val}')
        self.gauge.set(val)


class FileMetric(Metric):
    def __init__(self, name, description, fname, divider=1):
        super().__init__(name, description)
        self.fname = fname
        self.divider = divider

    def __str__(self):
        return self.fname

    def measure(self):
        f = open(self.fname)
        data = f.readline()
        f.close()
        data = float(data) / self.divider
        return data


class GPIOMetric(Metric):
    def __init__(self, name, description, pin):
        super().__init__(name, description)
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def __str__(self):
        return f'GPIO pin {self.pin}'

    def measure(self):
        return GPIO.input(self.pin)


class Reporter:
    def __init__(self, portno):
        self.portno = portno
        self.metrics = {}

    def start(self):
        start_http_server(self.portno)

    def add(self, metric):
        logging.info(f'New metric {metric.name} for {metric}')
        self.metrics[metric.name] = metric

    def report(self):
        for metric in self.metrics.keys():
            self.metrics[metric].report()


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
    parser.add_argument('--once', action='store_true',
                        help='Measure once and then terminate')
    parser.add_argument('--stub', action='store_true',
                        help='Use stubs (for debugging only')
    parser.add_argument('--debug', action='store_true',
                        help='Set logging level to debug')
    return parser.parse_args()


def print_config(cfg):
    return ', '.join([f'{key}={val}' for key, val in vars(cfg).items()])


if __name__ == '__main__':
    config = get_config()
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if config.debug else logging.INFO)
    logging.info('Starting.')
    logging.info(f'Configuration: {print_config(config)}')

    temp_fname = './temp' if config.stub else f'{config.sys}/devices/virtual/thermal/thermal_zone0/temp'
    freq_fname = './freq' if config.stub else f'{config.sys}/devices/system/cpu/cpufreq/policy0/scaling_cur_freq'

    reporter = Reporter(config.port)
    reporter.add(FileMetric('pimon_clockspeed', 'CPU clock speed', freq_fname))
    reporter.add(FileMetric('pimon_temperature', 'CPU temperature', temp_fname, 1000))
    try:
        reporter.add(GPIOMetric('pimon_fan', 'RPI Fan Status', 18))
    except RuntimeError:
        logging.warning('Could not add Fan monitor.  Possibly /dev/gpiomem isn\'t accessible?')

    try:
        reporter.start()
    except OSError as err:
        print(f"Could not start prometheus client on port {config.port}: {err}")
        exit(1)

    while True:
        reporter.report()
        if config.once:
            break
        time.sleep(config.interval)
