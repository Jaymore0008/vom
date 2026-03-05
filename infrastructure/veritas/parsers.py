# vom/infrastructure/parsers.py

import logging
from typing import List

from domain.storage.diskgroup import DiskGroup, DiskGroupState
from domain.storage.volume import Volume, VolumeLayout
from domain.storage.filesystem import Filesystem
from domain.cluster.service_group import ServiceGroup, ServiceGroupState


class VeritasParser:

    # --------------------------------------------------
    # Diskgroups
    # --------------------------------------------------

    @staticmethod
    def parse_diskgroups(output: str) -> List[DiskGroup]:

        diskgroups: List[DiskGroup] = []

        for line in output.splitlines():

            line = line.strip()

            if not line or line.startswith("NAME"):
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            name = parts[0]

            try:
                state = DiskGroupState(parts[1])
            except ValueError:
                state = DiskGroupState.UNKNOWN

            diskgroups.append(
                DiskGroup(
                    name=name,
                    state=state
                )
            )

        return diskgroups

    # --------------------------------------------------
    # Volumes
    # --------------------------------------------------

    @staticmethod
    def parse_volumes(vxprint_output: str, df_output: str) -> List[Volume]:

        volumes = {}
        current_dg = None

        for line in vxprint_output.splitlines():

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            # Diskgroup line
            if parts[0] == "dg":
                current_dg = parts[1]

            # Volume line
            elif parts[0] == "v":

                name = parts[1]

                try:
                    size_blocks = int(parts[5])
                    size_gb = round(size_blocks * 512 / (1024 ** 3))
                except (ValueError, IndexError):
                    logging.warning(f"[Parser] Failed to parse size for volume {name}")
                    size_gb = 0

                volumes[name] = {
                    "diskgroup": current_dg,
                    "size_gb": size_gb,
                    "layout": VolumeLayout.CONCAT,
                    "mount_point": None,
                    "mounted": False
                }

            # Plex line determines layout
            elif parts[0] == "pl":

                if len(parts) < 7:
                    continue

                volname = parts[2]

                if volname not in volumes:
                    continue

                layout_raw = parts[6].lower()

                if "stripe" in layout_raw:
                    layout = VolumeLayout.STRIPE
                else:
                    layout = VolumeLayout.CONCAT

                volumes[volname]["layout"] = layout

        # Map mountpoints from df
        for line in df_output.splitlines():

            line = line.strip()

            if "/dev/vx/dsk/" not in line:
                continue

            parts = line.split()

            if len(parts) < 7:
                continue

            device = parts[0]
            mount = parts[-1]

            volume_name = device.split("/")[-1]

            if volume_name in volumes:

                volumes[volume_name]["mount_point"] = mount
                volumes[volume_name]["mounted"] = True

        # Convert to Volume objects
        result: List[Volume] = []

        for name, data in volumes.items():

            result.append(
                Volume(
                    name=name,
                    diskgroup=data["diskgroup"],
                    size_gb=data["size_gb"],
                    layout=data["layout"],
                    mount_point=data["mount_point"],
                    mounted=data["mounted"]
                )
            )

        return result

    # --------------------------------------------------
    # Filesystems
    # --------------------------------------------------

    @staticmethod
    def parse_filesystems(df_output: str) -> List[Filesystem]:

        filesystems: List[Filesystem] = []

        for line in df_output.splitlines():

            line = line.strip()

            if not line.startswith("/dev/vx/dsk/"):
                continue

            parts = line.split()

            if len(parts) < 7:
                continue

            device = parts[0]

            try:
                size_gb = round(int(parts[2]) / (1024 * 1024))
                used_gb = round(int(parts[3]) / (1024 * 1024))
                avail_gb = round(int(parts[4]) / (1024 * 1024))
                percent = int(parts[5].replace("%", ""))
            except (ValueError, IndexError):

                logging.warning(f"[Parser] Failed to parse filesystem line: {line}")

                size_gb = used_gb = avail_gb = percent = 0

            mount = parts[6]

            filesystems.append(
                Filesystem(
                    device=device,
                    mount_point=mount,
                    size_gb=size_gb,
                    used_gb=used_gb,
                    available_gb=avail_gb,
                    percent_used=percent
                )
            )

        return filesystems

    # --------------------------------------------------
    # Service Groups
    # --------------------------------------------------

    @staticmethod
    def parse_service_group_states(output: str) -> List[ServiceGroup]:

        groups = {}

        for line in output.splitlines():

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) < 4:
                continue

            group_name = parts[0]
            node = parts[2]
            state_raw = parts[3].replace("|", "")

            try:
                state = ServiceGroupState(state_raw)
            except ValueError:
                state = ServiceGroupState.UNKNOWN

            if group_name not in groups:
                groups[group_name] = ServiceGroup(name=group_name)

            groups[group_name].set_state(node, state)

        return list(groups.values())