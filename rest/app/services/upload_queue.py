import asyncio
import logging
from dataclasses import dataclass
from uuid import uuid4

from app.schemas import UploadedSource
from app.services.retrieval import SourceIndex
from app.services.uploads import UploadedTextSource


logger = logging.getLogger(__name__)


@dataclass
class UploadJob:
    job_id: str
    sources: list[UploadedTextSource]
    status: str = "queued"
    error: str | None = None

    @property
    def uploaded(self) -> list[UploadedSource]:
        return [source.uploaded for source in self.sources]


class UploadQueue:
    def __init__(self, source_index: SourceIndex):
        self._source_index = source_index
        self._queue: asyncio.Queue[UploadJob] = asyncio.Queue()
        self._jobs: dict[str, UploadJob] = {}
        self._worker_task: asyncio.Task[None] | None = None

    def start(self) -> None:
        self._worker_task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._worker_task is None:
            return

        self._worker_task.cancel()
        try:
            await self._worker_task
        except asyncio.CancelledError:
            pass

    def enqueue(self, sources: list[UploadedTextSource]) -> UploadJob:
        job = UploadJob(job_id=uuid4().hex, sources=sources)
        self._jobs[job.job_id] = job
        self._queue.put_nowait(job)
        return job

    def get(self, job_id: str) -> UploadJob | None:
        return self._jobs.get(job_id)

    async def _run(self) -> None:
        while True:
            job = await self._queue.get()
            job.status = "processing"

            try:
                await self._source_index.add_sources(job.sources)
            except Exception:
                logger.exception("Upload job %s failed.", job.job_id)
                job.status = "failed"
                job.error = "Unable to index uploaded sources."
            else:
                job.status = "completed"
            finally:
                self._queue.task_done()
