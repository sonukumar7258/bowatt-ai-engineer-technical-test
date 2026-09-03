# BoWatt Applied AI Engineer Technical Test

A small research-agent application built around the supplied React frontend. The FastAPI
backend accepts text sources, indexes them locally, retrieves relevant passages, and
streams a grounded Markdown answer with citations.

## Current capabilities

- Upload one or more UTF-8 `text/*` source files.
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

Start the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend uses `http://localhost:8787` as its default
backend URL.

## Configuration

```env
GROQ_API_KEY=your-key
GROQ_MODEL=qwen/qwen3.6-27b
TAVILY_API_KEY=your-key
CORS_ORIGINS=http://localhost:5173
```

The local `.env` file and generated data under `rest/data/` are excluded from Git.

## API

- `GET /health`
- `POST /api/sources`
- `POST /api/research`

See [DOCUMENTATION.md](DOCUMENTATION.md) for request examples, architecture, design
decisions, error behavior, evaluation plans, and remaining work.
