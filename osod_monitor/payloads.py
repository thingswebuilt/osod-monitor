import struct
from dataclasses import dataclass
from enum import IntEnum


class PayloadType(IntEnum):
    REQUESTED_STATE = 4


PAYLOAD_DEFINITIONS = {
    PayloadType.REQUESTED_STATE: struct.Struct("ff"),
}


@dataclass
class RequestedState:
    velocity: float
    angular_velocity: float

    def __bytes__(self):
        return PAYLOAD_DEFINITIONS[PayloadType.REQUESTED_STATE].pack(self.velocity, self.angular_velocity)

    @classmethod
    def from_bytes(cls, byte_data: bytes):
        return cls(*PAYLOAD_DEFINITIONS[PayloadType.REQUESTED_STATE].unpack(byte_data))

    def __repr__(self):
        return f"RequestedState(velocity={self.velocity}, angular_velocity={self.angular_velocity})"
