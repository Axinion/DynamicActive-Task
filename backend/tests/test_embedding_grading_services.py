"""
Tests for the embedding and grading services.
Verifies production-ready functionality for Phase 3 AI grading.
"""

import pytest
import numpy as np
from app.services.embeddings import embed_text, get_embedding_dimension, clear_cache, get_cache_info
from app.services.grading import cosine, keyword_coverage, score_short_answer, batch_score_short_answers


class TestEmbeddingService:
    """Test the embedding service functionality."""
    
    def test_embed_text_basic(self):
        """Test basic text embedding functionality."""
        text = "Hello world"
        embedding = embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] > 0  # Should have some dimension
        assert np.linalg.norm(embedding) > 0.99  # Should be L2-normalized
    
    def test_embed_text_empty(self):
        """Test embedding with empty text."""
        embedding = embed_text("")
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] > 0
    
    def test_embed_text_whitespace(self):
        """Test embedding with whitespace-only text."""
        embedding = embed_text("   \n\t   ")
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] > 0
    
    def test_embedding_consistency(self):
        """Test that same text produces same embedding."""
        text = "Consistent text for testing"
        emb1 = embed_text(text)
        emb2 = embed_text(text)
        
        assert np.array_equal(emb1, emb2)
    
    def test_embedding_caching(self):
        """Test that embeddings are cached properly."""
        clear_cache()
        cache_info_before = get_cache_info()
        
        text = "Text for caching test"
        embed_text(text)
        
        cache_info_after = get_cache_info()
        assert cache_info_after.hits == 0  # First call, no hits
        assert cache_info_after.misses == 1  # One miss
        
        # Call again - should hit cache
        embed_text(text)
        cache_info_final = get_cache_info()
        assert cache_info_final.hits == 1  # One hit
        assert cache_info_final.misses == 1  # Still one miss
    
    def test_get_embedding_dimension(self):
        """Test getting embedding dimension."""
        dimension = get_embedding_dimension()
        assert isinstance(dimension, int)
        assert dimension > 0


class TestGradingService:
    """Test the grading service functionality."""
    
    def test_cosine_similarity_identical(self):
        """Test cosine similarity with identical vectors."""
        a = np.array([1, 0, 0])
        b = np.array([1, 0, 0])
        similarity = cosine(a, b)
        assert abs(similarity - 1.0) < 1e-6
    
    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity with orthogonal vectors."""
        a = np.array([1, 0, 0])
        b = np.array([0, 1, 0])
        similarity = cosine(a, b)
        assert abs(similarity - 0.0) < 1e-6
    
    def test_cosine_similarity_empty_vectors(self):
        """Test cosine similarity with empty vectors."""
        a = np.array([])
        b = np.array([])
        similarity = cosine(a, b)
        assert similarity == 0.0
    
    def test_keyword_coverage_perfect(self):
        """Test keyword coverage with all keywords present."""
        answer = "The student needs to isolate the variable and solve the equation using inverse operations"
        keywords = ["isolate", "variable", "solve", "equation", "inverse", "operations"]
        coverage = keyword_coverage(answer, keywords)
        assert coverage == 1.0
    
    def test_keyword_coverage_partial(self):
        """Test keyword coverage with some keywords present."""
        answer = "I need to isolate the variable"
        keywords = ["isolate", "variable", "solve", "equation", "inverse", "operations"]
        coverage = keyword_coverage(answer, keywords)
        assert coverage == 2.0 / 6.0  # 2 out of 6 keywords
    
    def test_keyword_coverage_none(self):
        """Test keyword coverage with no keywords present."""
        answer = "This answer has no relevant keywords"
        keywords = ["isolate", "variable", "solve", "equation"]
        coverage = keyword_coverage(answer, keywords)
        assert coverage == 0.0
    
    def test_keyword_coverage_case_insensitive(self):
        """Test keyword coverage is case-insensitive."""
        answer = "ISOLATE the VARIABLE"
        keywords = ["isolate", "variable"]
        coverage = keyword_coverage(answer, keywords)
        assert coverage == 1.0
    
    def test_keyword_coverage_empty_inputs(self):
        """Test keyword coverage with empty inputs."""
        assert keyword_coverage("", ["keyword"]) == 0.0
        assert keyword_coverage("answer", []) == 0.0
        assert keyword_coverage("", []) == 0.0
    
    def test_score_short_answer_good_answer(self):
        """Test scoring a good short answer."""
        student_answer = "To solve 2x + 3 = 7, I subtract 3 from both sides to isolate the variable x"
        model_answer = "To solve linear equations, isolate the variable by performing inverse operations on both sides"
        rubric_keywords = ["isolate", "variable", "inverse", "operations", "solve"]
        
        result = score_short_answer(student_answer, model_answer, rubric_keywords)
        
        assert "score" in result
        assert "confidence" in result
        assert "explanation" in result
        assert "matched_keywords" in result
        
        assert 0.0 <= result["score"] <= 1.0
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["explanation"], str)
        assert isinstance(result["matched_keywords"], list)
        
        # Should have matched some keywords
        assert len(result["matched_keywords"]) > 0
        assert "isolate" in result["matched_keywords"]
        assert "variable" in result["matched_keywords"]
    
    def test_score_short_answer_empty_answer(self):
        """Test scoring an empty answer."""
        student_answer = ""
        model_answer = "Expected answer"
        rubric_keywords = ["keyword"]
        
        result = score_short_answer(student_answer, model_answer, rubric_keywords)
        
        assert result["score"] == 0.0
        assert result["confidence"] == 0.0
        assert "No answer provided" in result["explanation"]
        assert result["matched_keywords"] == []
    
    def test_score_short_answer_whitespace_answer(self):
        """Test scoring a whitespace-only answer."""
        student_answer = "   \n\t   "
        model_answer = "Expected answer"
        rubric_keywords = ["keyword"]
        
        result = score_short_answer(student_answer, model_answer, rubric_keywords)
        
        assert result["score"] == 0.0
        assert result["confidence"] == 0.0
        assert "No answer provided" in result["explanation"]
    
    def test_batch_score_short_answers(self):
        """Test batch scoring of multiple answers."""
        student_answers = [
            "I isolate the variable by subtracting 3",
            "The answer is x = 5",
            "I don't know how to solve this"
        ]
        model_answers = [
            "Isolate the variable using inverse operations",
            "The solution is x = 5",
            "Use algebraic manipulation to solve"
        ]
        rubric_keywords_list = [
            ["isolate", "variable", "inverse"],
            ["solution", "answer"],
            ["algebraic", "manipulation", "solve"]
        ]
        
        results = batch_score_short_answers(student_answers, model_answers, rubric_keywords_list)
        
        assert len(results) == 3
        for result in results:
            assert "score" in result
            assert "confidence" in result
            assert "explanation" in result
            assert "matched_keywords" in result
    
    def test_batch_score_mismatched_lengths(self):
        """Test batch scoring with mismatched input lengths."""
        student_answers = ["Answer 1", "Answer 2"]
        model_answers = ["Model 1"]
        rubric_keywords_list = [["keyword"]]
        
        with pytest.raises(ValueError):
            batch_score_short_answers(student_answers, model_answers, rubric_keywords_list)


class TestIntegration:
    """Integration tests for embedding and grading services."""
    
    def test_end_to_end_grading_flow(self):
        """Test complete grading flow from text to score."""
        # Test with a realistic math problem
        student_answer = "To solve 3x - 7 = 14, I add 7 to both sides to get 3x = 21, then divide by 3 to get x = 7"
        model_answer = "To solve linear equations, isolate the variable by performing inverse operations. Add 7 to both sides, then divide by 3."
        rubric_keywords = ["isolate", "variable", "inverse", "operations", "add", "divide", "solve"]
        
        result = score_short_answer(student_answer, model_answer, rubric_keywords)
        
        # Verify the result structure
        assert isinstance(result, dict)
        assert all(key in result for key in ["score", "confidence", "explanation", "matched_keywords"])
        
        # Verify score is reasonable (should be decent for this good answer)
        assert result["score"] > 0.5  # Should be a good score
        assert result["confidence"] > 0.5  # Should be confident
        
        # Verify explanation is informative
        assert len(result["explanation"]) > 20  # Should be a reasonable explanation
        assert any(keyword in result["explanation"].lower() for keyword in ["similarity", "concept"])
        
        # Verify matched keywords
        assert len(result["matched_keywords"]) > 0
        assert "solve" in result["matched_keywords"]
    
    def test_different_answer_qualities(self):
        """Test scoring answers of different qualities."""
        model_answer = "To solve linear equations, isolate the variable by performing inverse operations"
        rubric_keywords = ["isolate", "variable", "inverse", "operations", "solve"]
        
        # Excellent answer
        excellent_answer = "I solve linear equations by isolating the variable using inverse operations on both sides"
        excellent_result = score_short_answer(excellent_answer, model_answer, rubric_keywords)
        
        # Poor answer
        poor_answer = "I don't know how to do this"
        poor_result = score_short_answer(poor_answer, model_answer, rubric_keywords)
        
        # Excellent answer should score higher
        assert excellent_result["score"] > poor_result["score"]
        assert excellent_result["confidence"] > poor_result["confidence"]
        assert len(excellent_result["matched_keywords"]) > len(poor_result["matched_keywords"])


if __name__ == "__main__":
    # Run basic tests
    print("Running embedding and grading service tests...")
    
    # Test embedding service
    print("\n=== Embedding Service Tests ===")
    test_emb = TestEmbeddingService()
    test_emb.test_embed_text_basic()
    test_emb.test_embedding_consistency()
    test_emb.test_embedding_caching()
    print("✅ Embedding service tests passed")
    
    # Test grading service
    print("\n=== Grading Service Tests ===")
    test_grad = TestGradingService()
    test_grad.test_cosine_similarity_identical()
    test_grad.test_keyword_coverage_perfect()
    test_grad.test_score_short_answer_good_answer()
    print("✅ Grading service tests passed")
    
    # Test integration
    print("\n=== Integration Tests ===")
    test_int = TestIntegration()
    test_int.test_end_to_end_grading_flow()
    test_int.test_different_answer_qualities()
    print("✅ Integration tests passed")
    
    print("\n🎉 All tests passed! Embedding and grading services are ready for production.")
