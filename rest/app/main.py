from typing import Annotated

from fastapi import File, FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.config import Settings, get_settings
from app.schemas import UploadSourcesResponse
from app.services.uploads import SourceUploadError, validate_text_upload


def create_app(settings: Settings | None = None):
    
    runtime_settings = settings or get_settings()
    app = FastAPI(title="BoWatt Research Agent API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=runtime_settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    @app.post("/api/sources", response_model=UploadSourcesResponse, status_code=201)
    async def upload_sources(
        files: Annotated[list[UploadFile] | None, File()] = None,
    ) -> UploadSourcesResponse | PlainTextResponse:
        if not files:
            return PlainTextResponse("At least one source file is required.", status_code=400)

        uploaded = []
        for file in files:
            try:
                uploaded.append(await validate_text_upload(file))
            except SourceUploadError as error:
                return PlainTextResponse(error.message, status_code=error.status_code)

        return UploadSourcesResponse(uploaded=uploaded)

    return app


app = create_app()
