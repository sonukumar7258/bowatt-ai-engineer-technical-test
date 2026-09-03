from app.services.retrieval import CHUNK_SIZE, chunk_text


def test_short_text_stays_in_one_chunk():
    assert chunk_text("A short source") == ["A short source"]


def test_long_text_is_split_into_valid_chunks():
    text = "\n".join(f"Section {number}: " + "word " * 30 for number in range(20))

    chunks = chunk_text(text)

    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)
    assert all(len(chunk) <= CHUNK_SIZE for chunk in chunks)
    assert chunks[0].startswith("Section 0")
    assert chunks[-1].endswith("word")
