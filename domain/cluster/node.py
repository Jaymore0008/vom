from dataclasses import dataclass
from enum import Enum


class NodeRole(Enum):
    SP = "SP"
    SF = "SF"


class NodeState(Enum):
    RUNNING = "RUNNING"
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Node:

    name: str
    ip: str
    role: NodeRole

    state: NodeState = NodeState.UNKNOWN
    is_active: bool = False

    service_group_count: int = 0
    resource_count: int = 0

    def is_running(self) -> bool:
        return self.state == NodeState.RUNNING

    def is_online(self) -> bool:
        return self.state in {NodeState.RUNNING, NodeState.ONLINE}