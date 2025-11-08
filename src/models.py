from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class VMState(Enum):
    """Virtual machine state enumeration."""

    RUNNING = "running"
    SHUTOFF = "shutoff"
    PAUSED = "paused"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class VMInfo:
    """Immutable virtual machine information container."""

    name: str
    state: VMState
    uuid: str
    memory: int  # In MB
    vcpus: int
