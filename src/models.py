from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class VMState(Enum):
    RUNNING = "running"
    SHUTOFF = "shutoff"
    PAUSED = "paused"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class VMInfo:
    name: str
    state: VMState
    uuid: str
    memory: int
    vcpus: int
