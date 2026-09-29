from pathlib import Path

import yt_dlp
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from api.models import DownloadRequest
from ffmpeg.manager import require_ffmpeg
from media.extractor import extract_info
from processing.audio import audio_options
from processing.video import video_options
from storage.manager import create_temp_dir, remove_temp_dir

router = APIRouter()


def download_clip(request: DownloadRequest, folder: Path) -> Path:
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "outtmpl": str(folder / "clip.%(ext)s"),
        "socket_timeout": 20,
    }
    if request.mode == "video":
        options.update(video_options(request.quality, request.format, request.start, request.end))
    else:
        options.update(audio_options(request.quality, request.start, request.end))
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.extract_info(str(request.url), download=True)
    except Exception as error:
        raise HTTPException(status_code=422, detail=f"Could not prepare this clip: {error}") from error
    expected = folder / f"clip.{request.format}"
    if expected.is_file():
        return expected
    files = [item for item in folder.iterdir() if item.is_file() and not item.name.endswith((".part", ".ytdl"))]
    if len(files) == 1:
        return files[0]
    raise HTTPException(status_code=500, detail="Processing finished without producing an output file.")


@router.post("/download")
async def download_media(request: DownloadRequest, background_tasks: BackgroundTasks) -> FileResponse:
    require_ffmpeg()
    info = extract_info(str(request.url))
    if request.end > info["duration"]:
        raise HTTPException(status_code=422, detail="End time exceeds the media duration.")
    folder = create_temp_dir()
    try:
        output = await run_in_threadpool(download_clip, request, folder)
    except Exception:
        remove_temp_dir(folder)
        raise
    background_tasks.add_task(remove_temp_dir, folder)
    return FileResponse(
        output,
        media_type="application/octet-stream",
        filename=f"clip.{request.format}",
        background=background_tasks,
    )