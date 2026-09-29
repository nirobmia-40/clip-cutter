from fastapi import HTTPException


def describe_media(info: dict) -> dict:
    duration = info.get("duration")
    if not duration:
        raise HTTPException(status_code=422, detail="The source did not provide a usable duration.")
    return {"title": info.get("title", "Media"), "duration": duration}