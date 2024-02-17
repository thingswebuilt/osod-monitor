import sys

import click
from loguru import logger

from osod_monitor.monitor import Monitor

logger.remove(0)
logger.add(sys.stdout, format="{time} {level} {message}", enqueue=True)


@click.command()
@click.option("--port", default="COM3", help="The serial port to connect to.")
def run(port: str):
    monitor = Monitor(port=port)
    monitor.start()
    try:
        while True:
            if not monitor.output_queue.empty():
                data = monitor.output_queue.get()
                logger.info(data)
    except KeyboardInterrupt:
        monitor.close()


if __name__ == "__main__":
    run()
