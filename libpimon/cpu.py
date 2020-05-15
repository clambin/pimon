from pimetrics.probe import SysFSProbe
from prometheus_client import Gauge

TempGAUGE = Gauge('pimon_temperature', 'RPi CPU Temperature')
FreqGAUGE = Gauge('pimon_clockspeed', 'RPi CPU Clock Speed')


class CPUTempProbe(SysFSProbe):
    def __init__(self, filename, divider=1):
        super().__init__(filename, divider)

    def report(self, output):
        super().report(output)
        TempGAUGE.set(output)


class CPUFreqProbe(SysFSProbe):
    def __init__(self, filename, divider=1):
        super().__init__(filename, divider)

    def report(self, output):
        super().report(output)
        FreqGAUGE.set(output)
