# Copyright 2020 by Christophe Lambin
# All rights reserved.

import argparse
import logging
import re
import time

import version
from metrics.probe import Probe, FileProbe, Probes, ProbeAggregator
from metrics.reporter import Reporters, PrometheusReporter, FileReporter

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


class OpenVPNProbe(FileProbe, ProbeAggregator):
    metrics = {
        'client_auth_read': {
            'regex': r'Auth read bytes,(\d+)',
            'name':  r'openvpn_client_auth_read_bytes_total',
            'desc':  r'Total amount of authentication traffic read, in bytes.'},
        'client_pre_compress': {
            'regex': r'pre-compress bytes,(\d+)',
            'name':  r'openvpn_client_pre_compress_bytes_total',
            'desc':  r'Total amount of data before compression, in bytes.'},
        'client_pre_decompress': {
            'regex': r'pre-decompress bytes,(\d+)',
            'name':  r'openvpn_client_pre_decompress_bytes_total',
            'desc':  r'Total amount of data before decompression, in bytes.'},
        'client_post_compress': {
            'regex': r'post-compress bytes,(\d+)',
            'name': r'openvpn_client_post_compress_bytes_total',
            'desc': r'Total amount of data after compression, in bytes.'},
        'client_post_decompress': {
            'regex': r'post-decompress bytes,(\d+)',
            'name':  r'openvpn_client_post_decompress_bytes_total',
            'desc':  r'Total amount of data after decompression, in bytes.'},
        'client_tcp_udp_read': {
            'regex': r'TCP/UDP read bytes,(\d+)',
            'name':  r'openvpn_client_tcp_udp_read_bytes_total',
            'desc':  r'Total amount of TCP/UDP traffic read, in bytes.'},
        'client_tcp_udp_write': {
            'regex': r'TCP/UDP write bytes,(\d+)',
            'name':  r'openvpn_client_tcp_udp_write_bytes_total',
            'desc':  r'Total amount of TCP/UDP traffic written, in bytes.'},
        'client_tun_tap_read': {
            'regex': r'TUN/TAP read bytes,(\d+)',
            'name':  r'openvpn_client_tun_tap_read_bytes_total',
            'desc':  r'Total amount of TUN/TAP traffic read, in bytes.'},
        'client_tun_tap_write': {
            'regex': r'TUN/TAP write bytes,(\d+)',
            'name':  r'openvpn_client_tun_tap_write_bytes_total',
            'desc':  r'Total amount of TUN/TAP traffic written, in bytes.'}
    }

    def __init__(self, filename):
        FileProbe.__init__(self, filename)
        ProbeAggregator.__init__(self, list(self.metrics.keys()))

    def process(self, content):
        for name in self.metrics:
            result = re.search(self.metrics[name]['regex'], content)
            if result:
                val = int(result.group(1))
                self.set_value(name, val)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'on'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'off'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_configuration(args=None):
    default_interval = 5
    default_port = 8080
    default_sys = '/sys'
    default_log = 'logfile.csv'
    default_vpn_client_status = 'client.status'

    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=default_interval,
                        help=f'Time between measurements (default: {default_interval} sec)')
    parser.add_argument('--once', action='store_true',
                        help='Measure once and then terminate')
    parser.add_argument('--stub', action='store_true',
                        help='Use stubs (for debugging only')
    parser.add_argument('--debug', action='store_true',
                        help='Set logging level to debug')
    # Reporters
    parser.add_argument('--reporter-prometheus', type=str2bool, nargs='?', default=True,
                        help='Report metrics to Prometheus')
    parser.add_argument('--port', type=int, default=default_port,
                        help=f'Prometheus port (default: {default_port})')
    parser.add_argument('--reporter-logfile', type=str2bool, nargs='?', default=False,
                        help='Report metrics to a CSV logfile')
    parser.add_argument('--logfile', action='store', default=default_log,
                        help=f'metrics output logfile (default: {default_log})')
    # CPU monitoring
    parser.add_argument('--monitor-cpu', type=str2bool, nargs='?', default=True,
                        help='Enable/Disable monitoring the CPU status')
    parser.add_argument('--monitor-cpu-sysfs', default=default_sys,
                        help=f'Location of the /sys filesystem (default: {default_sys})')
    # Fan status monitoring
    parser.add_argument('--monitor-fan', type=str2bool, nargs='?', default=True,
                        help='Enable/Disable monitoring the fan status')
    # OpenVPN monitoring
    parser.add_argument('--monitor-vpn', type=str2bool, nargs='?', default=False,
                        help='Enable/disable OpenVPN client metrics')
    parser.add_argument('--monitor-vpn-client-status', default=default_vpn_client_status,
                        help=f'OpenVPN client status file')
    parser.add_argument('--version', action='version', version=f'%(prog)s {version.version}')

    args = parser.parse_args(args)
    setattr(args, 'temp_filename', 'tests/temp' if args.stub else
            f'{args.monitor_cpu_sysfs}/devices/virtual/thermal/thermal_zone0/temp')
    setattr(args, 'freq_filename', 'tests/freq' if args.stub else
            f'{args.monitor_cpu_sysfs}/devices/system/cpu/cpufreq/policy0/scaling_cur_freq')

    # Pimoroni fan shim uses pin 18 of the GPIO to control the fan
    # No need to make this an argument (yet), but we'll already put it in configuration
    # We'll use this in test_pimon to trigger an exception when accessing the GPIO
    setattr(args, 'monitor_fan_pin', 18)
    return args


def print_configuration(config):
    return ', '.join([f'{key}={val}' for key, val in vars(config).items()])


def initialise(config):
    reporters = Reporters()
    probes = Probes()

    # Reporters
    if config.reporter_prometheus:
        reporters.register(PrometheusReporter(config.port))
    if config.reporter_logfile:
        reporters.register(FileReporter(config.logfile))
    if not config.reporter_prometheus and not config.reporter_logfile:
        logging.warning('No reporters configured')

    # Ideally this should be done after initialise() but since we can only register prometheus metrics
    # once (limiting what we can cover in unit testing), we do it here.
    try:
        reporters.start()
    except Exception as err:
        logging.fatal(f"Could not start prometheus client on port {config.port}: {err}")
        raise RuntimeError

    # Probes
    if config.monitor_cpu:
        reporters.add(probes.register(FileProbe(config.freq_filename)), 'pimon_clockspeed', 'CPU clock speed')
        reporters.add(probes.register(FileProbe(config.temp_filename, 1000)), 'pimon_temperature', 'CPU temperature')
    if config.monitor_fan:
        try:
            reporters.add(probes.register(GPIOProbe(config.monitor_fan_pin)), 'pimon_fan', 'RPI Fan Status')
        except RuntimeError:
            logging.warning('Could not add Fan monitor.  Possibly /dev/gpiomem isn\'t accessible?')
    if config.monitor_vpn:
        probe = probes.register(OpenVPNProbe(config.monitor_vpn_client_status))
        for metric in OpenVPNProbe.metrics.keys():
            reporters.add(probe.get_probe(metric), probe.metrics[metric]['name'], probe.metrics[metric]['desc'])

    return probes, reporters


def pimon(config):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if config.debug else logging.INFO)
    logging.info(f'Starting pimon v{version.version}')
    logging.info(f'Configuration: {print_configuration(config)}')

    try:
        probes, reporters = initialise(config)
    except RuntimeError:
        return 1

    while True:
        time.sleep(config.interval)
        probes.run()
        reporters.run()
        if config.once:
            break
    return 0


if __name__ == '__main__':
    pimon(get_configuration())
