from dataclasses import dataclass, field


@dataclass
class Node:

    name: str
    ip: str
    role: str   # SP or SF

    state: str = "UNKNOWN"

    is_active: bool = False

    service_group_count: int = 0

    resource_count: int = 0

    def is_running(self):

        return self.state.upper() == "RUNNING"

    def is_online(self):

        return self.state.upper() in ["RUNNING", "ONLINE"]

    def to_dict(self):

        return {
            "name": self.name,
            "ip": self.ip,
            "role": self.role,
            "state": self.state,
            "is_active": self.is_active,
            "service_group_count": self.service_group_count,
            "resource_count": self.resource_count
        }
