import pytest
from api.rag import chunk_text, generate_embeddings, compute_cosine_similarity

def test_chunk_text_basic():
    text = "This is a sentence. This is another sentence. Here is a third one."
    # With a small max_chars limit, it should split
    chunks = chunk_text(text, max_chars=30)
    assert len(chunks) > 1
    assert "This is a sentence." in chunks[0]

def test_chunk_text_handles_empty():
    chunks = chunk_text("", max_chars=100)
    assert chunks == []
    
def test_mock_generate_embeddings_length():
    chunks = ["Chunk one", "Chunk two"]
    embeddings = generate_embeddings(chunks)
    assert len(embeddings) == 2
    # Simple semantic assertion: check if embedding dimensionality is > 0
    assert len(embeddings[0]) > 0

def test_cosine_similarity_identical():
    emb1 = [1.0, 0.0, 0.0]
    emb2 = [1.0, 0.0, 0.0]
    sim = compute_cosine_similarity(emb1, emb2)
    assert pytest.approx(sim, 0.01) == 1.0

def test_cosine_similarity_orthogonal():
    emb1 = [1.0, 0.0, 0.0]
    emb2 = [0.0, 1.0, 0.0]
    sim = compute_cosine_similarity(emb1, emb2)
    assert pytest.approx(sim, 0.01) == 0.0
