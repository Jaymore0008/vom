# vom/infrastructure/mock_data.py

import logging
from pathlib import Path

from ..veritas.veritas_commands import VeritasCommands


MOCK_DIR = Path(__file__).parent / "mock_samples"


def load_mock_file(filename: str) -> str:

    path = MOCK_DIR / filename

    if not path.exists():
        logging.warning(f"[MockData] Missing mock file: {filename}")
        return ""

    return path.read_text()


MOCK_RESPONSES = {

    VeritasCommands.VXDG_LIST.value: load_mock_file("vxdg_list.txt"),

    VeritasCommands.HASYS_STATE.value: load_mock_file("hasys_state.txt"),

    VeritasCommands.HAGRP_STATE.value: load_mock_file("hagrp_state.txt"),

    VeritasCommands.VXPRINT.value: load_mock_file("vxprint.txt"),

    VeritasCommands.DF.value: load_mock_file("df.txt"),
}