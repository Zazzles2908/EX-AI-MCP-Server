"""Direct SDK test to see if SDK works at all"""
import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# Load .env
load_dotenv()

# Test with z.ai base URL
print("Testing SDK with z.ai base URL...")
api_key = os.getenv("GLM_API_KEY")
print(f"API key loaded: {api_key[:10]}..." if api_key else "No API key!")

client = ZhipuAI(
    api_key=api_key,
    base_url="https://api.z.ai/api/paas/v4"
)

print("Calling SDK with long prompt...")
long_prompt = "Analyze this code: " + ("x" * 8000)  # 8000+ chars like the real call
try:
    response = client.chat.completions.create(
        model="glm-4.5-flash",
        messages=[{"role": "user", "content": long_prompt}],
        temperature=0.2,
        stream=False
    )
    print(f"✅ SUCCESS! Response length: {len(response.choices[0].message.content)} chars")
    print(f"Response preview: {response.choices[0].message.content[:100]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

