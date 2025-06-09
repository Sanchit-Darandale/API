from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import uuid
import os

app = FastAPI()


@app.get("/audio/")
async def download_audio(url: str = Query(..., alias="url")):
    try:
        uid = str(uuid.uuid4())
        filename = f"{uid}.mp3"
        output_path = f"/tmp/{filename}"

        cmd = [
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--cookies", "cookies.txt",
            "-o", output_path,
            url
        ]

        subprocess.run(cmd, check=True)
        if os.path.exists(output_path):
            return FileResponse(output_path, filename=filename, media_type="audio/mpeg")
        else:
            return JSONResponse(status_code=500, content={"detail": "Download failed"})

    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/video/")
async def download_video(url: str = Query(..., alias="url"), quality: str = "720"):
    try:
        uid = str(uuid.uuid4())
        filename = f"{uid}.mp4"
        output_path = f"/tmp/{filename}"

        format_map = {
            "360": "18",    # mp4 360p
            "480": "135+140",  # video+audio
            "720": "22",    # mp4 720p
            "1080": "137+140"  # bestvideo+bestaudio
        }

        yt_format = format_map.get(quality, "22")

        cmd = [
            "yt-dlp",
            "-f", yt_format,
            "--merge-output-format", "mp4",
            "--cookies", "cookies.txt",
            "-o", output_path,
            url
        ]

        subprocess.run(cmd, check=True)
        if os.path.exists(output_path):
            return FileResponse(output_path, filename=filename, media_type="video/mp4")
        else:
            return JSONResponse(status_code=500, content={"detail": "Download failed"})

    except subprocess.CalledProcessError as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
