from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_IMAGE_UPLOAD_SIZE = 5 * 1024 * 1024
APP_DIR = Path(__file__).resolve().parents[1]
UPLOAD_ROOT = APP_DIR / "static" / "uploads"
STATIC_UPLOAD_PREFIX = "/static/uploads"


class UploadValidationError(ValueError):
    pass


async def save_cover_image(upload: UploadFile) -> str:
    content_type = (upload.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        allowed = ", ".join(sorted(ALLOWED_IMAGE_TYPES))
        raise UploadValidationError(f"封面图片类型必须是：{allowed}。")

    content = await upload.read(MAX_IMAGE_UPLOAD_SIZE + 1)
    await upload.close()
    if len(content) > MAX_IMAGE_UPLOAD_SIZE:
        raise UploadValidationError("封面图片不能超过 5 MB。")
    if not content:
        raise UploadValidationError("封面图片不能为空。")

    extension = _verified_image_extension(content, content_type)
    now = datetime.now(timezone.utc)
    upload_dir = UPLOAD_ROOT / f"{now.year:04d}" / f"{now.month:02d}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4().hex}.{extension}"
    destination = upload_dir / stored_filename
    destination.write_bytes(content)

    return f"{STATIC_UPLOAD_PREFIX}/{now.year:04d}/{now.month:02d}/{stored_filename}"


def _verified_image_extension(content: bytes, content_type: str) -> str:
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
            format_name = (image.format or "").lower()
    except (UnidentifiedImageError, OSError) as exc:
        raise UploadValidationError("封面图片文件无效。") from exc

    expected_extension = ALLOWED_IMAGE_TYPES[content_type]
    if format_name == "jpeg":
        actual_extension = "jpg"
    else:
        actual_extension = format_name

    if actual_extension != expected_extension:
        raise UploadValidationError("封面图片内容与文件类型不匹配。")
    return expected_extension
