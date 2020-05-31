import argparse
from src.pimon import pimon, initialise
from src.cpu import CPUTempProbe, CPUFreqProbe
from src.gpio import GPIOProbe
from src.openvpn import OpenVPNProbe


def test_initialise():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=18,
                                monitor_vpn=True, monitor_vpn_client_status='client.status', monitor_vpn_proxies='',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp',
                                monitor_mediaserver=False)
    scheduler = initialise(config)
    assert len(scheduler.scheduled_items) == 4
    assert type(scheduler.scheduled_items[0].probe) is CPUFreqProbe
    assert type(scheduler.scheduled_items[1].probe) is CPUTempProbe
    assert type(scheduler.scheduled_items[2].probe) is GPIOProbe
    assert type(scheduler.scheduled_items[3].probe) is OpenVPNProbe


def test_bad_temp_filename():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=18,
                                monitor_vpn=True, monitor_vpn_client_status='client.status', monitor_vpn_proxies='',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='notafile',
                                monitor_mediaserver=False)
    scheduler = initialise(config)
    assert len(scheduler.scheduled_items) == 3
    assert type(scheduler.scheduled_items[0].probe) is CPUFreqProbe
    assert type(scheduler.scheduled_items[1].probe) is GPIOProbe
    assert type(scheduler.scheduled_items[2].probe) is OpenVPNProbe


def test_bad_fan_pin():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=-1,
                                monitor_vpn=True, monitor_vpn_client_status='client.status', monitor_vpn_proxies='',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp',
                                monitor_mediaserver=False)
    scheduler = initialise(config)
    assert len(scheduler.scheduled_items) == 3
    assert type(scheduler.scheduled_items[0].probe) is CPUFreqProbe
    assert type(scheduler.scheduled_items[1].probe) is CPUTempProbe
    assert type(scheduler.scheduled_items[2].probe) is OpenVPNProbe


def test_bad_vpn_file():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=18,
                                monitor_vpn=True, monitor_vpn_client_status='notafile', monitor_vpn_proxies='',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp',
                                monitor_mediaserver=False)
    scheduler = initialise(config)
    assert len(scheduler.scheduled_items) == 3
    assert type(scheduler.scheduled_items[0].probe) is CPUFreqProbe
    assert type(scheduler.scheduled_items[1].probe) is CPUTempProbe
    assert type(scheduler.scheduled_items[2].probe) is GPIOProbe


def test_pimon():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=18,
                                monitor_vpn=True, monitor_vpn_client_status='client.status', monitor_vpn_proxies='',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp',
                                monitor_mediaserver=False)
    assert pimon(config) == 0

