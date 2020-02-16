import argparse
from pimon import pimon


def test_pimon():
    config = argparse.Namespace(interval=5, port=8080, sys='/host/sys', once=True, stub=True, debug=True,
                                freq_filename='freq', temp_filename='temp')
    if pimon(config) != 0:
        assert False
