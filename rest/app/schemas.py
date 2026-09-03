from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UploadedSource(BaseModel):
    name: str
    size: int
    type: str


class UploadJobResponse(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    uploaded: list[UploadedSource]
    error: str | None = None


class ResearchRequest(BaseModel):
    request: str = Field(max_length=4000)

    @field_validator("request")
    @classmethod
    def request_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Research request must not be empty.")
        return value
