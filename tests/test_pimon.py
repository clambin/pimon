import argparse
import os

from pimon import pimon, get_configuration


def test_pimon():
    config = argparse.Namespace(interval=5, port=8080, sys='/host/sys', once=True, enable_monitor_fan=True,
                                logfile='logfile.txt', stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp')
    assert pimon(config) == 0
    os.remove('logfile.txt')


def test_get_config():
    args = '--interval 25 --port 1234 --logfile log.txt --sys=/foo/bar --once --debug'.split()
    config = get_configuration(args)
    assert config.interval == 25
    assert config.port == 1234
    assert config.logfile == 'log.txt'
    assert config.once
    assert config.debug
    assert config.sys == '/foo/bar'


def test_default_config():
    config = get_configuration([])
    assert config.interval == 5
    assert config.port == 8080
    assert config.logfile is None
    assert config.once is False
    assert config.debug is False
    assert config.stub is False
    assert config.sys == '/sys'
    assert config.enable_monitor_fan is False
