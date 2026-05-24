from __future__ import annotations

from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str

