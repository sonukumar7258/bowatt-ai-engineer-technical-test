from pydantic import BaseModel


class UploadedSource(BaseModel):
    name: str
    size: int
    type: str


class UploadSourcesResponse(BaseModel):
    uploaded: list[UploadedSource]
