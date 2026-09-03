import asyncio
import logging
from typing import Annotated

from fastapi import File, FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse

from app.config import Settings, get_settings
from app.schemas import ResearchRequest, UploadSourcesResponse
from app.services.research import ResearchServiceError, start_research
from app.services.retrieval import SourceIndex, SourceIndexError
from app.services.uploads import SourceUploadError, read_text_upload
from app.services.web_search import search_web


logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None):
    
    runtime_settings = settings or get_settings()
    app = FastAPI(title="BoWatt Research Agent API", version="0.1.0")
    source_index = SourceIndex(runtime_settings.data_dir)

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

    @app.post("/api/research", response_model=None)
    async def research(
        research_request: ResearchRequest,
    ) -> PlainTextResponse | StreamingResponse:
        if not runtime_settings.groq_api_key:
            return PlainTextResponse(
                "GROQ_API_KEY is not configured.",
                status_code=503,
            )

        if runtime_settings.tavily_api_key:
            local_result, web_result = await asyncio.gather(
                source_index.search(research_request.request),
                search_web(
                    research_request.request,
                    runtime_settings.tavily_api_key,
                ),
                return_exceptions=True,
            )
        else:
            try:
                local_result = await source_index.search(research_request.request)
            except Exception as error:
                local_result = error
            web_result = []

        local_failed = isinstance(local_result, Exception)
        web_failed = isinstance(web_result, Exception)
        chunks = [] if local_failed else local_result
        web_results = [] if web_failed else web_result

        if local_failed:
            logger.warning("Local source search failed: %s", local_result)
        if web_failed:
            logger.warning("External search failed: %s", web_result)

        if not chunks and not web_results:
            if local_failed or web_failed:
                return PlainTextResponse(
                    "Unable to retrieve research sources.",
                    status_code=503,
                )
            return PlainTextResponse(
                "No relevant research sources were found.",
                status_code=400,
            )

        try:
            response_stream = await start_research(
                research_request.request,
                chunks,
                web_results,
                api_key=runtime_settings.groq_api_key,
                model=runtime_settings.groq_model,
            )
        except ResearchServiceError:
            return PlainTextResponse(
                "Unable to start research generation.",
                status_code=503,
            )

        return StreamingResponse(response_stream, media_type="text/markdown")

    return app


app = create_app()
