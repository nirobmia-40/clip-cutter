from processing.clipper import clip_options


def audio_options(bitrate: str, start: float, end: float) -> dict:
    return {
        "format": "bestaudio/best",
        **clip_options(start, end),
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": bitrate}
        ],
    }