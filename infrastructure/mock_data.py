# vom/infrastructure/mock_data.py

from pathlib import Path


MOCK_DIR = Path(__file__).parent / "mock_samples"


def load_mock_file(filename: str) -> str:
    path = MOCK_DIR / filename
    if path.exists():
        return path.read_text()
    return ""


MOCK_RESPONSES = {

    "hagrp -state": load_mock_file("hagrp_state.txt"),
    "/usr/sbin/vxprint -ht": load_mock_file("vxprint.txt"),
    "df -P -T": load_mock_file("df.txt"),
}