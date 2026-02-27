# vom/domain/cluster.py

from dataclasses import dataclass, field
from typing import List

from .node import Node
from .diskgroup import DiskGroup
from .volume import Volume
from .filesystem import Filesystem
from .service_group import ServiceGroup
from .issue import Issue
from .health import HealthStatus


@dataclass
class Cluster:

    sid: str

    # Explicit HA tracking
    sp_node: str = None
    sf_node: str = None
    active_node: str = None

    nodes: List[Node] = field(default_factory=list)

    diskgroups: List[DiskGroup] = field(default_factory=list)
    volumes: List[Volume] = field(default_factory=list)
    filesystems: List[Filesystem] = field(default_factory=list)
    service_groups: List[ServiceGroup] = field(default_factory=list)

    issues: List[Issue] = field(default_factory=list)

    def detect_issues(self):

        self.issues.clear()

        # Service group issues
        for sg in self.service_groups:
            if sg.is_offline_everywhere():
                self.issues.append(
                    Issue(
                        message=f"Service Group {sg.name} is OFFLINE everywhere",
                        severity="CRITICAL",
                        source="SERVICE_GROUP"
                    )
                )

        # Filesystem issues
        for fs in self.filesystems:
            if fs.is_critical():
                self.issues.append(
                    Issue(
                        message=f"Filesystem {fs.mount_point} > 90% full",
                        severity="CRITICAL",
                        source="FILESYSTEM"
                    )
                )
            elif fs.is_warning():
                self.issues.append(
                    Issue(
                        message=f"Filesystem {fs.mount_point} > 75% full",
                        severity="WARNING",
                        source="FILESYSTEM"
                    )
                )

    def health(self):

        if any(issue.severity == "CRITICAL" for issue in self.issues):
            return HealthStatus.CRITICAL

        if any(issue.severity == "WARNING" for issue in self.issues):
            return HealthStatus.WARNING

        return HealthStatus.HEALTHY

    def summary(self):

        return {
            "sid": self.sid,
            "sp_node": self.sp_node,
            "sf_node": self.sf_node,
            "active_node": self.active_node,
            "node_count": len(self.nodes),
            "diskgroup_count": len(self.diskgroups),
            "volume_count": len(self.volumes),
            "filesystem_count": len(self.filesystems),
            "service_group_count": len(self.service_groups),
            "issues": len(self.issues),
            "health": self.health().value
        }
