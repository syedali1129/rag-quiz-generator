import re
import math
import random

def chunk_text(text: str, max_chars: int = 500, overlap_sentences: int = 1) -> list[str]:
    """
    Splits text into smaller chunks with an overlap of N sentences to preserve context.
    Improved for Assignment 6 to prevent semantic fragmentation.
    """
    if not text.strip():
        return []
        
    # Improved regex to prevent splitting on decimals or common abbreviations
    sentences = re.split(r'(?<!\b[A-Z]\.)(?<!\b(?:Mr|Ms|Dr|Inc|Ltd|vs)\.)(?<=\.|\?|\!)\s+', text.strip())
    chunks = []
    current_sentences = []
    current_len = 0
    
    for sentence in sentences:
        if current_len + len(sentence) <= max_chars or not current_sentences:
            current_sentences.append(sentence)
            current_len += len(sentence) + 1
        else:
            chunks.append(" ".join(current_sentences))
            # Start new chunk with overlap
            current_sentences = current_sentences[-overlap_sentences:] + [sentence]
            current_len = sum(len(s) + 1 for s in current_sentences)
            
    if current_sentences:
        chunks.append(" ".join(current_sentences))
        
    return chunks

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Mock embedding generator for testing without LLM API keys.
    Generates a random float matrix of shape (len(texts), 1536).
    """
    if not texts:
        return []
    embeddings = [[random.random() for _ in range(1536)] for _ in texts]
    return embeddings

def compute_cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculates the cosine similarity between two vectors.
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    return float(dot_product / (norm_a * norm_b))
