from metrics.probe import Probe


class SimpleProbe(Probe):
    def __init__(self, test_sequence):
        super().__init__()
        self.test_sequence = test_sequence
        self.index = 0

    def measure(self):
        output = self.test_sequence[self.index]
        self.index = (self.index+1) % len(self.test_sequence)
        return output

