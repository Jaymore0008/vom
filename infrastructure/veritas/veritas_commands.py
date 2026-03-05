# vom/infrastructure/veritas_commands.py

from enum import Enum


class VeritasCommands(Enum):

    # Diskgroups
    VXDG_LIST = "/usr/sbin/vxdg list"

    # Volumes
    VXPRINT = "/usr/sbin/vxprint -ht"

    # Filesystems
    DF = "df -P -T"
    MOUNT = "mount"

    # Service groups
    HASTATUS_SUM = "hastatus -sum"
    HAGRP_STATE = "/opt/VRTS/bin/hagrp -state"
    HAGRP_LIST = "hagrp -list"

    # Resources
    HARES_STATE = "hares -state"
    HARES_LIST = "hares -list"

    # Nodes
    HASYS_STATE = "hasys -state"

    # Cluster health
    HASTATUS = "hastatus"

    # Utilities
    HOSTNAME = "hostname"
    UPTIME = "uptime"
    DATE = "date"