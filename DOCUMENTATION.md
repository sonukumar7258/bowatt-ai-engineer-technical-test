# Research Agent Backend

## Current status

The repository contains the supplied React frontend and a FastAPI backend in `rest/`.
The backend currently supports uploading UTF-8 text sources, indexing them locally, and
searching them alongside external web sources. Groq streams a grounded answer with
citations to the evidence used.

Implemented endpoints:

- `GET /health`
- `POST /api/sources`
- `POST /api/research`

## Setup

The project was developed with Python 3.12 in a Conda environment named `bowatt-test`.

```powershell
cd rest
conda create -n bowatt-test python=3.12
conda activate bowatt-test
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set the required Groq API key in `rest/.env`. The Tavily key is optional; without it,
research requests use only uploaded local sources.

```env
GROQ_API_KEY=your-key
GROQ_MODEL=qwen/qwen3.6-27b
TAVILY_API_KEY=your-key
CORS_ORIGINS=http://localhost:5173
```

The `.env` file and generated index data are excluded from Git.

Start the backend from `rest/`:

```powershell
uvicorn app.main:app --reload --port 8787
```

From the repository root, start the supplied frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and sends requests to
`http://localhost:8787` by default.

## Tests

Run the automated tests from `rest/`:

```powershell
python -m pytest -q
```

The automated suite currently contains 10 tests. It covers text chunking,
research-request validation, upload validation, evidence labels, and source-list
filtering. Groq and Tavily were checked with manual requests instead of automated live
tests so that the test suite does not require API keys or use credits.

## Sample source

The repository includes
[`test-data/northbridge-microgrid-handbook.md`](test-data/northbridge-microgrid-handbook.md),
a fictional microgrid handbook used for the local and combined research examples below.
Upload it through the frontend to reproduce those examples. Its organizations,
equipment, measurements, and procedures are invented and are only for testing.

## Docker

The backend can run in Docker. The image installs a CPU-only PyTorch build so that the
embedding model does not pull GPU libraries into the container.

Build the image from the repository root:

```powershell
docker build -t bowatt-research-api ./rest
```

Run it with the local environment file and a mounted directory for the generated FAISS
index and metadata:

```powershell
New-Item -ItemType Directory -Force .\rest\data | Out-Null
docker run --rm -p 8787:8787 --env-file .\rest\.env -v "${PWD}\rest\data:/app/data" bowatt-research-api
```

The frontend can continue running locally with `npm run dev` and connects to the
container at `http://localhost:8787`. The container health endpoint was verified with a
local `200` response from `GET /health`. The first upload or local research request can
take longer while the embedding model downloads inside the container. A clean-container
test also verified that a source can be uploaded again after clearing generated data and
that local and external research requests complete successfully.

## API usage

### Upload sources

`POST /api/sources` accepts one or more files under the repeated multipart field
`files`. The current implementation accepts non-empty UTF-8 `text/*` files up to 5 MiB.

```powershell
curl.exe -X POST "http://127.0.0.1:8787/api/sources" `
    -F "files=@path\to\notes.md;type=text/markdown"
```

Example response:

```json
{
  "uploaded": [
    {
      "name": "notes.md",
      "size": 2048,
      "type": "text/markdown"
    }
  ]
}
```

### Submit a research request

`POST /api/research` accepts JSON containing a non-empty `request` string. The response
is raw streamed Markdown rather than server-sent events.

```json
{
  "request": "When should the backup generator start and stop?"
}
```

Example response:

```markdown
The backup generator should start when the documented battery or forecast conditions
are met [L1]. It should stop only after the stated recovery conditions are satisfied
[L1].

## Sources
- [L1] operations-handbook.md, chunk 9
```

The source list is written by the backend. It includes only chunks cited in the model's
answer.

### Example research queries

The following are excerpts from manual test runs. Citation label numbers can change
between requests because labels are assigned from the retrieval order.

Local document query:

```text
According to the Northbridge handbook, when should BG-12 start and stop during island mode?
```

Example response:

```markdown
According to the Northbridge handbook, BG-12 should start during island mode when the
battery reaches 32 percent state of charge or when the two-hour forecast shows an energy
deficit greater than 1.0 megawatt-hour [L1] [L2].

BG-12 should stop only after the battery has recovered to 55 percent and the two-hour
forecast shows a surplus of at least 0.5 megawatt-hour [L2].

## Sources
- [L1] northbridge-microgrid-handbook.md, chunk 8
- [L2] northbridge-microgrid-handbook.md, chunk 9
```

External research query:

```text
What are the main changes in Python 3.14?
```

Example response excerpt:

```markdown
Based on the provided evidence, the main changes in Python 3.14 include updates to the
language, implementation, and standard library.

* **Template String Literals:** Python 3.14 introduces template string literals as a
  major language change [W1].
* **Free-Threaded Build (No-GIL):** Python 3.14 officially supports a free-threaded
  build that removes the Global Interpreter Lock [W2].
* **Zstandard Compression:** A new `compression.zstd` module provides support for
  Zstandard compression [W1].

## Sources
- [W1] [What's new in Python 3.14 - Python 3.14.7 documentation](https://docs.python.org/3/whatsnew/3.14.html)
- [W2] [Python 3.14: 12 Features You Can Use Today](https://www.nb-data.com/p/python-314-12-features-you-can-use)
```

Combined research query:

```text
How do batteries and backup generators support microgrid island mode, and how does that compare with the Northbridge BG-12 rules?
```

Example response excerpt:

```markdown
Batteries and backup generators support microgrid island mode through complementary
roles in stability, power supply, and fuel management.

* **Batteries:** The Willow battery provides fast frequency support to stabilize the
  microgrid [L2].
* **Backup generators:** Generators provide sustained power during outages and black-start
  support [L3]. In island mode, the generator becomes responsible for stabilizing voltage
  and frequency without the main utility grid [W3].

For Northbridge, BG-12 starts when battery state of charge drops to 32 percent or the
two-hour forecast predicts an energy deficit greater than 1.0 megawatt-hour [L1] [L2].
It stops after the battery reaches 55 percent and the forecast shows a surplus of at
least 0.5 megawatt-hour [L1].

## Sources
- [L1] northbridge-microgrid-handbook.md, chunk 9
- [L2] northbridge-microgrid-handbook.md, chunk 8
- [L3] northbridge-microgrid-handbook.md, chunk 1
- [W3] [Power Plant Generators vs. Microgrid Resiliency - Generator Source](https://generatorsource.com/power-insights/power-plant-generators-vs-microgrid-resiliency)
```

Partially answerable query:

```text
According to the Northbridge handbook, who manufactured the Willow battery, and what is its capacity?
```

Example response:

```markdown
According to the Northbridge handbook, the capacity of the Willow battery is 7.5
megawatt-hours [L6]. The provided sources do not contain enough information to answer who
manufactured the Willow battery.

## Sources
- [L6] northbridge-microgrid-handbook.md, chunk 21
```

## Architecture

The backend uses a small retrieval-augmented generation flow:

```text
text upload
    -> validation
    -> overlapping chunks
    -> local embeddings
    -> FAISS index + JSON metadata

research request
    -> local similarity search + Tavily search in parallel
    -> relevant local and web evidence
    -> Groq chat completion
    -> streamed Markdown + source list
```

### Source ingestion

Uploaded files are validated before indexing. Text is split into chunks of roughly 750
characters with 100 characters of overlap. The splitter prefers a newline or space near
the end of a chunk so that it does not cut every passage at an arbitrary character.

The chunks are embedded with `sentence-transformers/all-MiniLM-L6-v2`. Embeddings are
normalized and stored in a native FAISS `IndexFlatIP` index. With normalized vectors,
inner-product ranking is equivalent to cosine-similarity ranking.

FAISS stores vector IDs and vectors. The corresponding filename, source ID, chunk
number, content type, size, and original text are stored in `rest/data/sources.json`.
The index is stored in `rest/data/research.faiss`.

### Retrieval

The request is embedded with the same local model used during ingestion. FAISS returns
up to six nearest chunks. A minimum similarity score of `0.30` removes weak matches
before generation. When `TAVILY_API_KEY` is configured, a basic Tavily search runs at
the same time and returns up to four web results. If one retrieval path fails, the other
can still provide evidence. If neither path returns evidence, Groq is not called.

The threshold is an initial value based on a small set of relevant and unrelated test
queries. A larger evaluation set will tune it rather than treating it as a universal
constant.

When Tavily is configured, the application starts local retrieval and web search for
every research request. There is no intent router deciding which source to use. Both
operations are passed to `asyncio.gather`, so the embedding and FAISS work can overlap
with the Tavily network request. Generation begins after both operations finish. This
makes retrieval behavior predictable and demonstrates useful parallelism without adding
a routing model or another LLM call.

This choice means that a clearly local question still consumes one Tavily search credit.
That is acceptable for the current small test workload. If search cost or irrelevant web
context becomes a measured problem, a later version will add an explicit request option
or a lightweight routing rule. An LLM-based intent router remains out of scope because it
adds latency, cost, and failure modes before there is evidence that it is needed.

### Generation and citations

Retrieved chunks receive temporary local labels according to their rank for the current
request: `[L1]`, `[L2]`, and so on. Tavily results receive `[W1]`, `[W2]`, and so on.
These labels are assigned per request and may map to different sources on the next
request.

Groq receives two messages:

1. A system instruction requiring answers to use only directly supported evidence,
   report partial or insufficient context, and use exact `[L#]` or `[W#]` citations.
2. The research request followed by each local chunk's label, filename, chunk number,
   and text, plus each web result's label, title, URL, and snippet.

Embedding vectors, similarity scores, the full FAISS index, and non-retrieved chunks are
not sent to Groq. Tavily's optional generated answer and raw page content are not
requested; the application synthesizes the returned result snippets itself.

The generation prompt asks the model to treat an uploaded document as authoritative for
questions about what that document says. For external facts, it prefers official and
first-party sources, then original research, reputable secondary sources, and finally
community posts or videos. This is a prompt-level preference rather than a search-result
filter, so source authority remains part of evaluation.

The completion is opened before the HTTP streaming response begins. This allows
authentication, model, connection, and other startup failures to be returned as a
normal `503` response. Once generation starts, text is forwarded to the frontend as raw
Markdown. The backend tracks cited labels and appends a deterministic source section
containing only the cited chunks.

## Error handling

The API reports errors before expensive work where possible. Examples include:

- `400` for empty files, invalid UTF-8, or when neither local nor web search returns
  relevant evidence.
- `413` for files larger than 5 MiB.
- `415` for unsupported file content types.
- `422` for a missing, blank, or invalid research request.
- `503` when neither retrieval path is usable, or for indexing, Groq configuration, and
  Groq startup failures.

If the Groq connection fails after streaming has begun, the response includes a short
warning because the HTTP status can no longer be changed.

## Design decisions and trade-offs

FastAPI provides request validation, async endpoints, and streaming without introducing
an agent framework. The retrieval and prompting flow is ordinary application code; the
project does not use LangChain or LlamaIndex.

Tavily is called through its HTTP API using `httpx` rather than an integration framework.
Basic search was selected because it returns concise result snippets at lower latency and
credit cost than advanced search. Tavily's generated answer is disabled so that Groq has
one clear responsibility for synthesis and citations.

Local and external retrieval fail independently. If Tavily is unavailable, local
evidence can still produce an answer. If the local embedding or index search fails, web
evidence can still be used. The endpoint returns an error only when neither path provides
usable evidence. This partial-failure behavior is more useful than failing the entire
request because one optional source is unavailable.

FAISS and JSON metadata keep the project easy to run and inspect. This is suitable for a
single-process technical test, but concurrent application replicas could write to the
same files unsafely. A production deployment will need a shared vector store and
transactional metadata storage.

The embedding model loads in-process and may make the first upload or request slower.
This avoids a separate embedding service but increases application memory usage.

The current index appends every upload. It does not deduplicate files, replace older
versions, delete sources, or isolate sources by user. Those capabilities are deliberately
out of scope for the current single-user implementation.

## Evaluation completed and future evaluation

Evaluation separates retrieval quality from answer quality. This makes it possible to
identify whether a poor answer came from missing evidence or from generation.

Completed checks:

- The automated suite passed 10 tests for chunking, request validation, upload
  validation, prompt evidence labels, and source-list filtering.
- Manual local research verified the BG-12 start and stop thresholds against the
  Northbridge handbook.
- Manual external research verified web citations and an official Python documentation
  source for a Python 3.14 question.
- Manual combined research verified that local `[L#]` and web `[W#]` citations can
  appear together and that the final source list includes only cited evidence.
- Manual partial-answer testing verified that the system reports the Willow battery
  capacity while declining to invent a manufacturer.
- Manual frontend testing verified file upload, streamed responses, and rendered
  Markdown links, headings, lists, and inline code.
- Docker image build and container health testing verified that `GET /health` returns
  `200` from the container.
- Manual Docker testing cleared generated data, uploaded the handbook again, and completed
  two research requests successfully.

Future evaluation will use a small labeled query set containing the expected supporting
chunks and expected answer behavior. It will measure:

- Recall at six: whether at least one supporting chunk appears in the retrieved set.
- Precision of chunks above the similarity threshold.
- Behavior on unrelated queries that return no evidence.
- Retrieval across multiple uploaded documents with overlapping terminology.
- Citation validity and completeness against the source text.
- Grounded refusals and partial answers.
- Preference for authoritative web sources when both primary and secondary sources are
  returned.
- Behavior when either local retrieval or Tavily is unavailable.

The regression set will keep each request, expected facts, expected source file, and
expected behavior in a simple JSON file. Automated checks will validate retrieval IDs
and citation syntax, while a small human review will confirm that cited text supports the
answer.

## Plans and remaining work

The remaining work is prioritized as follows:

1. Extend the automated tests to cover similarity filtering, concurrent retrieval,
   partial failures, and interrupted streaming.
2. Build a labeled evaluation set and tune the `0.30` similarity threshold from measured
   retrieval precision and recall rather than the current manual examples.
3. Add source lifecycle operations such as listing, replacing, and deleting uploads.
   Deduplication will prevent repeated uploads from adding identical chunks.
4. Improve web-source quality controls beyond the current prompt preference with domain
   allowlists, source-authority scoring, or a user-selectable web-search mode.
5. Evaluate an MCP-compatible external-source adapter if the application later needs to
   connect to several research tools or source providers. The direct Tavily HTTP client
   remains simpler for the current single-provider implementation.
6. Add upload queueing if uploads become larger or sustained concurrent ingestion makes
   synchronous indexing slow. A queued version will need job status and restart handling.
7. Move FAISS and metadata to shared services if the application needs multiple backend
   replicas or separate user workspaces.
8. Add request tracing and basic latency metrics for embedding, local retrieval, Tavily,
   time to first token, and total generation time.
