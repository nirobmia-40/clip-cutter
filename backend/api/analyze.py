from fastapi import APIRouter

from api.models import AnalyzeRequest
from media.extractor import extract_info
from media.formats import available_qualities
from media.metadata import describe_media

router = APIRouter()


@router.post("/analyze")
def analyze_media(request: AnalyzeRequest) -> dict:
    info = extract_info(str(request.url))
    return {**describe_media(info), "qualities": available_qualities(info)}