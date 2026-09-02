# Implementation Plan

## Goal

Add a small backend in `rest/` for the supplied frontend. It should use uploaded text files and web sources to produce a streamed, cited research answer.

## Contract noted from the frontend

- `POST /api/sources`: repeated multipart `files` field.
- `POST /api/research`: `{ "request": "..." }`.
- Research response: raw streamed Markdown.
- Backend default: `http://localhost:8787`.

## Decisions

- Use FastAPI for the REST API, request validation, async I/O, and streaming.
- Store vectors locally in FAISS and chunk metadata in a Git-ignored JSON file. This is enough for the small test corpus and preserves citation details.
- Use LangChain only where it removes retrieval boilerplate. Keep the research flow in application code.
- Use Tavily for web search via `TAVILY_API_KEY`. A direct API client is easier for a reviewer to run than an MCP server.
- Run local retrieval and web search concurrently. The LLM receives only the resulting evidence.
- Return source citations. If evidence is weak, say so instead of guessing.

## Request flow

```text
upload -> validate -> chunk -> embed -> FAISS + metadata JSON
request -> local retrieval + Tavily search -> evidence -> LLM -> streamed Markdown
```

## Build order

1. FastAPI scaffold, config, CORS, health check.
2. Source upload and chunking.
3. Embeddings, FAISS, metadata JSON, local retrieval.
4. Tavily search in parallel with retrieval.
5. Grounded LLM streaming and citations.
6. Tests, README, examples, evaluation notes, then Docker if time remains.

## Notes

- Keep `.env` and runtime index data out of Git.
- Reject invalid or empty uploads and requests.
- Use timeouts for external calls.
- No database, queue, multi-agent loop, or authentication unless the core work shows a real need.
