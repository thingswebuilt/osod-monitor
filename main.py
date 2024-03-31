import sys

import click
from loguru import logger
from pySerialTransfer.pySerialTransfer import InvalidSerialPort

from osod_monitor.monitor import Monitor

logger.remove(0)
logger.add(sys.stdout, format="{time} {level} {message}", enqueue=True)
logger.add("payload.log", format="{time} {level} {message}", enqueue=True)


@click.command()
@click.option("--port", default="COM3", help="The serial port to connect to.")
def run(port: str):
    while True:
        try:
            monitor = Monitor(port=port)
            monitor.start()
            break  # If Monitor() call succeeds, break the loop
        except InvalidSerialPort as e:
            logger.error(f"Failed to start Monitor: {e}")
            continue  # If Monitor() call fails, continue the loop
    try:
        while True:
            if not monitor.output_queue.empty():
                data = monitor.output_queue.get()
                logger.info(data)
    except KeyboardInterrupt:
        monitor.close()


if __name__ == "__main__":
    run()
