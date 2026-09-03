from pydantic import BaseModel, Field, field_validator


class UploadedSource(BaseModel):
    name: str
    size: int
    type: str


class UploadSourcesResponse(BaseModel):
    uploaded: list[UploadedSource]


class ResearchRequest(BaseModel):
    request: str = Field(max_length=4000)

    @field_validator("request")
    @classmethod
    def request_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Research request must not be empty.")
        return value
