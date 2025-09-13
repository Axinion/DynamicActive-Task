"""
Embedding service for text similarity and semantic analysis.
Provides lazy-loaded sentence transformers with caching for production use.
"""

import os
import hashlib
import functools
from typing import Optional
import numpy as np
from sentence_transformers import SentenceTransformer


# Global model instance (lazy-loaded)
_model: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        print(f"Loading embedding model: {model_name}")
        _model = SentenceTransformer(model_name)
        print(f"Model loaded successfully: {model_name}")
    return _model


def _hash_text(text: str) -> str:
    """Create a hash of the text for caching purposes."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


@functools.lru_cache(maxsize=2048)
def _embed_text_cached(text_hash: str, text: str) -> np.ndarray:
    """
    Cached embedding function.
    
    Args:
        text_hash: Hash of the text for cache key
        text: The actual text to embed
        
    Returns:
        L2-normalized embedding vector
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    
    # L2-normalize the embedding
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding


def embed_text(text: str) -> np.ndarray:
    """
    Generate L2-normalized embedding for the given text.
    
    Args:
        text: Input text to embed
        
    Returns:
        L2-normalized embedding vector as numpy array
        
    Example:
        >>> embedding = embed_text("Hello world")
        >>> print(embedding.shape)  # (384,) for all-MiniLM-L6-v2
        >>> print(np.linalg.norm(embedding))  # Should be ~1.0 (L2-normalized)
    """
    if not text or not text.strip():
        # Return zero vector for empty text
        model = _get_model()
        return np.zeros(model.get_sentence_embedding_dimension())
    
    text_hash = _hash_text(text)
    return _embed_text_cached(text_hash, text)


def get_embedding_dimension() -> int:
    """
    Get the dimension of the embedding vectors.
    
    Returns:
        Dimension of the embedding vectors
    """
    model = _get_model()
    return model.get_sentence_embedding_dimension()


def clear_cache():
    """Clear the embedding cache. Useful for testing or memory management."""
    _embed_text_cached.cache_clear()


def get_cache_info():
    """Get cache statistics."""
    return _embed_text_cached.cache_info()


# Example usage and testing
if __name__ == "__main__":
    # Test the embedding service
    print("Testing embedding service...")
    
    # Test basic embedding
    text1 = "The quick brown fox jumps over the lazy dog"
    text2 = "A fast brown fox leaps over a sleepy dog"
    text3 = "Completely different content about machine learning"
    
    emb1 = embed_text(text1)
    emb2 = embed_text(text2)
    emb3 = embed_text(text3)
    
    print(f"Embedding dimension: {emb1.shape[0]}")
    print(f"L2 norm of embedding 1: {np.linalg.norm(emb1):.6f}")
    print(f"L2 norm of embedding 2: {np.linalg.norm(emb2):.6f}")
    print(f"L2 norm of embedding 3: {np.linalg.norm(emb3):.6f}")
    
    # Test similarity
    similarity_1_2 = np.dot(emb1, emb2)
    similarity_1_3 = np.dot(emb1, emb3)
    
    print(f"Similarity between text1 and text2: {similarity_1_2:.4f}")
    print(f"Similarity between text1 and text3: {similarity_1_3:.4f}")
    
    # Test caching
    print(f"Cache info: {get_cache_info()}")
    
    # Test with same text (should hit cache)
    emb1_cached = embed_text(text1)
    print(f"Cache info after repeat: {get_cache_info()}")
    print(f"Embeddings are identical: {np.array_equal(emb1, emb1_cached)}")
    
    print("Embedding service test completed successfully!")