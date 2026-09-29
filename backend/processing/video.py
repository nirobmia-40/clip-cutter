from processing.clipper import clip_options


def video_options(quality: str, output_format: str, start: float, end: float) -> dict:
    if quality == "best":
        format_selector = "bestvideo+bestaudio/best"
    else:
        format_selector = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
    return {
        "format": format_selector,
        "merge_output_format": output_format,
        "force_keyframes_at_cuts": True,
        **clip_options(start, end),
        "postprocessors": [{"key": "FFmpegVideoRemuxer", "preferedformat": output_format}],
    }