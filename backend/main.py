from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.analyze import router as analyze_router
from api.download import router as download_router

app = FastAPI(title="Clip Cutter Local API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://[a-p]{32}",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(analyze_router, prefix="/api")
app.include_router(download_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}