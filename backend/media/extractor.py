import ipaddress
import socket
from urllib.parse import urlsplit

import yt_dlp
from fastapi import HTTPException


def validate_public_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Only HTTP and HTTPS media URLs are supported.")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as error:
        raise HTTPException(status_code=400, detail="The source hostname could not be resolved.") from error
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise HTTPException(status_code=400, detail="Local and private network sources are not supported.")


def extract_info(url: str) -> dict:
    validate_public_url(url)
    options = {"quiet": True, "no_warnings": True, "noplaylist": True, "socket_timeout": 20}
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=False)
    except Exception as error:
        raise HTTPException(status_code=422, detail=f"Could not read media information: {error}") from error
    if not info or not info.get("duration"):
        raise HTTPException(status_code=422, detail="The source did not provide a usable duration.")
    return info