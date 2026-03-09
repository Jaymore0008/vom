from dataclasses import dataclass, field
from typing import List, Optional

from .node import Node
from .service_group import ServiceGroup
from ..storage.diskgroup import DiskGroup
from ..storage.volume import Volume
from ..storage.filesystem import Filesystem
from ..monitoring.issue import Issue, IssueSeverity, IssueSource
from ..monitoring.health import HealthStatus


@dataclass
class Cluster:

    sid: str

    sp_node: Optional[str] = None
    sf_node: Optional[str] = None
    active_node: Optional[str] = None

    nodes: List[Node] = field(default_factory=list)

    diskgroups: List[DiskGroup] = field(default_factory=list)
    volumes: List[Volume] = field(default_factory=list)
    filesystems: List[Filesystem] = field(default_factory=list)
    service_groups: List[ServiceGroup] = field(default_factory=list)

    issues: List[Issue] = field(default_factory=list)

    def detect_issues(self):

        issues: List[Issue] = []

        for sg in self.service_groups:
            if sg.is_offline_everywhere():
                issues.append(
                    Issue(
                        message=f"Service Group {sg.name} is OFFLINE everywhere",
                        severity=IssueSeverity.CRITICAL,
                        source=IssueSource.SERVICE_GROUP
                    )
                )

        for fs in self.filesystems:

            if fs.is_critical():
                issues.append(
                    Issue(
                        message=f"Filesystem {fs.mount_point} > 90% full",
                        severity=IssueSeverity.CRITICAL,
                        source=IssueSource.FILESYSTEM
                    )
                )

            elif fs.is_warning():
                issues.append(
                    Issue(
                        message=f"Filesystem {fs.mount_point} > 75% full",
                        severity=IssueSeverity.WARNING,
                        source=IssueSource.FILESYSTEM
                    )
                )

        self.issues = issues

    def summary(self) -> dict:

        return {
            "sid": self.sid,
            "health": self.health.value,
            "node_count": len(self.nodes),
            "service_group_count": len(self.service_groups),
            "diskgroup_count": len(self.diskgroups),
            "filesystem_count": len(self.filesystems),
            "issue_count": len(self.issues)
        }

    def detect_active_node(self):

        node_sg_count = {node.name: 0 for node in self.nodes}

        for sg in self.service_groups:
            for node, state in sg.node_states.items():

                if state.value == "ONLINE":
                    node_sg_count[node] += 1

        if not node_sg_count:
            return

        active_node = max(node_sg_count, key=lambda node: node_sg_count[node])

        for node in self.nodes:
            node.is_active = node.name == active_node

    @property
    def health(self) -> HealthStatus:

        if any(issue.severity == IssueSeverity.CRITICAL for issue in self.issues):
            return HealthStatus.CRITICAL

        if any(issue.severity == IssueSeverity.WARNING for issue in self.issues):
            return HealthStatus.WARNING

        return HealthStatus.HEALTHY