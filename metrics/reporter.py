# Copyright 2020 by Christophe Lambin
# All rights reserved.

from prometheus_client import start_http_server, Gauge


class Reporter:
    def __init__(self):
        self.probes = {}

    def start(self):
        pass

    def add(self, probe, name, description, label=None, key=None):
        # No duplicates allowed
        for p in self.probes.values():
            if p['name'] == name and p['label'] == label and p['key'] == key:
                raise KeyError("Probe already exists")
        self.probes[probe] = {'name': name, 'description': description, 'label': label, 'key': key}

    def get_probe_info(self, probe):
        info = self.probes[probe]
        return info['name'], info['label'], info['key']

    def report(self, probe, value):
        pass

    def pre_run(self):
        pass

    def post_run(self):
        pass

    def run(self):
        self.pre_run()
        for probe in self.probes:
            self.report(probe, probe.measured())
        self.post_run()


class PrometheusReporter(Reporter):
    def __init__(self, portno=8080):
        super().__init__()
        self.portno = portno
        self.gauges = {}

    def start(self):
        start_http_server(self.portno)

    def find_gauge(self, name, label):
        keyname = f'{name}|{label}' if label else name
        if keyname in self.gauges:
            return self.gauges[keyname]
        return None

    def make_gauge(self, name, description, label):
        if not self.find_gauge(name, label):
            if not label:
                self.gauges[name] = Gauge(name, description)
            else:
                keyname = f'{name}|{label}'
                self.gauges[keyname] = Gauge(name, description, [label])

    def add(self, m, name, description, label=None, key=None):
        super().add(m, name, description, label, key)
        self.make_gauge(name, description, label)

    def report(self, probe, val):
        name, label, key = self.get_probe_info(probe)
        g = self.find_gauge(name, label)
        if label is not None:
            g = g.labels(key)
        g.set(val)

