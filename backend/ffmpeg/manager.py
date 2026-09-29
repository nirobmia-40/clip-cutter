import shutil

from fastapi import HTTPException


def require_ffmpeg() -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise HTTPException(status_code=503, detail="FFmpeg and FFprobe must be installed and available on PATH.")