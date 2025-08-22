from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID

from fastapi import FastAPI, UploadFile, Form, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import settings
from .models import SubmissionAdmin, SubmissionPublic, SubmissionDetail, Status, MediaType, AdminLoginRequest, SubmissionCreateResponse
from .storage import store
from .auth import create_token, verify_admin_password, require_admin
from .media import handle_image_upload, handle_video_upload

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: ({"detail": "Too Many Requests"}, 429))
app.add_middleware(SlowAPIMiddleware)

settings.media_root.mkdir(parents=True, exist_ok=True)
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.thumb_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(settings.media_root)), name="media")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


def _build_thumb_url(request: Request, path: str) -> str:
    return str(request.base_url).rstrip("/") + "/media/" + path.replace(str(settings.media_root) + "/", "")


def _build_media_url(request: Request, path: str) -> str:
    return str(request.base_url).rstrip("/") + "/media/" + path.replace(str(settings.media_root) + "/", "")


@app.post("/api/admin/login")
def admin_login(payload: AdminLoginRequest):
    if not verify_admin_password(payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    token = create_token()
    return {"token": token}


@app.post("/api/submissions", response_model=SubmissionCreateResponse, status_code=201)
@limiter.limit("5/minute")
async def create_submission(
    request: Request,
    file: UploadFile,
    title: str = Form(...),
    author_name: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    name_lower = (file.filename or "").lower()
    ct = file.content_type or ""
    is_image = (ct in settings.image_mime_types) or any(name_lower.endswith(ext) for ext in settings.image_exts)
    is_video = (ct in settings.video_mime_types) or any(name_lower.endswith(ext) for ext in settings.video_exts)
    if is_image:
        media_type = MediaType.image
        final, thumb = handle_image_upload(file)
        duration = None
    elif is_video:
        media_type = MediaType.video
        final, thumb, duration = handle_video_upload(file)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported media type")
    sub = SubmissionAdmin(
        id=uuid4(),
        title=title,
        author_name=author_name,
        description=description,
        tags=tag_list,
        media_type=media_type,
        file_path=str(final),
        thumb_path=str(thumb),
        duration_seconds=duration,
        created_at=datetime.utcnow(),
        status=Status.pending,
        rejected_reason=None,
    )
    await store.create(sub)
    return SubmissionCreateResponse(id=sub.id, status=sub.status)


@app.get("/api/gallery", response_model=list[SubmissionPublic])
async def list_gallery(request: Request):
    items = await store.list(status=Status.approved)
    res: list[SubmissionPublic] = []
    for s in items:
        thumb_url = _build_thumb_url(request, s.thumb_path or s.file_path)
        detail_url = str(request.base_url).rstrip("/") + f"/api/items/{s.id}"
        res.append(
            SubmissionPublic(
                id=s.id,
                title=s.title,
                author_name=s.author_name,
                tags=s.tags,
                media_type=s.media_type,
                thumb_url=thumb_url,
                detail_url=detail_url,
            )
        )
    return res


@app.get("/api/items/{sid}", response_model=SubmissionDetail)
async def item_detail(sid: UUID, request: Request):
    s = await store.get(sid)
    if not s or s.status != Status.approved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    thumb_url = _build_thumb_url(request, s.thumb_path or s.file_path)
    media_url = _build_media_url(request, s.file_path)
    return SubmissionDetail(
        id=s.id,
        title=s.title,
        author_name=s.author_name,
        description=s.description,
        tags=s.tags,
        media_type=s.media_type,
        thumb_url=thumb_url,
        media_url=media_url,
        duration_seconds=s.duration_seconds,
        created_at=s.created_at,
    )


@app.get("/api/admin/submissions", response_model=list[SubmissionAdmin])
async def admin_list_submissions(status: Optional[Status] = None, admin_ok: bool = Depends(require_admin)):
    return await store.list(status=status)


@app.post("/api/admin/submissions/{sid}/approve", response_model=SubmissionAdmin)
async def admin_approve_submission(sid: UUID, admin_ok: bool = Depends(require_admin)):
    s = await store.get(sid)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return await store.update(sid, status=Status.approved, rejected_reason=None)


@app.post("/api/admin/submissions/{sid}/reject", response_model=SubmissionAdmin)
async def admin_reject_submission(sid: UUID, reason: str = Form(""), admin_ok: bool = Depends(require_admin)):
    s = await store.get(sid)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return await store.update(sid, status=Status.rejected, rejected_reason=reason)
