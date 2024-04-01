import ast
import dataclasses
import sys

import click
from loguru import logger
from pySerialTransfer.pySerialTransfer import InvalidSerialPort

from osod_monitor.monitor import Monitor
from osod_monitor.payloads import (
    Payload,
    PAYLOADS,
)

logger.remove(0)
logger.add(sys.stdout, format="{time} {level} {message}", enqueue=True)
logger.add("payload.log", format="{time} {level} {message}", enqueue=True)
logger.add(
    "monitor.log",
    format="{message}",
    enqueue=True,
    filter="osod_monitor.monitor",
)


def title_to_snake_case(title_case_str):
    snake_case_str = "".join(
        "_" + i.lower() if i.isupper() else i for i in title_case_str
    )
    return snake_case_str.lstrip("_")


def csv_logger(record):
    message_dict = ast.literal_eval(record["message"])
    try:
        data_values = ",".join(str(val) for val in message_dict.values())
        return f"{data_values}\n"
    except TypeError:
        pass


def match_logger(record, payload_name: str):
    return record["extra"].get("payload_type") == payload_name


# there's almost certainly a better way to do this
logger.add(
    "cell_status.log",
    format=csv_logger,
    filter=lambda record: match_logger(record, "CellStatus"),
    enqueue=True,
)
logger.add(
    "incoming_serial_data.log",
    format=csv_logger,
    filter=lambda record: match_logger(record, "IncomingSerialData"),
    enqueue=True,
)
logger.add(
    "estimated_state.log",
    format=csv_logger,
    filter=lambda record: match_logger(record, "EstimatedState"),
    enqueue=True,
)
logger.add(
    "requested_state.log",
    format=csv_logger,
    filter=lambda record: match_logger(record, "RequestedState"),
    enqueue=True,
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
                with logger.contextualize(payload_type=data.__class__.__name__):
                    logger.info(dataclasses.asdict(data))
    except KeyboardInterrupt:
        monitor.close()


if __name__ == "__main__":
    run()
