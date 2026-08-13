import pytest
from app.services.extraction_service import ExtractionService


def test_markdown_extraction():
    md_content = """# Database Normalization

## First Normal Form
First normal form (1NF) requires that atomic values be stored in each cell.

## Second Normal Form
Second normal form (2NF) requires that non-key attributes depend on the whole primary key.
"""
    segments = ExtractionService.extract_markdown(md_content)
    assert len(segments) >= 2
    assert segments[0].section_title in ["Database Normalization", "First Normal Form"]
    assert "atomic values" in segments[0].content


def test_txt_extraction():
    txt_content = "Paragraph 1 detailing DBMS concepts.\n\nParagraph 2 detailing transactions."
    segments = ExtractionService.extract_txt(txt_content)
    assert len(segments) == 2
    assert segments[0].content == "Paragraph 1 detailing DBMS concepts."
