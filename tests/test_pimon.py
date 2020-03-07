import argparse
import os

from pimon import pimon, get_configuration


def test_pimon():
    config = argparse.Namespace(interval=5, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=False,
                                monitor_vpn=False,
                                reporter_prometheus=True,
                                reporter_logfile=True,
                                once=True, logfile='logfile.txt', stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp')
    assert pimon(config) == 0
    os.remove('logfile.txt')


def test_get_config():
    args = '--interval 25 --port 1234 --logfile log.txt --monitor-cpu-sysfs=/foo/bar --once --debug'.split()
    config = get_configuration(args)
    assert config.interval == 25
    assert config.port == 1234
    assert config.logfile == 'log.txt'
    assert config.monitor_cpu_sysfs == '/foo/bar'
    assert config.once
    assert config.debug


def test_default_config():
    config = get_configuration([])
    assert config.debug is False
    assert config.freq_filename == '/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq'
    assert config.interval == 5
    assert config.logfile == 'logfile.csv'
    assert config.monitor_cpu is True
    assert config.monitor_cpu_sysfs == '/sys'
    assert config.monitor_fan is True
    assert config.monitor_vpn is False
    assert config.monitor_vpn_client_status == 'client.status'
    assert config.once is False
    assert config.port == 8080
    assert config.reporter_logfile is False
    assert config.reporter_prometheus is True
    assert config.stub is False
    assert config.monitor_cpu_sysfs == '/sys'
    assert config.monitor_fan is True
    assert config.temp_filename == '/sys/devices/virtual/thermal/thermal_zone0/temp'
