import os
import shutil
import uuid
import re
import subprocess
from pathlib import Path
from typing import Tuple, Optional

from fastapi import UploadFile, HTTPException, status
from PIL import Image
import imageio_ffmpeg as iioffmpeg
import ffmpeg

from .config import settings


def ensure_dirs():
    settings.media_root.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.thumb_dir.mkdir(parents=True, exist_ok=True)


def _read_to_temp_and_validate(file: UploadFile, allowed_mimes: set[str], max_bytes: int) -> Path:
    ct = file.content_type or ""
    if ct not in allowed_mimes and ct != "application/octet-stream":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported media type")
    ensure_dirs()
    temp_path = settings.upload_dir / f"tmp_{uuid.uuid4().hex}"
    total = 0
    with temp_path.open("wb") as out:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                file.file.close()
                try:
                    temp_path.unlink(missing_ok=True)
                except Exception:
                    pass
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")
            out.write(chunk)
    file.file.seek(0)
    return temp_path


def _save_final(temp_path: Path, suffix: str) -> Path:
    final_name = f"{uuid.uuid4().hex}{suffix}"
    final_path = settings.upload_dir / final_name
    shutil.move(str(temp_path), str(final_path))
    return final_path


def _make_image_thumb(src_path: Path) -> Path:
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        w, h = im.size
        if w > settings.thumb_max_width:
            new_h = int(h * settings.thumb_max_width / w)
            im = im.resize((settings.thumb_max_width, new_h))
        out_path = settings.thumb_dir / f"{src_path.stem}.jpg"
        im.save(out_path, format="JPEG", quality=90)
        return out_path


def _probe_duration(src_path: Path) -> Optional[float]:
    try:
        ffmpeg_path = iioffmpeg.get_ffmpeg_exe()
        proc = subprocess.run(
            [ffmpeg_path, "-hide_banner", "-i", str(src_path), "-f", "null", "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        m = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}(?:\.\d+)?)", proc.stdout)
        if not m:
            return None
        hh, mm, ss = m.groups()
        return int(hh) * 3600 + int(mm) * 60 + float(ss)
    except Exception:
        return None


def _make_video_thumb(src_path: Path) -> Path:
    out_path = settings.thumb_dir / f"{src_path.stem}.jpg"
    ffmpeg_path = iioffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_path,
        "-ss",
        "1",
        "-i",
        str(src_path),
        "-frames:v",
        "1",
        "-vf",
        f"scale={settings.thumb_max_width}:-1",
        "-y",
        str(out_path),
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return out_path


def handle_image_upload(file: UploadFile) -> Tuple[Path, Path]:
    temp = _read_to_temp_and_validate(file, settings.image_mime_types, settings.max_image_bytes)
    name = (file.filename or "").lower()
    if name.endswith(".png"):
        suffix = ".png"
    elif name.endswith(".webp"):
        suffix = ".webp"
    elif name.endswith(".jpg") or name.endswith(".jpeg"):
        suffix = ".jpg"
    else:
        ct = file.content_type or ""
        if ct == "image/png":
            suffix = ".png"
        elif ct == "image/webp":
            suffix = ".webp"
        else:
            suffix = ".jpg"
    final = _save_final(temp, suffix)
    thumb = _make_image_thumb(final)
    return final, thumb


def handle_video_upload(file: UploadFile) -> Tuple[Path, Path, Optional[float]]:
    temp = _read_to_temp_and_validate(file, settings.video_mime_types, settings.max_video_bytes)
    name = (file.filename or "").lower()
    if name.endswith(".mp4"):
        suffix = ".mp4"
    elif name.endswith(".webm"):
        suffix = ".webm"
    else:
        ct = file.content_type or ""
        if ct == "video/mp4":
            suffix = ".mp4"
        elif ct == "video/webm":
            suffix = ".webm"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported video format")
    final = _save_final(temp, suffix)
    duration = _probe_duration(final)
    if duration is not None and duration > settings.max_video_seconds:
        try:
            final.unlink(missing_ok=True)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Video too long")
    thumb = _make_video_thumb(final)
    return final, thumb, duration
