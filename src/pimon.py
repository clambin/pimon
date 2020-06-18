import logging
from prometheus_client import start_http_server
from src.version import version
from src.configuration import print_configuration
from src.cpu import CPUTempProbe, CPUFreqProbe
from src.gpio import GPIOProbe
from pimetrics.scheduler import Scheduler


def initialise(config):
    scheduler = Scheduler()
    try:
        scheduler.register(CPUFreqProbe(config.freq_filename), 5)
        scheduler.register(CPUTempProbe(config.temp_filename), 5)
    except FileNotFoundError as err:
        logging.warning(f'Could not add CPU monitor(s): {err}')
    if config.fan:
        try:
            scheduler.register(GPIOProbe(config.fan_pin), 5)
        except RuntimeError:
            logging.warning('Could not add Fan monitor.  Possibly /dev/gpiomem isn\'t accessible?')
    return scheduler


def pimon(config):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if config.debug else logging.INFO)
    logging.info(f'Starting pimon v{version}')
    logging.info(f'Configuration: {print_configuration(config)}')

    start_http_server(config.port)

    scheduler = initialise(config)
    if config.once:
        scheduler.run(once=True)
    else:
        while True:
            scheduler.run(duration=config.interval)
    return 0
