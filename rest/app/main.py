import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import File, FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse

from app.config import Settings, get_settings
from app.schemas import ResearchRequest, UploadJobResponse
from app.services.research import ResearchServiceError, start_research
from app.services.retrieval import SourceIndex, SourceIndexError
from app.services.upload_queue import UploadQueue
from app.services.uploads import SourceUploadError, read_text_upload
from app.services.web_search import search_web


logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None):
    runtime_settings = settings or get_settings()
    source_index = SourceIndex(runtime_settings.data_dir)
    upload_queue = UploadQueue(source_index)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        upload_queue.start()
        try:
            yield
        finally:
            await upload_queue.stop()

    app = FastAPI(
        title="BoWatt Research Agent API",
        version="0.1.0",
        lifespan=lifespan,
    )

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

    @app.post(
        "/api/sources",
        response_model=UploadJobResponse,
        response_model_exclude_none=True,
        status_code=202,
    )
    async def upload_sources(
        files: Annotated[list[UploadFile] | None, File()] = None,
    ) -> UploadJobResponse | PlainTextResponse:
        if not files:
            return PlainTextResponse("At least one source file is required.", status_code=400)

        sources = []
        for file in files:
            try:
                sources.append(await read_text_upload(file))
            except SourceUploadError as error:
                return PlainTextResponse(error.message, status_code=error.status_code)

        job = upload_queue.enqueue(sources)
        return UploadJobResponse(
            job_id=job.job_id,
            status="queued",
            uploaded=job.uploaded,
        )

    @app.get(
        "/api/upload-jobs/{job_id}",
        response_model=UploadJobResponse,
        response_model_exclude_none=True,
    )
    async def get_upload_job(job_id: str) -> UploadJobResponse | PlainTextResponse:
        job = upload_queue.get(job_id)
        if job is None:
            return PlainTextResponse("Upload job was not found.", status_code=404)

        return UploadJobResponse(
            job_id=job.job_id,
            status=job.status,
            uploaded=job.uploaded,
            error=job.error,
        )

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
