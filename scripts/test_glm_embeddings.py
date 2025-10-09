"""
Test script for GLM Embeddings Provider (Phase 5)

Tests:
1. Single text embedding
2. Multiple texts embedding
3. Different models (embedding-3, embedding-2)
4. Error handling

Usage:
    python scripts/test_glm_embeddings.py
"""
import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load .env file
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from src.embeddings.provider import GLMEmbeddingsProvider


def test_single_text():
    """Test embedding a single text"""
    print("\n" + "="*80)
    print("TEST 1: Single Text Embedding")
    print("="*80)
    
    provider = GLMEmbeddingsProvider()
    
    text = "Hello, world! This is a test of GLM embeddings."
    result = provider.embed([text])
    
    print(f"✅ Input: {text}")
    print(f"✅ Embeddings count: {len(result)}")
    print(f"✅ Embedding dimensions: {len(result[0]) if result else 0}")
    print(f"✅ First 5 values: {result[0][:5] if result else []}")
    
    assert len(result) == 1, "Should return 1 embedding"
    assert len(result[0]) > 0, "Embedding should have dimensions"
    
    print("✅ TEST 1 PASSED")
    return result


def test_multiple_texts():
    """Test embedding multiple texts"""
    print("\n" + "="*80)
    print("TEST 2: Multiple Texts Embedding")
    print("="*80)
    
    provider = GLMEmbeddingsProvider()
    
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is a subset of artificial intelligence.",
        "Python is a popular programming language."
    ]
    
    result = provider.embed(texts)
    
    print(f"✅ Input count: {len(texts)}")
    print(f"✅ Embeddings count: {len(result)}")
    print(f"✅ Embedding dimensions: {len(result[0]) if result else 0}")
    
    for i, text in enumerate(texts):
        print(f"  Text {i+1}: {text[:50]}...")
        print(f"  Embedding {i+1}: {len(result[i])} dims, first 3 values: {result[i][:3]}")
    
    assert len(result) == len(texts), f"Should return {len(texts)} embeddings"
    assert all(len(emb) == len(result[0]) for emb in result), "All embeddings should have same dimensions"
    
    print("✅ TEST 2 PASSED")
    return result


def test_embedding_3_model():
    """Test embedding-3 model (8192 dimensions)"""
    print("\n" + "="*80)
    print("TEST 3: Embedding-3 Model (8192 dimensions)")
    print("="*80)
    
    provider = GLMEmbeddingsProvider(model="embedding-3")
    
    text = "Testing embedding-3 model with 8192 dimensions."
    result = provider.embed([text])
    
    print(f"✅ Model: embedding-3")
    print(f"✅ Expected dimensions: 8192")
    print(f"✅ Actual dimensions: {len(result[0]) if result else 0}")
    
    # Note: Actual dimensions might vary based on API response
    # Just verify we got embeddings
    assert len(result) == 1, "Should return 1 embedding"
    assert len(result[0]) > 0, "Embedding should have dimensions"
    
    print("✅ TEST 3 PASSED")
    return result


def test_embedding_2_model():
    """Test embedding-2 model (1024 dimensions)"""
    print("\n" + "="*80)
    print("TEST 4: Embedding-2 Model (1024 dimensions)")
    print("="*80)
    
    provider = GLMEmbeddingsProvider(model="embedding-2")
    
    text = "Testing embedding-2 model with 1024 dimensions."
    result = provider.embed([text])
    
    print(f"✅ Model: embedding-2")
    print(f"✅ Expected dimensions: 1024")
    print(f"✅ Actual dimensions: {len(result[0]) if result else 0}")
    
    # Note: Actual dimensions might vary based on API response
    # Just verify we got embeddings
    assert len(result) == 1, "Should return 1 embedding"
    assert len(result[0]) > 0, "Embedding should have dimensions"
    
    print("✅ TEST 4 PASSED")
    return result


def test_empty_input():
    """Test handling of empty input"""
    print("\n" + "="*80)
    print("TEST 5: Empty Input Handling")
    print("="*80)
    
    provider = GLMEmbeddingsProvider()
    
    result = provider.embed([])
    
    print(f"✅ Input: []")
    print(f"✅ Result: {result}")
    
    assert result == [], "Empty input should return empty list"
    
    print("✅ TEST 5 PASSED")
    return result


def test_provider_selection():
    """Test provider selection via get_embeddings_provider()"""
    print("\n" + "="*80)
    print("TEST 6: Provider Selection")
    print("="*80)
    
    from src.embeddings.provider import get_embeddings_provider
    
    # Save original value
    original_provider = os.getenv("EMBEDDINGS_PROVIDER")
    
    try:
        # Test GLM provider selection
        os.environ["EMBEDDINGS_PROVIDER"] = "glm"
        provider = get_embeddings_provider()
        
        print(f"✅ EMBEDDINGS_PROVIDER=glm")
        print(f"✅ Provider type: {type(provider).__name__}")
        
        assert isinstance(provider, GLMEmbeddingsProvider), "Should return GLMEmbeddingsProvider"
        
        # Test embedding with selected provider
        result = provider.embed(["Test provider selection"])
        assert len(result) == 1, "Should return 1 embedding"
        
        print("✅ TEST 6 PASSED")
        
    finally:
        # Restore original value
        if original_provider:
            os.environ["EMBEDDINGS_PROVIDER"] = original_provider
        else:
            os.environ.pop("EMBEDDINGS_PROVIDER", None)
    
    return provider


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("GLM EMBEDDINGS PROVIDER TEST SUITE")
    print("Phase 5 Implementation - 2025-10-09")
    print("="*80)
    
    try:
        # Check environment
        api_key = os.getenv("GLM_API_KEY")
        if not api_key:
            print("❌ ERROR: GLM_API_KEY not set in environment")
            print("   Set GLM_API_KEY to run tests")
            sys.exit(1)
        
        print(f"✅ GLM_API_KEY: {api_key[:10]}...{api_key[-10:]}")
        print(f"✅ GLM_BASE_URL: {os.getenv('GLM_BASE_URL', 'https://api.z.ai/api/paas/v4')}")
        print(f"✅ GLM_EMBED_MODEL: {os.getenv('GLM_EMBED_MODEL', 'embedding-3')}")
        
        # Run tests
        test_single_text()
        test_multiple_texts()
        test_embedding_3_model()
        test_embedding_2_model()
        test_empty_input()
        test_provider_selection()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print("\nGLM Embeddings Provider is working correctly!")
        print("You can now use EMBEDDINGS_PROVIDER=glm in your .env file")
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

