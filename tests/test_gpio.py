import pytest
from libpimon.gpio import GPIOProbe


def test_gpio():
    probe = GPIOProbe(18)
    probe.run()
    assert probe.measured() == 0


def test_bad_pin():
    with pytest.raises(RuntimeError):
        probe = GPIOProbe(-1)