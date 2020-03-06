# Copyright 2020 by Christophe Lambin
# All rights reserved.

import time
import argparse
import re
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


class SubProbe(Probe):
    def __init__(self, name, parent):
        super().__init__()
        self.name = name
        self.parent = parent

    def measure(self):
        try:
            return self.parent.probes[self.name]['value']
        except KeyError:
            return None


class OpenVPNClientStatusProbe(FileProbe):
    def __init__(self, filename):
        super().__init__(filename)
        self.probes = {
             'client_auth_read': {
                 'regex': r'Auth read bytes,(\d+)',
                 'probe': SubProbe('client_auth_read', self),
                 'value': None
             },
             'client_pre_compress': {
                 'regex': r'pre-compress bytes,(\d+)',
                 'probe': SubProbe('client_pre_compress', self),
                 'value': None
             },
             'client_pre_decompress': {
                 'regex': r'pre-decompress bytes,(\d+)',
                 'probe': SubProbe('client_pre_decompress', self),
                 'value': None
             },
             'client_post_decompress': {
                 'regex': r'post-decompress bytes,(\d+)',
                 'probe': SubProbe('client_post_decompress', self),
                 'value': None
             },
             'client_post_compress': {
                 'regex': r'post-compress bytes,(\d+)',
                 'probe': SubProbe('client_post_compress', self),
                 'value': None
             },
             'client_tcp_udp_read': {
                 'regex': r'TCP/UDP read bytes,(\d+)',
                 'probe': SubProbe('client_tcp_udp_read', self),
                 'value': None
             },
             'client_tcp_udp_write': {
                 'regex': r'TCP/UDP write bytes,(\d+)',
                 'probe': SubProbe('client_tcp_udp_write', self),
                 'value': None
             },
             'client_tun_tap_read': {
                 'regex': r'TUN/TAP read bytes,(\d+)',
                 'probe': SubProbe('client_tun_tap_read', self),
                 'value': None
             },
             'client_tun_tap_write': {
                 'regex': r'TUN/TAP write bytes,(\d+)',
                 'probe': SubProbe('client_tun_tap_write', self),
                 'value': None
             },
        }

    def get_probe(self, name):
        try:
            return self.probes[name]['probe']
        except KeyError as err:
            logging.warning(err)
            return None

    def set_probe_value(self, name, value):
        try:
            self.probes[name]['value'] = value
        except KeyError as err:
            logging.warning(err)

    def measure(self):
        with open(self.filename) as f:
            content = '\n'.join(f.readlines())
            for name in self.probes.keys():
                regex = self.probes[name]['regex']
                result = re.search(regex, content)
                if result:
                    val = int(result.group(1))
                    logging.debug(f'{name}: {val}')
                    self.set_probe_value(name, val)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_configuration(args=None):
    default_interval = 5
    default_port = 8080
    default_sys = '/sys'
    default_log = None
    default_vpn_client_status = 'client.status'

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f'%(prog)s {version.version}')
    parser.add_argument('--interval', type=int, default=default_interval,
                        help=f'Time between measurements (default: {default_interval} sec)')
    parser.add_argument('--port', type=int, default=default_port,
                        help=f'Prometheus port (default: {default_port})')
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
    parser.add_argument('--monitor-openvpn', type=str2bool, nargs='?', default=False,
                        help='Enable/disable OpenVPN client metrics')
    parser.add_argument('--monitor-openvpn-client_status', default=default_vpn_client_status,
                        help=f'openvpn client status file')

    parser.add_argument('--once', action='store_true',
                        help='Measure once and then terminate')
    parser.add_argument('--stub', action='store_true',
                        help='Use stubs (for debugging only')
    parser.add_argument('--debug', action='store_true',
                        help='Set logging level to debug')
    args = parser.parse_args(args)
    setattr(args, 'temp_filename',
            'tests/temp' if args.stub else f'{args.monitor_cpu_sysfs}/devices/virtual/thermal/thermal_zone0/temp')
    setattr(args, 'freq_filename',
            'tests/freq' if args.stub else f'{args.monitor_cpu_sysfs}/devices/system/cpu/cpufreq/policy0/scaling_cur_freq')
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

    if config.monitor_cpu:
        reporters.add(probes.register(FileProbe(config.freq_filename)), 'pimon_clockspeed', 'CPU clock speed')
        reporters.add(probes.register(FileProbe(config.temp_filename, 1000)), 'pimon_temperature', 'CPU temperature')

    if config.monitor_fan:
        try:
            # Pimoroni fan shim uses pin 18 of the GPIO to control the fan
            reporters.add(probes.register(GPIOProbe(18)),
                          'pimon_fan', 'RPI Fan Status')
        except RuntimeError:
            logging.warning('Could not add Fan monitor.  Possibly /dev/gpiomem isn\'t accessible?')

    if config.monitor_openvpn:
        probe = probes.register(OpenVPNClientStatusProbe(config.monitor_openvpn_client_status))
        for name in probe.probes.keys():
            probes.register(probe.probes[name]['probe'])

        reporters.add(probe.get_probe('client_auth_read'),        'openvpn_client_auth_read_bytes_total', '')
        reporters.add(probe.get_probe('client_pre_compress'),     'openvpn_client_pre_compress_bytes_total', '')
        reporters.add(probe.get_probe('client_pre_decompress'),   'openvpn_client_pre_decompress_bytes_total', '')
        reporters.add(probe.get_probe('client_post_compress'),    'openvpn_client_post_compress_bytes_total', '')
        reporters.add(probe.get_probe('client_post_decompress'),  'openvpn_client_post_decompress_bytes_total', '')
        reporters.add(probe.get_probe('client_tcp_udp_read'),     'openvpn_client_tcp_udp_read_bytes_total', '')
        reporters.add(probe.get_probe('client_tcp_udp_write'),    'openvpn_client_tcp_udp_write_bytes_total', '')
        reporters.add(probe.get_probe('client_tun_tap_read'),     'openvpn_client_tun_tap_read_bytes_total', '')
        reporters.add(probe.get_probe('client_tun_tap_write'),    'openvpn_client_tun_tap_write_bytes_total', '')

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
