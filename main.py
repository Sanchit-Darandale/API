from fastapi import FastAPI, Path
from fastapi.responses import FileResponse, JSONResponse
from yt_dlp import YoutubeDL
import os
import uuid

app = FastAPI()

COOKIES_PATH = os.path.join(os.path.dirname(__file__), "cookies.txt")
TMP_DIR = "/tmp"

@app.get("/audio/{video_url:path}")
async def download_audio(video_url: str):
    file_id = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(TMP_DIR, file_id)

    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": output_path,
        "cookiefile": COOKIES_PATH,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return FileResponse(output_path, media_type="audio/mpeg", filename="audio.mp3")
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.get("/video/{video_url:path}")
async def download_video(video_url: str):
    file_id = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(TMP_DIR, file_id)

    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": output_path,
        "cookiefile": COOKIES_PATH,
        "quiet": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return FileResponse(output_path, media_type="video/mp4", filename="video.mp4")
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
