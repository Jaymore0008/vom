# vom/infrastructure/parsers.py

import re


class VeritasParser:

    @staticmethod
    def parse_diskgroups(output):
        diskgroups = []
        lines = output.splitlines()

        for line in lines:
            if line.startswith("NAME") or not line.strip():
                continue

            parts = line.split()

            if len(parts) >= 2:
                diskgroups.append({
                    "name": parts[0],
                    "state": parts[1]
                })

        return diskgroups

    @staticmethod
    def parse_volumes(vxprint_output, df_output):

        volumes = {}
        current_dg = None

        for line in vxprint_output.splitlines():

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            # Detect diskgroup
            if parts[0] == "dg":
                current_dg = parts[1]

            # Detect volume
            elif parts[0] == "v":

                name = parts[1]

                try:
                    size_blocks = int(parts[5])
                    size_gb = round(size_blocks * 512 / (1024 ** 3))
                except:
                    size_gb = 0

                volumes[name] = {
                    "volume": name,
                    "diskgroup": current_dg,
                    "size_gb": size_gb,
                    "layout": "UNKNOWN",
                    "mount": None,
                    "status": "Not Mounted"
                }

            # Detect layout from plex line
            elif parts[0] == "pl":

                volname = parts[2]

                if volname in volumes and len(parts) >= 7:
                    volumes[volname]["layout"] = parts[6]

        # Map mountpoints from df output
        for line in df_output.splitlines():

            line = line.strip()

            if "/dev/vx/dsk/" not in line:
                continue

            parts = line.split()

            device = parts[0]
            mount = parts[-1]

            volume = device.split("/")[-1]

            if volume in volumes:
                volumes[volume]["mount"] = mount
                volumes[volume]["status"] = "Mounted"

        return list(volumes.values())

    @staticmethod
    def parse_filesystems(df_output):

        filesystems = []

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
            except:
                size_gb = used_gb = avail_gb = 0

            percent = int(parts[5].replace("%", ""))
            mount = parts[6]

            filesystems.append({
                "device": device,
                "mount_point": mount,
                "size_gb": size_gb,
                "used_gb": used_gb,
                "available_gb": avail_gb,
                "percent_used": percent
            })

        return filesystems

    @staticmethod
    def parse_service_group_states(output):

        service_groups = []

        for line in output.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) < 4:
                continue

            group = parts[0]
            system = parts[2]
            state = parts[3].replace("|", "")

            service_groups.append({
                "service_group": group,
                "node": system,
                "state": state
            })

        return service_groups
