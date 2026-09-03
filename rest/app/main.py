from typing import Annotated

from fastapi import File, FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.config import Settings, get_settings
from app.schemas import UploadSourcesResponse
from app.services.retrieval import SourceIndex, SourceIndexError
from app.services.uploads import SourceUploadError, read_text_upload


def create_app(settings: Settings | None = None):
    
    runtime_settings = settings or get_settings()
    app = FastAPI(title="BoWatt Research Agent API", version="0.1.0")
    source_index = SourceIndex(runtime_settings.data_dir)
    app.state.source_index = source_index

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

        sources = []
        for file in files:
            try:
                sources.append(await read_text_upload(file))
            except SourceUploadError as error:
                return PlainTextResponse(error.message, status_code=error.status_code)

        try:
            await source_index.add_sources(sources)
        except SourceIndexError:
            return PlainTextResponse("Unable to index uploaded sources.", status_code=503)

        return UploadSourcesResponse(uploaded=[source.uploaded for source in sources])

    return app


app = create_app()
