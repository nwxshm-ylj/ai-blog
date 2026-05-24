from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_UPLOAD_SIZE = 5 * 1024 * 1024
APP_DIR = Path(__file__).resolve().parents[1]
UPLOAD_ROOT = APP_DIR / "static" / "uploads"
STATIC_UPLOAD_PREFIX = "/static/uploads"


class UploadValidationError(ValueError):
    pass


async def save_cover_image(upload: UploadFile) -> str:
    filename = upload.filename or ""
    extension = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))
        raise UploadValidationError(f"Cover image must be one of: {allowed}.")

    now = datetime.now(timezone.utc)
    upload_dir = UPLOAD_ROOT / f"{now.year:04d}" / f"{now.month:02d}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4().hex}.{extension}"
    destination = upload_dir / stored_filename
    size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_IMAGE_UPLOAD_SIZE:
                    raise UploadValidationError("Cover image must be 5 MB or smaller.")
                output.write(chunk)
    except UploadValidationError:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    return f"{STATIC_UPLOAD_PREFIX}/{now.year:04d}/{now.month:02d}/{stored_filename}"
