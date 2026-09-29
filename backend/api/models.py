from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, model_validator


class AnalyzeRequest(BaseModel):
    url: HttpUrl


class DownloadRequest(BaseModel):
    url: HttpUrl
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    mode: Literal["video", "audio"]
    quality: str = "best"
    format: Literal["mp4", "mov", "mp3"]

    @model_validator(mode="after")
    def validate_options(self) -> "DownloadRequest":
        if self.end <= self.start:
            raise ValueError("End time must be after start time.")
        if self.mode == "video" and self.format not in {"mp4", "mov"}:
            raise ValueError("Video output must be MP4 or MOV.")
        if self.mode == "audio" and self.format != "mp3":
            raise ValueError("Audio output must be MP3.")
        if self.mode == "video" and self.quality != "best":
            try:
                height = int(self.quality)
            except ValueError as error:
                raise ValueError("Video quality must be a resolution or best.") from error
            if not 1 <= height <= 4320:
                raise ValueError("Unsupported video resolution.")
        if self.mode == "audio" and self.quality not in {"128", "192", "256", "320"}:
            raise ValueError("Audio bitrate must be 128, 192, 256, or 320 kbps.")
        return self