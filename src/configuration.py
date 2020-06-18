import argparse

from src.version import version


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
    default_vpn_client_status = 'client.status'

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    parser.add_argument('--interval', type=int, default=default_interval,
                        help=f'Time between measurements (default: {default_interval} sec)')
    parser.add_argument('--port', type=int, default=default_port,
                        help=f'Prometheus listener port (default: {default_port})')
    parser.add_argument('--once', action='store_true',
                        help='Measure once and then terminate')
    parser.add_argument('--stub', action='store_true',
                        help='Use stubs (for debugging only')
    parser.add_argument('--debug', action='store_true',
                        help='Set logging level to debug')
    # CPU monitoring
    parser.add_argument('--sysfs', default=default_sys,
                        help=f'Location of the /sys filesystem (default: {default_sys})')
    # Fan status monitoring
    parser.add_argument('--fan', type=str2bool, nargs='?', default=True,
                        help='Enable/Disable monitoring the fan status (default: on)')
    args = parser.parse_args(args)
    setattr(args, 'temp_filename',
            'tests/temp' if args.stub else
            f'{args.sysfs}/devices/virtual/thermal/thermal_zone0/temp')
    setattr(args, 'freq_filename',
            'tests/freq' if args.stub else
            f'{args.sysfs}/devices/system/cpu/cpufreq/policy0/scaling_cur_freq')

    # Pimoroni fan shim uses pin 18 of the GPIO to control the fan
    # No need to make this an argument (yet), but we'll already put it in configuration
    # We'll use this in test_pimon to trigger an exception when accessing the GPIO
    setattr(args, 'fan_pin', 18)
    return args


def print_configuration(config):
    return ', '.join([f'{key}={val}' for key, val in vars(config).items()])
