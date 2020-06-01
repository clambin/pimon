from pimetrics.probe import SysFSProbe
from prometheus_client import Gauge

TempGAUGE = Gauge('pimon_temperature', 'RPi CPU Temperature')
FreqGAUGE = Gauge('pimon_clockspeed', 'RPi CPU Clock Speed')


class CPUTempProbe(SysFSProbe):
    def __init__(self, filename):
        super().__init__(filename, 1000)

    def report(self, output):
        TempGAUGE.set(output)


class CPUFreqProbe(SysFSProbe):
    def __init__(self, filename):
        super().__init__(filename)

    def report(self, output):
        FreqGAUGE.set(output)
