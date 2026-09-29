from yt_dlp.utils import download_range_func


def clip_options(start: float, end: float) -> dict:
    return {"download_ranges": download_range_func(None, [(start, end)])}