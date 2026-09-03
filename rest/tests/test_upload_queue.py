import asyncio
import time

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.services.retrieval import SourceIndex, SourceIndexError


def wait_for_job(client: TestClient, job_id: str) -> dict:
    for _ in range(30):
        response = client.get(f"/api/upload-jobs/{job_id}")
        assert response.status_code == 200
        job = response.json()
        if job["status"] in {"completed", "failed"}:
            return job
        time.sleep(0.02)

    raise AssertionError("Upload job did not finish.")


def make_client(tmp_path, monkeypatch, index_sources):
    monkeypatch.setattr(SourceIndex, "add_sources", index_sources)
    app = create_app(Settings(data_dir=tmp_path))
    return TestClient(app)


def test_upload_returns_queued_job_and_completes(tmp_path, monkeypatch):
    indexed = []

    async def index_sources(self, sources):
        indexed.extend(source.text for source in sources)

    with make_client(tmp_path, monkeypatch, index_sources) as client:
        response = client.post(
            "/api/sources",
            files={"files": ("source.txt", b"queue test", "text/plain")},
        )

        assert response.status_code == 202
        queued_job = response.json()
        assert queued_job["status"] == "queued"
        assert queued_job["uploaded"][0]["name"] == "source.txt"

        completed_job = wait_for_job(client, queued_job["job_id"])

    assert completed_job["status"] == "completed"
    assert indexed == ["queue test"]


def test_invalid_upload_is_rejected_before_queueing(tmp_path, monkeypatch):
    indexed = []

    async def index_sources(self, sources):
        indexed.extend(sources)

    with make_client(tmp_path, monkeypatch, index_sources) as client:
        response = client.post(
            "/api/sources",
            files={"files": ("source.pdf", b"not text", "application/pdf")},
        )

    assert response.status_code == 415
    assert indexed == []


def test_unknown_upload_job_returns_not_found(tmp_path, monkeypatch):
    async def index_sources(self, sources):
        pass

    with make_client(tmp_path, monkeypatch, index_sources) as client:
        response = client.get("/api/upload-jobs/missing")

    assert response.status_code == 404


def test_failed_indexing_is_reported_by_job_status(tmp_path, monkeypatch):
    async def index_sources(self, sources):
        raise SourceIndexError("Indexing failed.")

    with make_client(tmp_path, monkeypatch, index_sources) as client:
        response = client.post(
            "/api/sources",
            files={"files": ("source.txt", b"queue test", "text/plain")},
        )
        failed_job = wait_for_job(client, response.json()["job_id"])

    assert failed_job["status"] == "failed"
    assert failed_job["error"] == "Unable to index uploaded sources."


def test_upload_jobs_are_processed_in_submission_order(tmp_path, monkeypatch):
    indexed = []

    async def index_sources(self, sources):
        indexed.append(sources[0].text)
        await asyncio.sleep(0.02)

    with make_client(tmp_path, monkeypatch, index_sources) as client:
        first_response = client.post(
            "/api/sources",
            files={"files": ("first.txt", b"first", "text/plain")},
        )
        second_response = client.post(
            "/api/sources",
            files={"files": ("second.txt", b"second", "text/plain")},
        )

        first_job = wait_for_job(client, first_response.json()["job_id"])
        second_job = wait_for_job(client, second_response.json()["job_id"])

    assert first_job["status"] == "completed"
    assert second_job["status"] == "completed"
    assert indexed == ["first", "second"]
