"""
Test script to discover available models on z.ai endpoint

This script attempts to:
1. List available models
2. Test different embedding model names
3. Determine if z.ai supports embeddings at all
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

from zai import ZaiClient

def test_list_models():
    """Try to list available models"""
    print("\n" + "="*80)
    print("TEST: List Available Models")
    print("="*80)
    
    api_key = os.getenv("GLM_API_KEY")
    base_url = "https://api.z.ai/api/paas/v4"
    
    client = ZaiClient(api_key=api_key, base_url=base_url)
    
    try:
        # Try to list models
        models = client.models.list()
        print(f"✅ Available models:")
        for model in models.data:
            print(f"  - {model.id}")
    except Exception as e:
        print(f"❌ Failed to list models: {e}")


def test_embedding_model_names():
    """Try different embedding model name variations"""
    print("\n" + "="*80)
    print("TEST: Try Different Embedding Model Names")
    print("="*80)
    
    api_key = os.getenv("GLM_API_KEY")
    base_url = "https://api.z.ai/api/paas/v4"
    
    client = ZaiClient(api_key=api_key, base_url=base_url)
    
    # Try different model name variations
    model_names = [
        "embedding-2",
        "embedding-3",
        "Embedding-2",
        "Embedding-3",
        "text-embedding-2",
        "text-embedding-3",
        "glm-embedding-2",
        "glm-embedding-3",
        "zhipu-embedding-2",
        "zhipu-embedding-3",
    ]
    
    test_text = "Hello, world!"
    
    for model_name in model_names:
        try:
            print(f"\nTrying model: {model_name}")
            response = client.embeddings.create(
                model=model_name,
                input=[test_text]
            )
            print(f"✅ SUCCESS with model: {model_name}")
            print(f"   Embedding dimensions: {len(response.data[0].embedding)}")
            return  # Stop on first success
        except Exception as e:
            error_msg = str(e)
            if "Unknown Model" in error_msg or "模型不存在" in error_msg:
                print(f"❌ Model not found: {model_name}")
            else:
                print(f"❌ Error with {model_name}: {error_msg}")


def test_bigmodel_endpoint():
    """Test if bigmodel.cn endpoint works"""
    print("\n" + "="*80)
    print("TEST: Try bigmodel.cn Endpoint")
    print("="*80)
    
    api_key = os.getenv("GLM_API_KEY")
    base_url = "https://open.bigmodel.cn/api/paas/v4"
    
    client = ZaiClient(api_key=api_key, base_url=base_url)
    
    model_names = ["embedding-2", "embedding-3"]
    test_text = "Hello, world!"
    
    for model_name in model_names:
        try:
            print(f"\nTrying model: {model_name} on bigmodel.cn")
            response = client.embeddings.create(
                model=model_name,
                input=[test_text]
            )
            print(f"✅ SUCCESS with model: {model_name}")
            print(f"   Embedding dimensions: {len(response.data[0].embedding)}")
            return  # Stop on first success
        except Exception as e:
            error_msg = str(e)
            if "Unknown Model" in error_msg or "模型不存在" in error_msg:
                print(f"❌ Model not found: {model_name}")
            else:
                print(f"❌ Error with {model_name}: {error_msg}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("Z.AI ENDPOINT MODEL DISCOVERY")
    print("Testing z.ai endpoint for embeddings support")
    print("="*80)
    
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("❌ ERROR: GLM_API_KEY not set in environment")
        sys.exit(1)
    
    print(f"✅ GLM_API_KEY: {api_key[:10]}...{api_key[-10:]}")
    
    # Run tests
    test_list_models()
    test_embedding_model_names()
    test_bigmodel_endpoint()
    
    print("\n" + "="*80)
    print("DISCOVERY COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()

