import pytest
from pydantic import ValidationError

from app.schemas import ResearchRequest


def test_research_request_is_trimmed():
    request = ResearchRequest(request="  Explain the source  ")

    assert request.request == "Explain the source"


def test_research_request_cannot_be_empty():
    with pytest.raises(ValidationError):
        ResearchRequest(request="   ")
