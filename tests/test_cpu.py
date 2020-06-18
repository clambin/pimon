import pytest
from src.cpu import *


def test_cpufreq_probe():
    freq = CPUFreqProbe('./freq')
    freq.run()
    assert freq.measured() == 1500000
    temp = CPUTempProbe('./temp')
    temp.run()
    assert temp.measured() == 41.381


def test_cpufreq_badfile():
    with pytest.raises(FileNotFoundError):
        CPUFreqProbe('./nosuchfile')
    with pytest.raises(FileNotFoundError):
        CPUTempProbe('./nosuchfile')
