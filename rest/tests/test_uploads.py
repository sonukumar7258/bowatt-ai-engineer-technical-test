import asyncio
from io import BytesIO

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.services.uploads import SourceUploadError, read_text_upload


def make_upload(content: bytes, content_type: str = "text/plain") -> UploadFile:
    return UploadFile(
        file=BytesIO(content),
        filename="source.txt",
        headers=Headers({"content-type": content_type}),
    )


def test_valid_text_upload():
    result = asyncio.run(read_text_upload(make_upload(b"Useful source text")))

    assert result.text == "Useful source text"
    assert result.uploaded.name == "source.txt"
    assert result.uploaded.size == 18


def test_non_text_upload_is_rejected():
    with pytest.raises(SourceUploadError) as error:
        asyncio.run(read_text_upload(make_upload(b"data", "application/pdf")))

    assert error.value.status_code == 415


def test_empty_upload_is_rejected():
    with pytest.raises(SourceUploadError) as error:
        asyncio.run(read_text_upload(make_upload(b"  \n")))

    assert error.value.status_code == 400
