from app.services.research import _build_sources_section, _build_user_prompt
from app.services.retrieval import RetrievedChunk
from app.services.web_search import WebResult


def local_chunk(number: int) -> RetrievedChunk:
    return RetrievedChunk(
        vector_id=number,
        filename="handbook.txt",
        chunk_index=number,
        text=f"Local evidence {number}",
        score=0.8,
    )


def web_result(number: int) -> WebResult:
    return WebResult(
        title=f"Web source {number}",
        url=f"https://example.com/{number}",
        content=f"Web evidence {number}",
    )


def test_user_prompt_labels_local_and_web_evidence():
    prompt = _build_user_prompt(
        "Compare the sources",
        [local_chunk(3)],
        [web_result(7)],
    )

    assert "Research request:\nCompare the sources" in prompt
    assert "[L1] handbook.txt, chunk 3" in prompt
    assert "[W1] Web source 7" in prompt


def test_sources_section_only_lists_cited_sources():
    sources = _build_sources_section(
        [local_chunk(1), local_chunk(2)],
        [web_result(1), web_result(2)],
        "The answer uses [L2] and [W1].",
    )

    assert "[L2] handbook.txt, chunk 2" in sources
    assert "[W1] [Web source 1](https://example.com/1)" in sources
    assert "[L1]" not in sources
    assert "[W2]" not in sources


def test_sources_section_handles_answer_without_citations():
    sources = _build_sources_section([local_chunk(1)], [], "Not enough information.")

    assert "- No sources were cited." in sources
