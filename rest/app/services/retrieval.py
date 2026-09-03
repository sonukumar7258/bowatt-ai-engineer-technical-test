import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.services.uploads import UploadedTextSource


CHUNK_SIZE = 750
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MIN_SIMILARITY_SCORE = 0.30


class SourceIndexError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetrievedChunk:
    vector_id: int
    filename: str
    chunk_index: int
    text: str
    score: float


class SourceIndex:
    """Local FAISS index with JSON metadata for a small uploaded-source corpus."""

    def __init__(self, data_dir: Path):
        self._data_dir = data_dir
        self._index_path = data_dir / "research.faiss"
        self._metadata_path = data_dir / "sources.json"
        self._lock = asyncio.Lock()
        self._model: SentenceTransformer | None = None
        self._index: faiss.Index | None = None
        self._metadata: dict[int, dict[str, object]] = {}
        self._next_vector_id = 0
        self._load_persisted_index()

    async def add_sources(self, sources: list[UploadedTextSource]) -> None:
        chunks = self._build_chunks(sources)
        if not chunks:
            return

        async with self._lock:
            try:
                vectors = await asyncio.to_thread(self._embed, [chunk["text"] for chunk in chunks])
                await asyncio.to_thread(self._add_and_persist, vectors, chunks)
            except Exception as error:
                # Model loading and local file writes are the service boundary for indexing.
                raise SourceIndexError("Source indexing failed.") from error

    async def search(self, query: str, limit: int = 4) -> list[RetrievedChunk]:
        async with self._lock:
            if self._index is None:
                return []

            try:
                query_vector = await asyncio.to_thread(self._embed, [query])
                scores, vector_ids = await asyncio.to_thread(self._index.search, query_vector, limit)
            except Exception as error:
                raise SourceIndexError("Source retrieval failed.") from error

        matches = []
        for score, vector_id in zip(scores[0], vector_ids[0], strict=True):
            if vector_id == -1:
                continue
            if float(score) < MIN_SIMILARITY_SCORE:
                continue

            metadata = self._metadata.get(int(vector_id))
            if metadata is None:
                continue

            matches.append(
                RetrievedChunk(
                    vector_id=int(vector_id),
                    filename=str(metadata["filename"]),
                    chunk_index=int(metadata["chunk_index"]),
                    text=str(metadata["text"]),
                    score=float(score),
                )
            )

        return matches

    def _build_chunks(self, sources: list[UploadedTextSource]) -> list[dict[str, object]]:
        chunks = []
        for source in sources:
            source_id = uuid4().hex
            for chunk_index, text in enumerate(chunk_text(source.text)):
                chunks.append(
                    {
                        "source_id": source_id,
                        "filename": source.uploaded.name,
                        "content_type": source.uploaded.type,
                        "size": source.uploaded.size,
                        "chunk_index": chunk_index,
                        "text": text,
                    }
                )
        return chunks

    def _embed(self, texts: list[object]) -> np.ndarray:
        if self._model is None:
            self._model = SentenceTransformer(EMBEDDING_MODEL)

        vectors = self._model.encode(
            [str(text) for text in texts],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return np.ascontiguousarray(vectors, dtype=np.float32)

    def _add_and_persist(self, vectors: np.ndarray, chunks: list[dict[str, object]]) -> None:
        if self._index is None:
            self._index = faiss.IndexIDMap2(faiss.IndexFlatIP(vectors.shape[1]))
        elif self._index.d != vectors.shape[1]:
            raise SourceIndexError("Embedding dimensions do not match the stored index.")

        vector_ids = np.arange(
            self._next_vector_id,
            self._next_vector_id + len(chunks),
            dtype=np.int64,
        )
        self._index.add_with_ids(vectors, vector_ids)

        for vector_id, chunk in zip(vector_ids, chunks, strict=True):
            self._metadata[int(vector_id)] = {"vector_id": int(vector_id), **chunk}

        self._next_vector_id += len(chunks)
        self._persist()

    def _load_persisted_index(self) -> None:
        if not self._index_path.exists() and not self._metadata_path.exists():
            return
        if not self._index_path.exists() or not self._metadata_path.exists():
            raise SourceIndexError("Stored source index is incomplete.")

        self._index = faiss.read_index(str(self._index_path))
        stored_metadata = json.loads(self._metadata_path.read_text(encoding="utf-8"))
        self._metadata = {
            int(chunk["vector_id"]): chunk for chunk in stored_metadata.get("chunks", [])
        }
        self._next_vector_id = max(self._metadata, default=-1) + 1

    def _persist(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        index_temp_path = self._index_path.with_suffix(".tmp")
        metadata_temp_path = self._metadata_path.with_suffix(".tmp")

        faiss.write_index(self._index, str(index_temp_path))
        metadata_temp_path.write_text(
            json.dumps({"chunks": list(self._metadata.values())}, indent=2),
            encoding="utf-8",
        )

        index_temp_path.replace(self._index_path)
        metadata_temp_path.replace(self._metadata_path)


def chunk_text(text: str) -> list[str]:
    normalized_text = text.replace("\r\n", "\n").strip()
    chunks = []
    start = 0

    while start < len(normalized_text):
        end = min(start + CHUNK_SIZE, len(normalized_text))
        if end < len(normalized_text):
            boundary = max(
                normalized_text.rfind("\n", start + CHUNK_SIZE // 2, end),
                normalized_text.rfind(" ", start + CHUNK_SIZE // 2, end),
            )
            if boundary > start:
                end = boundary

        chunk = normalized_text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == len(normalized_text):
            break

        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks
