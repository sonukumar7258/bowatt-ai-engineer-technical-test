from dataclasses import dataclass

from fastapi import UploadFile

from app.schemas import UploadedSource


MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@dataclass
class SourceUploadError(Exception):
    message: str
    status_code: int


async def validate_text_upload(file: UploadFile) -> UploadedSource:
    """Validate one browser upload without persisting its contents yet."""

    filename = file.filename or "unnamed-source"
    content_type = file.content_type or ""

    if not content_type.startswith("text/"):
        raise SourceUploadError(
            message=f"{filename} must have a text/* content type.",
            status_code=415,
        )

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise SourceUploadError(
            message=f"{filename} exceeds the 5 MiB upload limit.",
            status_code=413,
        )

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise SourceUploadError(
            message=f"{filename} must use UTF-8 encoding.",
            status_code=400,
        ) from error

    if not text.strip():
        raise SourceUploadError(
            message=f"{filename} is empty.",
            status_code=400,
        )

    return UploadedSource(name=filename, size=len(content), type=content_type)
