import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum


class PayloadType(IntEnum):
    INCOMING_SERIAL_DATA = 1
    REQUESTED_STATE = 2
    ESTIMATED_STATE = 3
    CELL_STATUS = 4


class Payload(ABC):

    payload_type: PayloadType
    struct_format: str = ""
    struct_obj: struct.Struct

    def __init__(self, *args):
        self.struct_obj = struct.Struct(self.struct_format)

    @abstractmethod
    def __bytes__(self):
        pass

    @classmethod
    def from_bytes(cls, byte_data: bytes):
        args = struct.unpack(cls.struct_format, byte_data[: cls.struct_obj.size])
        return cls(*args)

    @abstractmethod
    def __repr__(self):
        pass

    @property
    def payload_size(self) -> int:
        return self.struct_obj.size


@dataclass
class IncomingSerialData(Payload):
    struct_format = "<?"
    struct_obj = struct.Struct(struct_format)

    available: bool

    def __bytes__(self):
        return self.struct_obj.pack(self.available)

    def __repr__(self):
        return f"IncomingSerialData(available={self.available})"


@dataclass
class RequestedState(Payload):
    struct_format = "<ff"
    struct_obj = struct.Struct(struct_format)

    velocity: float
    angular_velocity: float

    def __bytes__(self):
        return self.struct_obj.pack(self.velocity, self.angular_velocity)

    def __repr__(self):
        return (
            f"RequestedState("
            f"velocity={self.velocity}, "
            f"angular_velocity={self.angular_velocity})"
        )


@dataclass
class EstimatedState(Payload):
    struct_format = "<Ifffffff"
    struct_obj = struct.Struct(struct_format)

    timestamp: int
    x: float
    y: float
    heading: float

    tof_front: float
    tof_rear: float
    tof_left: float
    tof_right: float

    def __bytes__(self):
        return self.struct_obj.pack(
            self.timestamp,
            self.x,
            self.y,
            self.heading,
            self.tof_front,
            self.tof_rear,
            self.tof_left,
            self.tof_right,
        )

    def __repr__(self):
        return (
            f"EstimatedState("
            f"timestamp={self.timestamp}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"heading={self.heading}, "
            f"tof_front={self.tof_front}, "
            f"tof_rear={self.tof_rear}, "
            f"tof_left={self.tof_left}, "
            f"tof_right={self.tof_right})"
        )


@dataclass
class CellStatus(Payload):
    struct_format = "<ffff?????"
    struct_obj = struct.Struct(struct_format)

    cell_1_voltage: float
    cell_2_voltage: float
    cell_3_voltage: float
    psu_voltage: float
    all_ok: bool
    out_of_balance: bool
    low_cell_voltage: bool
    high_cell_voltage: bool
    psu_under_voltage: bool

    def __bytes__(self):
        return self.struct_obj.pack(
            self.cell_1_voltage,
            self.cell_2_voltage,
            self.cell_3_voltage,
            self.psu_voltage,
            self.all_ok,
            self.out_of_balance,
            self.low_cell_voltage,
            self.high_cell_voltage,
            self.psu_under_voltage,
        )

    def __repr__(self):
        return (
            f"CellStatus("
            f"cell_1_voltage={self.cell_1_voltage}, "
            f"cell_2_voltage={self.cell_2_voltage}, "
            f"cell_3_voltage={self.cell_3_voltage}, "
            f"psu_voltage={self.psu_voltage}, "
            f"all_ok={self.all_ok}, "
            f"out_of_balance={self.out_of_balance}, "
            f"low_cell_voltage={self.low_cell_voltage}, "
            f"high_cell_voltage={self.high_cell_voltage}, "
            f"psu_under_voltage={self.psu_under_voltage})"
        )


PAYLOADS = {
    PayloadType.INCOMING_SERIAL_DATA: IncomingSerialData,
    PayloadType.REQUESTED_STATE: RequestedState,
    PayloadType.ESTIMATED_STATE: EstimatedState,
    PayloadType.CELL_STATUS: CellStatus,
}
