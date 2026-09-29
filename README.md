# Clip Cutter

A Chrome extension popup backed by a local FastAPI service. It analyzes a media URL, lets you select a time range and output settings, and prepares an MP4, MOV, or MP3 clip on your machine.

Use this only with media you own or are authorized to download. This project does not provide DRM circumvention.

## Requirements

- Python 3.10 or newer
- FFmpeg and FFprobe available on `PATH`
- Google Chrome

## Run the backend

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8765
```

The API listens only on loopback. Keep it running while using the extension.

## Load the extension

1. Open `chrome://extensions` and enable Developer mode.
2. Choose **Load unpacked** and select the `extension` directory.
3. Open the extension, paste a supported media URL, and choose **Analyze**.

The local service must be running before Analyze will work. FFmpeg is required for clip cutting and format conversion.