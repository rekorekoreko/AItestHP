import os
from pathlib import Path
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = BASE_DIR / "media"
UPLOAD_DIR = MEDIA_ROOT / "uploads"
THUMB_DIR = MEDIA_ROOT / "thumbs"

IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
VIDEO_MIME_TYPES = {"video/mp4", "video/webm"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTS = {".mp4", ".webm"}

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_BYTES = 50 * 1024 * 1024
MAX_VIDEO_SECONDS = 180

THUMB_MAX_WIDTH = 512

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGO = "HS256"
JWT_TTL_SECONDS = 3600


class AppSettings(BaseModel):
    media_root: Path = MEDIA_ROOT
    upload_dir: Path = UPLOAD_DIR
    thumb_dir: Path = THUMB_DIR
    image_mime_types: set[str] = IMAGE_MIME_TYPES
    video_mime_types: set[str] = VIDEO_MIME_TYPES
    image_exts: set[str] = IMAGE_EXTS
    video_exts: set[str] = VIDEO_EXTS
    max_image_bytes: int = MAX_IMAGE_BYTES
    max_video_bytes: int = MAX_VIDEO_BYTES
    max_video_seconds: int = MAX_VIDEO_SECONDS
    thumb_max_width: int = THUMB_MAX_WIDTH
    admin_password: str = ADMIN_PASSWORD
    jwt_secret: str = JWT_SECRET
    jwt_algo: str = JWT_ALGO
    jwt_ttl_seconds: int = JWT_TTL_SECONDS


settings = AppSettings()
