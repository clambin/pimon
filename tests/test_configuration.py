import argparse
import pytest
from src.configuration import str2bool, get_configuration


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
    args = '--interval 25 --port 1234 --sysfs=/foo/bar --fan yes --once --debug'.split()
    config = get_configuration(args)
    assert config.interval == 25
    assert config.port == 1234
    assert config.sysfs == '/foo/bar'
    assert config.fan is True
    assert config.once
    assert config.debug


def test_default_config():
    config = get_configuration([])
    assert config.debug is False
    assert config.freq_filename == '/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq'
    assert config.interval == 5
    assert config.sysfs == '/sys'
    assert config.fan is True
    assert config.fan_pin == 18
    assert config.once is False
    assert config.port == 8080
    assert config.stub is False
