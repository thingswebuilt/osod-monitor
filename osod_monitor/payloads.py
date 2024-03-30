import struct
from dataclasses import dataclass
from enum import IntEnum


class PayloadType(IntEnum):
    REQUESTED_STATE = 4
    ESTIMATED_STATE = 6


PAYLOAD_DEFINITIONS = {
    PayloadType.REQUESTED_STATE: struct.Struct("<ff"),
    PayloadType.ESTIMATED_STATE: struct.Struct("<Ifffffff"),
}


@dataclass
class RequestedState:
    velocity: float
    angular_velocity: float

    def __bytes__(self):
        return PAYLOAD_DEFINITIONS[PayloadType.REQUESTED_STATE].pack(
            self.velocity, self.angular_velocity
        )

    @classmethod
    def from_bytes(cls, byte_data: bytes):
        return cls(*PAYLOAD_DEFINITIONS[PayloadType.REQUESTED_STATE].unpack(byte_data))

    def __repr__(self):
        return f"RequestedState(velocity={self.velocity}, angular_velocity={self.angular_velocity})"


@dataclass
class EstimatedState:
    timestamp: int
    x: float
    y: float
    heading: float

    tof_front: float
    tof_rear: float
    tof_left: float
    tof_right: float

    def __bytes__(self):
        return PAYLOAD_DEFINITIONS[PayloadType.ESTIMATED_STATE].pack(
            self.timestamp,
            self.x,
            self.y,
            self.heading,
            self.tof_front,
            self.tof_rear,
            self.tof_left,
            self.tof_right,
        )

    @classmethod
    def from_bytes(cls, byte_data: bytes):
        return cls(*PAYLOAD_DEFINITIONS[PayloadType.ESTIMATED_STATE].unpack(byte_data))

    def __repr__(self):
        return (
            f"EstimatedState(timestamp={self.timestamp}, x={self.x}, y={self.y}, heading={self.heading}, "
            f"tof_front={self.tof_front}, tof_rear={self.tof_rear}, tof_left={self.tof_left}, tof_right={self.tof_right})"
        )
