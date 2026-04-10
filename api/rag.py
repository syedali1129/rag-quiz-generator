import re
import numpy as np

def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    """
    Splits text into smaller chunks for embeddings.
    A naive implementation splitting by sentences and grouping up to max_chars.
    """
    if not text.strip():
        return []
        
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If a single sentence is longer than max_chars, we just add it anyway.
            # In a robust implementation, we'd split it further.
            current_chunk = sentence
            
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Mock embedding generator for testing without LLM API keys.
    Generates a random float matrix of shape (len(texts), 1536).
    """
    # Simulate OpenAI ada-002 dimensionality
    if not texts:
        return []
    embeddings = np.random.rand(len(texts), 1536).tolist()
    return embeddings

def compute_cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculates the cosine similarity between two vectors.
    """
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    return float(dot_product / (norm_a * norm_b))
