import pytest
from unittest.mock import MagicMock
from onyx.indexing.chunker import Chunker, _combine_chunks, SECTION_SEPARATOR
from onyx.indexing.models import DocAwareChunk
from onyx.connectors.models import IndexingDocument, TextSection, Document
from onyx.configs.constants import DocumentSource
from onyx.indexing.embedder import DefaultIndexingEmbedder
from onyx.indexing.indexing_pipeline import process_image_sections
from onyx.utils.text_processing import clean_text
from tests.unit.onyx.indexing.conftest import MockHeartbeat


@pytest.fixture
def embedder() -> DefaultIndexingEmbedder:
    return DefaultIndexingEmbedder(
        model_name="intfloat/e5-base-v2",
        normalize=True,
        query_prefix=None,
        passage_prefix=None,
    )


@pytest.fixture
def chunker(embedder: DefaultIndexingEmbedder) -> Chunker:
    return Chunker(
        tokenizer=embedder.embedding_model.tokenizer,
        enable_multipass=False,
    )


def test_chunk_document(embedder: DefaultIndexingEmbedder) -> None:
    short_section_1 = "This is a short section."
    long_section = (
        "This is a long section that should be split into multiple chunks. " * 100
    )
    short_section_2 = "This is another short section."
    short_section_3 = "This is another short section again."
    short_section_4 = "Final short section."
    semantic_identifier = "Test Document"

    document = Document(
        id="test_doc",
        source=DocumentSource.WEB,
        semantic_identifier=semantic_identifier,
        metadata={"tags": ["tag1", "tag2"]},
        doc_updated_at=None,
        sections=[
            TextSection(text=short_section_1, link="link1"),
            TextSection(text=short_section_2, link="link2"),
            TextSection(text=long_section, link="link3"),
            TextSection(text=short_section_3, link="link4"),
            TextSection(text=short_section_4, link="link5"),
        ],
    )
    indexing_documents = process_image_sections([document])

    chunker = Chunker(
        tokenizer=embedder.embedding_model.tokenizer,
        enable_multipass=False,
    )
    chunks = chunker.chunk(indexing_documents)

    assert len(chunks) == 5
    assert short_section_1 in chunks[0].content
    assert short_section_3 in chunks[-1].content
    assert short_section_4 in chunks[-1].content
    assert "tag1" in chunks[0].metadata_suffix_keyword
    assert "tag2" in chunks[0].metadata_suffix_semantic


def test_chunker_heartbeat(
    embedder: DefaultIndexingEmbedder, mock_heartbeat: MockHeartbeat
) -> None:
    document = Document(
        id="test_doc",
        source=DocumentSource.WEB,
        semantic_identifier="Test Document",
        metadata={"tags": ["tag1", "tag2"]},
        doc_updated_at=None,
        sections=[
            TextSection(text="This is a short section.", link="link1"),
        ],
    )
    indexing_documents = process_image_sections([document])

    chunker = Chunker(
        tokenizer=embedder.embedding_model.tokenizer,
        enable_multipass=False,
        callback=mock_heartbeat,
    )

    chunks = chunker.chunk(indexing_documents)

    assert mock_heartbeat.call_count == 1
    assert len(chunks) > 0


def test_chunk_document_with_pdf_sections(chunker: Chunker):
    long_content = "This is a long section that should be split into multiple chunks. " * 100
    sections = [
        TextSection(
            text=long_content + " (Page 1)",
            link="http://example.com/doc.pdf#page=1",
            image_file_name=None,
        ),
        TextSection(
            text=long_content + " (Page 2)",
            link="http://example.com/doc.pdf#page=2",
            image_file_name=None,
        ),
        TextSection(
            text=long_content + " (Page 3)",
            link="http://example.com/doc.pdf#page=3",
            image_file_name=None,
        ),
    ]

    doc = IndexingDocument(
        id="test_pdf_doc",
        sections=sections,
        processed_sections=sections, 
        source=DocumentSource.FILE,
        semantic_identifier="test_pdf.pdf",
        metadata={},
        doc_updated_at=None,
        primary_owners=[],
        secondary_owners=[],
        chunk_count=3,
    )

    chunks = chunker.chunk([doc])

    chunks_by_page = {}
    for chunk in chunks:
        link = list(chunk.source_links.values())[0]
        if link not in chunks_by_page:
            chunks_by_page[link] = []
        chunks_by_page[link].append(chunk)

    assert len(chunks_by_page) == 3
    assert all(len(page_chunks) > 0 for page_chunks in chunks_by_page.values())

    for page_num in range(1, 4):
        page_link = f"http://example.com/doc.pdf#page={page_num}"
        assert page_link in chunks_by_page
        for chunk in chunks_by_page[page_link]:
            assert chunk.source_links == {0: page_link}


def test_combine_chunks_with_pdf_sections(chunker: Chunker):
    source_doc = Document(
        id="test_pdf_doc",
        sections=[],
        source=DocumentSource.FILE,
        semantic_identifier="test_pdf.pdf",
        metadata={},
        doc_updated_at=None,
    )

    chunks = [
        DocAwareChunk(
            source_document=source_doc,
            chunk_id=0,
            blurb="Page 1",
            content="Page 1 content",
            source_links={0: "http://example.com/doc.pdf#page=1"},
            section_continuation=False,
            title_prefix="",
            metadata_suffix_semantic="",
            metadata_suffix_keyword="",
            mini_chunk_texts=None,
            large_chunk_reference_ids=[],
            large_chunk_id=None,
            image_file_name=None,
        ),
        DocAwareChunk(
            source_document=source_doc,
            chunk_id=1,
            blurb="Page 2",
            content="Page 2 content",
            source_links={0: "http://example.com/doc.pdf#page=2"},
            section_continuation=True,
            title_prefix="",
            metadata_suffix_semantic="",
            metadata_suffix_keyword="",
            mini_chunk_texts=None,
            large_chunk_reference_ids=[],
            large_chunk_id=None,
            image_file_name=None,
        ),
    ]

    combined_chunk = _combine_chunks(chunks, large_chunk_id=0)

    assert combined_chunk.source_links == {
        0: "http://example.com/doc.pdf#page=1",
        len(SECTION_SEPARATOR) + len("Page 1 content"): "http://example.com/doc.pdf#page=2",
    }
    assert combined_chunk.content == f"Page 1 content{SECTION_SEPARATOR}Page 2 content"
