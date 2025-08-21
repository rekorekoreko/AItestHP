from enum import Enum
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class MediaType(str, Enum):
    image = "image"
    video = "video"


class Status(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class SubmissionAdmin(BaseModel):
    id: UUID
    title: str
    author_name: str
    description: str = ""
    tags: List[str] = []
    media_type: MediaType
    file_path: str
    thumb_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: datetime
    status: Status
    rejected_reason: Optional[str] = None


class SubmissionPublic(BaseModel):
    id: UUID
    title: str
    author_name: str
    tags: List[str] = []
    media_type: MediaType
    thumb_url: str
    detail_url: str


class SubmissionDetail(BaseModel):
    id: UUID
    title: str
    author_name: str
    description: str
    tags: List[str]
    media_type: MediaType
    thumb_url: str
    media_url: str
    duration_seconds: Optional[float] = None
    created_at: datetime


class AdminLoginRequest(BaseModel):
    password: str


class SubmissionCreateResponse(BaseModel):
    id: UUID
    status: Status = Field(default=Status.pending)
