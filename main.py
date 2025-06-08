from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import unquote
import requests
import yt_dlp

app = FastAPI(title="YouTube Downloader API")

def extract_download_url(video_url: str, format_code: str) -> str:
    ydl_opts = {
        'quiet': True,
        'format': format_code,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        if 'url' in info:
            return info['url']
        elif 'requested_formats' in info:
            return info['requested_formats'][0]['url']
        raise Exception("Download URL could not be extracted.")

def stream_file(url: str, filename: str, media_type: str):
    r = requests.get(url, stream=True)
    return StreamingResponse(
        r.iter_content(chunk_size=8192),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@app.get("/video/{quality}/{video_url:path}")
def download_video(quality: int, video_url: str):
    video_url = unquote(video_url)
    format_map = {
        480: "bestvideo[height<=480]+bestaudio[ext=m4a]/best[height<=480]",
        720: "bestvideo[height<=720]+bestaudio[ext=m4a]/best[height<=720]",
        1080: "bestvideo[height<=1080]+bestaudio[ext=m4a]/best[height<=1080]",
    }
    if quality not in format_map:
        raise HTTPException(status_code=400, detail="Unsupported video quality")
    try:
        download_url = extract_download_url(video_url, format_map[quality])
        return stream_file(download_url, f"video_{quality}p.mp4", "video/mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{video_url:path}")
def download_audio(video_url: str):
    video_url = unquote(video_url)
    try:
        download_url = extract_download_url(video_url, "bestaudio[ext=m4a]/bestaudio")
        return stream_file(download_url, "audio.m4a", "audio/m4a")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
