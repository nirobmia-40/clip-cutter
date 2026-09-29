import shutil
import tempfile
from pathlib import Path


def create_temp_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix="clip-cutter-"))


def remove_temp_dir(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)