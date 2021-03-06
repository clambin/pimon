import argparse
import pytest
from libpimon.configuration import str2bool, get_configuration


def test_str2bool():
    assert str2bool(True) is True
    for arg in ['yes', 'true', 't', 'y', '1', 'on']:
        assert str2bool(arg) is True
    for arg in ['no', 'false', 'f', 'n', '0', 'off']:
        assert str2bool(arg) is False
    with pytest.raises(argparse.ArgumentTypeError) as e:
        assert str2bool('maybe')
    assert str(e.value) == 'Boolean value expected.'


def test_get_config():
    args = '--interval 25 --port 1234 --monitor-cpu-sysfs=/foo/bar --once --debug'.split()
    config = get_configuration(args)
    assert config.interval == 25
    assert config.port == 1234
    assert config.monitor_cpu_sysfs == '/foo/bar'
    assert config.once
    assert config.debug


def test_default_config():
    config = get_configuration([])
    assert config.debug is False
    assert config.freq_filename == '/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq'
    assert config.interval == 5
    assert config.monitor_cpu is True
    assert config.monitor_cpu_sysfs == '/sys'
    assert config.monitor_fan is True
    assert config.monitor_fan_pin == 18
    assert config.monitor_vpn is False
    assert config.monitor_vpn_client_status == 'client.status'
    assert config.once is False
    assert config.port == 8080
    assert config.stub is False
    assert config.monitor_cpu_sysfs == '/sys'
    assert config.monitor_fan is True
    assert config.temp_filename == '/sys/devices/virtual/thermal/thermal_zone0/temp'
    assert config.monitor_vpn is False
    assert config.monitor_vpn_client_status == 'client.status'
    assert config.monitor_vpn_proxies == ''
    assert config.monitor_mediaserver is False
    assert config.monitor_mediaserver_transmission == ''
    assert config.monitor_mediaserver_sonarr == ''
    assert config.monitor_mediaserver_sonarr_apikey == ''
    assert config.monitor_mediaserver_radarr == ''
    assert config.monitor_mediaserver_radarr_apikey == ''
