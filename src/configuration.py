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
    parser.add_argument('--monitor-cpu', type=str2bool, nargs='?', default=True,
                        help='Enable/Disable monitoring the CPU status (default: on)')
    parser.add_argument('--monitor-cpu-sysfs', default=default_sys,
                        help=f'Location of the /sys filesystem (default: {default_sys})')
    # Fan status monitoring
    parser.add_argument('--monitor-fan', type=str2bool, nargs='?', default=True,
                        help='Enable/Disable monitoring the fan status (default: on)')
    # OpenVPN monitoring
    parser.add_argument('--monitor-vpn', type=str2bool, nargs='?', default=False,
                        help='Enable/disable OpenVPN client metrics (default: off)')
    parser.add_argument('--monitor-vpn-client-status', default=default_vpn_client_status,
                        help='OpenVPN client status file')
    parser.add_argument('--monitor-vpn-proxies', default='',
                        help='Comma-separated list of OpenVPN proxies to use to check connectivity. '
                             'Requires running a proxy alongside the openvpn server (eg haugene/transmission-openvpn)')
    # Media server monitoring
    parser.add_argument('--monitor-mediaserver', type=str2bool, nargs='?', default=False,
                        help='Enable/disable mediaserver metrics (default: off')
    parser.add_argument('--monitor-mediaserver-transmission', default='',
                        help='Transmission address (<host>:<port>)')
    parser.add_argument('--monitor-mediaserver-sonarr', default='',
                        help='Sonarr address (<host>:<port>)')
    parser.add_argument('--monitor-mediaserver-sonarr-apikey', default='',
                        help='Sonarr API Key')
    parser.add_argument('--monitor-mediaserver-radarr', default='',
                        help='Radarr address (<host>:<port>)')
    parser.add_argument('--monitor-mediaserver-radarr-apikey', default='',
                        help='Radarr API Key')
    args = parser.parse_args(args)
    setattr(args, 'temp_filename',
            'tests/temp' if args.stub else
            f'{args.monitor_cpu_sysfs}/devices/virtual/thermal/thermal_zone0/temp')
    setattr(args, 'freq_filename',
            'tests/freq' if args.stub else
            f'{args.monitor_cpu_sysfs}/devices/system/cpu/cpufreq/policy0/scaling_cur_freq')

    # Pimoroni fan shim uses pin 18 of the GPIO to control the fan
    # No need to make this an argument (yet), but we'll already put it in configuration
    # We'll use this in test_pimon to trigger an exception when accessing the GPIO
    setattr(args, 'monitor_fan_pin', 18)
    return args


def print_configuration(config):
    return ', '.join([f'{key}={val}' for key, val in vars(config).items()])
