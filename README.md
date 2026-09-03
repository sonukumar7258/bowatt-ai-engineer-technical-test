# BoWatt Applied AI Engineer Technical Test

A small research-agent application built around the supplied React frontend. The FastAPI
backend accepts text sources, indexes them locally, retrieves relevant passages, and
streams a grounded Markdown answer with citations.

## Current capabilities

- Queue one or more UTF-8 `text/*` source files for background indexing.
- Split and embed source text with `sentence-transformers/all-MiniLM-L6-v2`.
- Store vectors in FAISS and citation metadata in a local JSON file.
- Retrieve up to six chunks that meet a cosine-similarity threshold.
- Search the web with Tavily in parallel with local retrieval when configured.
- Generate answers with Groq using only the retrieved local and web evidence.
- Stream raw Markdown with inline citations and a filtered source list.
- Report irrelevant, partially supported, and unsupported requests without guessing.

## Quick start

Create and configure the backend environment:

```powershell
cd rest
conda create -n bowatt-test python=3.12
conda activate bowatt-test
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Add a Groq API key to `rest/.env`, then start the API:

```powershell
uvicorn app.main:app --reload --port 8787
```

From the repository root, start the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend uses `http://localhost:8787` as its default
backend URL.

Run the backend tests from the `rest` directory:

```powershell
python -m pytest -q
```

## Sample source

[`test-data/northbridge-microgrid-handbook.md`](test-data/northbridge-microgrid-handbook.md)
is a fictional handbook used for the local and combined research examples in the
documentation. Upload it through the frontend and wait for indexing to complete before
reproducing those examples.

## Docker

With Docker Desktop running, build the backend image from the repository root:

```powershell
docker build -t bowatt-research-api ./rest
```

Run the container with the local environment file and a mounted data directory:

```powershell
New-Item -ItemType Directory -Force .\rest\data | Out-Null
docker run --rm -p 8787:8787 --env-file .\rest\.env -v "${PWD}\rest\data:/app/data" bowatt-research-api
```

The frontend can still run locally with `npm run dev` and connect to the container at
`http://localhost:8787`. The first upload or local research request can take longer while
the embedding model downloads inside the container.

## Configuration

```env
GROQ_API_KEY=your-key
GROQ_MODEL=qwen/qwen3.6-27b
TAVILY_API_KEY=your-key
CORS_ORIGINS=http://localhost:5173
```

`TAVILY_API_KEY` is optional; without it, research uses uploaded local sources only. The
local `.env` file and generated data under `rest/data/` are excluded from Git.

## API

- `GET /health`
- `POST /api/sources`
- `GET /api/upload-jobs/{job_id}`
- `POST /api/research`

See [DOCUMENTATION.md](DOCUMENTATION.md) for request examples, architecture, design
decisions, error behavior, evaluation plans, and remaining work.
