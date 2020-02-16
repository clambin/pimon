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


# TODO: adapt from pinger
DEFAULT_WAIT = 5
DEFAULT_PORT = 8080
DEFAULT_SYS = '/sys'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wait', type=int, default=DEFAULT_WAIT,
                        help=f'Time between measurements (default: {DEFAULT_WAIT} sec')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                        help=f'Prometheus port (default: {DEFAULT_PORT})')
    parser.add_argument('--sys', default=DEFAULT_SYS, help=f'Location of the /sys filesystem (default: {DEFAULT_SYS})')
    parser.add_argument('--stub', action='store_true', help='Use stubs')
    parser.add_argument('--debug', action='store_true', help='Set logging level to debug')
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logging.info('Starting')
    logging.debug(f'Args: {vars(args)}')

    temp_fname = './temp' if args.stub else f'{args.sys}/devices/virtual/thermal/thermal_zone0/temp'
    freq_fname = './freq' if args.stub else f'{args.sys}/devices/system/cpu/cpufreq/policy0/scaling_cur_freq'

    reporter = Reporter(args.port)
    reporter.add(FileMetric('pimon_clockspeed', 'CPU clock speed', freq_fname))
    reporter.add(FileMetric('pimon_temperature', 'CPU temperature', temp_fname, 1000))
    try:
        reporter.add(GPIOMetric('pimon_fan', 'RPI Fan Status', 18))
    except RuntimeError:
        logging.warning('Could not add Fan monitor.  Possibly /dev/gpiomem isn\'t accessible?')

    try:
        reporter.start()
    except OSError as err:
        print(f"Could not start prometheus client on port {args.port}: {err}")
        exit(1)

    while True:
        reporter.report()
        time.sleep(args.wait)
