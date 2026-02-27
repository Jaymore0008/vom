from dataclasses import dataclass, field


@dataclass
class Resource:

    name: str

    service_group: str

    node_states: dict = field(default_factory=dict)

    def set_state(self, node: str, state: str):

        self.node_states[node] = state

    def health(self):

        if any(state == "FAULTED" for state in self.node_states.values()):
            return "CRITICAL"

        return "HEALTHY"
