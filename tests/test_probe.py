import os
from metrics.probe import Probe, FileProbe, ProcessProbe


class UnittestProbe(Probe):
    def __init__(self, testdata):
        super().__init__()
        self.testdata = testdata
        self.index = -1

    def measure(self):
        self.index += 1
        if self.index == len(self.testdata): self.index = 0
        return self.testdata[self.index]


class UnittestProcessProbe(ProcessProbe):
    def __init__(self, command):
        super().__init__(command)

    def process(self, lines):
        val = 0
        for line in lines:
            val += int(line)
        return val


def test_simple():
    testdata = [1, 2, 3, 4]
    probe = UnittestProbe(testdata)
    for val in testdata:
        assert probe.measure() == val


def test_file():
    # create the file
    open('testfile.txt', 'w')
    probe = FileProbe('testfile.txt')
    for val in range(1, 10):
        with open('testfile.txt', 'w') as f:
            f.write(f'{val}')
        assert probe.measure() == val
    os.remove('testfile.txt')


def test_bad_file():
    bad_file = False
    try:
        FileProbe('testfile.txt')
    except FileNotFoundError:
        bad_file = True
    assert bad_file


def test_process():
    metric = UnittestProcessProbe('/bin/sh -c ./process_ut.sh')
    out = 0
    while metric.running():
        out += metric.measure()
    assert out == 55


def test_bad_process():
    bad_file = False
    try:
        UnittestProcessProbe('missing_process_ut.sh')
    except FileNotFoundError:
        bad_file = True
    assert bad_file
