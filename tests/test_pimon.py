import argparse
from pimon.pimon import pimon, initialise
from pimon.cpu import CPUTempProbe, CPUFreqProbe
from pimon.gpio import GPIOProbe
from pimon.openvpn import OpenVPNProbe


def test_initialise():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=18,
                                monitor_vpn=True, monitor_vpn_client_status='client.status',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp',
                                monitor_mediaserver=False)
    probes = initialise(config)
    assert len(probes.probes) == 4
    assert type(probes.probes[0]) is CPUFreqProbe
    assert type(probes.probes[1]) is CPUTempProbe
    assert type(probes.probes[2]) is GPIOProbe
    assert type(probes.probes[3]) is OpenVPNProbe


def test_bad_temp_filename():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=18,
                                monitor_vpn=True, monitor_vpn_client_status='client.status',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='notafile',
                                monitor_mediaserver=False)
    probes = initialise(config)
    assert len(probes.probes) == 3
    assert type(probes.probes[0]) is CPUFreqProbe
    assert type(probes.probes[1]) is GPIOProbe
    assert type(probes.probes[2]) is OpenVPNProbe


def test_bad_fan_pin():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=-1,
                                monitor_vpn=True, monitor_vpn_client_status='client.status',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp',
                                monitor_mediaserver=False)
    probes = initialise(config)
    assert len(probes.probes) == 3
    assert type(probes.probes[0]) is CPUFreqProbe
    assert type(probes.probes[1]) is CPUTempProbe
    assert type(probes.probes[2]) is OpenVPNProbe


def test_bad_vpn_file():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=18,
                                monitor_vpn=True, monitor_vpn_client_status='notafile',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp',
                                monitor_mediaserver=False)
    probes = initialise(config)
    assert len(probes.probes) == 3
    assert type(probes.probes[0]) is CPUFreqProbe
    assert type(probes.probes[1]) is CPUTempProbe
    assert type(probes.probes[2]) is GPIOProbe


def test_pimon():
    config = argparse.Namespace(interval=0, port=8080,
                                monitor_cpu=True, monitor_cpu_sysfs='.',
                                monitor_fan=True, monitor_fan_pin=18,
                                monitor_vpn=True, monitor_vpn_client_status='client.status',
                                once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp',
                                monitor_mediaserver=False)
    assert pimon(config) == 0

