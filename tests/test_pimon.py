import argparse
from src.pimon import pimon, initialise
from src.cpu import CPUTempProbe, CPUFreqProbe
from src.gpio import GPIOProbe


def test_initialise():
    config = argparse.Namespace(interval=0, port=8080,
                                sysfs='.', fan=True, fan_pin=18,
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp')
    scheduler = initialise(config)
    assert len(scheduler.scheduled_items) == 3
    assert type(scheduler.scheduled_items[0].probe) is CPUFreqProbe
    assert type(scheduler.scheduled_items[1].probe) is CPUTempProbe
    assert type(scheduler.scheduled_items[2].probe) is GPIOProbe


def test_bad_temp_filename():
    config = argparse.Namespace(interval=0, port=8080,
                                sysfs='.', fan=True, fan_pin=18,
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='notafile')
    scheduler = initialise(config)
    assert len(scheduler.scheduled_items) == 2
    assert type(scheduler.scheduled_items[0].probe) is CPUFreqProbe
    assert type(scheduler.scheduled_items[1].probe) is GPIOProbe


def test_bad_fan_pin():
    config = argparse.Namespace(interval=0, port=8080,
                                sysfs='.', fan=True, fan_pin=-1,
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp')
    scheduler = initialise(config)
    assert len(scheduler.scheduled_items) == 2
    assert type(scheduler.scheduled_items[0].probe) is CPUFreqProbe
    assert type(scheduler.scheduled_items[1].probe) is CPUTempProbe


def test_pimon():
    config = argparse.Namespace(interval=0, port=8080,
                                sysfs='.', fan=True, fan_pin=18,
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp')
    assert pimon(config) == 0
