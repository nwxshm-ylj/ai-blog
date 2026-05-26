from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class PublicComment(BaseModel):
    id: uuid.UUID
    author_name: str
    content: str
    created_at: datetime


class AdminComment(BaseModel):
    id: uuid.UUID
    post_slug: str
    post_title: str
    author_name: str
    content: str
    is_approved: bool
    created_at: datetime
    updated_at: datetime
