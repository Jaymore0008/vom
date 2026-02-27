# vom/infrastructure/veritas_commands.py

"""
Veritas CLI command definitions.

This module contains ONLY command strings.
It does NOT execute commands.
Execution is handled by veritas_client.py
"""


class VeritasCommands:

    # --------------------------------------------------
    # Diskgroup commands
    # --------------------------------------------------

    VXDG_LIST = "/usr/sbin/vxdg list"

    VXDG_LIST_BRIEF = "/usr/sbin/vxdg list | awk '{print $1, $2}'"

    # --------------------------------------------------
    # Volume commands
    # --------------------------------------------------

    VXPRINT = "/usr/sbin/vxprint -ht"

    VXPRINT_BRIEF = "/usr/sbin/vxprint -ht | egrep '^dg|^v|^pl'"

    # --------------------------------------------------
    # Filesystem commands
    # --------------------------------------------------

    DF = "df -P -T"

    MOUNT = "mount"

    # --------------------------------------------------
    # Service group commands
    # --------------------------------------------------

    HASTATUS_SUM = "hastatus -sum"

    HAGRP_STATE = "/opt/VRTS/bin/hagrp -state"

    HAGRP_LIST = "hagrp -list"

    # --------------------------------------------------
    # Resource commands
    # --------------------------------------------------

    HARES_STATE = "hares -state"

    HARES_LIST = "hares -list"

    # --------------------------------------------------
    # Node state commands
    # --------------------------------------------------

    HASYS_STATE = "hasys -state"

    # --------------------------------------------------
    # Cluster health commands
    # --------------------------------------------------

    HASTATUS = "hastatus"

    # --------------------------------------------------
    # Utility commands
    # --------------------------------------------------

    HOSTNAME = "hostname"

    UPTIME = "uptime"

    DATE = "date"
