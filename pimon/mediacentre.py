from abc import ABC
from prometheus_client import Summary
from metrics.probe import APIProbe

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request', ['server', 'endpoint'])


class MediaCentreProbe(APIProbe, ABC):
    def __init__(self, url, endpoint, headers):
        super().__init__(f'{url}{endpoint}', headers=headers)
        self.endpoint = endpoint

    def process(self, response):
        return len(response) if response is not None else 0


class CalendarProbe(MediaCentreProbe):
    def __init__(self, url, api_key):
        super().__init__(url, 'calendar', headers={'X-Api-Key': api_key})


class QueueProbe(MediaCentreProbe):
    def __init__(self, url, api_key):
        super().__init__(url, 'queue', headers={'X-Api-Key': api_key})


class LibraryProbe(MediaCentreProbe):
    def __init__(self, url, endpoint, api_key):
        super().__init__(url, endpoint, headers={'X-Api-Key': api_key})


class SonarrSeriesProbe(LibraryProbe):
    def __init__(self, url, api_key):
        super().__init__(url, 'movie', api_key)


class RadarrSeriesProbe(LibraryProbe):
    def __init(self, url, api_key):
        super().__init__(url, 'series', api_key)


class PlexLibraryProbe(LibraryProbe, ABC):
    def __next__(self, url, directory_type, api_key):
        super().__init__(url, 'library/sections', api_key)
        self.directory_type = directory_type

    def measure_children(self):
        """"To be implemented by children"""

    def process(self, response):
        count = 0
        for directory in response['MediaContainer']['Directory']:
            directory_key = directory["key"]
            directory_type = directory["type"]
            if directory_type == self.directory_type:
                count += self.measure_children()
        return count


class PlexSeriesProbe(PlexLibraryProbe):
    def __init__(self, url, api_key):
        super().__init__(url, 'show', api_key)

    def measure_children(self):
        probe = LibraryProbe(self.url,  )


class PlexMoviesProbe(PlexLibraryProbe):
    def __init__(self, url, api_key):
        pass
