from pimetrics.probe import Probe
from prometheus_client import Gauge

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    # Use a stub instead
    import src.GPIOstub as GPIO


GAUGE = Gauge('pimon_fan', 'Status of RPi fan')


class GPIOProbe(Probe):
    def __init__(self, pin):
        super().__init__()
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def report(self, output):
        GAUGE.set(output)

    def measure(self):
        return GPIO.input(self.pin)
