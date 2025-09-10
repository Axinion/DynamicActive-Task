import numpy as np
from typing import Optional
from sentence_transformers import SentenceTransformer
from ..core.config import settings

# Global model instance
_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Get or create the embedding model instance."""
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_text(text: str) -> np.ndarray:
    """Generate embedding for a text string."""
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding


def embed_texts(texts: list[str]) -> np.ndarray:
    """Generate embeddings for multiple text strings."""
    model = get_embedding_model()
    embeddings = model.encode(texts)
    return embeddings


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_similar_texts(query_embedding: np.ndarray, text_embeddings: np.ndarray, top_k: int = 5) -> list[tuple[int, float]]:
    """Find most similar texts based on cosine similarity."""
    similarities = []
    for i, embedding in enumerate(text_embeddings):
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((i, similarity))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]
