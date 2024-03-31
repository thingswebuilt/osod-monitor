import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum


class PayloadType(IntEnum):
    INCOMING_SERIAL_DATA = 1
    REQUESTED_STATE = 2
    ESTIMATED_STATE = 3


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


PAYLOADS = {
    PayloadType.INCOMING_SERIAL_DATA: IncomingSerialData,
    PayloadType.REQUESTED_STATE: RequestedState,
    PayloadType.ESTIMATED_STATE: EstimatedState,
}
