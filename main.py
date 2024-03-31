import sys

import click
from loguru import logger
from pySerialTransfer.pySerialTransfer import InvalidSerialPort

from osod_monitor.monitor import Monitor
from osod_monitor.payloads import (
    PayloadType,
    IncomingSerialData,
    RequestedState,
    EstimatedState,
    Payload,
    PAYLOADS,
)

logger.remove(0)
logger.add(sys.stdout, format="{time} {level} {message}", enqueue=True)
logger.add("payload.log", format="{time} {level} {message}", enqueue=True)
logger.add(
    "monitor.log",
    format="{time} {level} {message}",
    enqueue=True,
    filter="osod_monitor.monitor",
)


def process_payload(payload_bytes: bytes) -> Payload | None:
    payload_type, payload_data = payload_bytes[0], payload_bytes[1:]

    if payload_cls := PAYLOADS.get(payload_type, None):
        return payload_cls.from_bytes(payload_data)

    return None


@click.command()
@click.option("--port", default="COM3", help="The serial port to connect to.")
def run(port: str):
    while True:
        try:
            monitor = Monitor(port=port, payload_processor=process_payload, baud=115200)
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
