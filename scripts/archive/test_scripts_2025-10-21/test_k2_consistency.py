"""
K2 Model Calculation Consistency Test

SAFETY CRITICAL: Tests K2 models for calculation consistency.
User reported 9x difference in arc flash calculations (11.2 vs 1.22 cal/cm²).
Wrong PPE specification = potential FATALITIES.

This script tests all K2 models with the same calculation prompt to identify
which model is giving incorrect results.

Usage:
    python scripts/testing/test_k2_consistency.py

Models Tested:
    - kimi-k2-0905-preview
    - kimi-k2-turbo-preview
    - kimi-thinking-preview (K2-based thinking model)

Test Case:
    Arc flash calculation from user's test results
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.providers.kimi import KimiProvider
from src.providers.base import ProviderType


# Test prompt from user's experience (arc flash calculation)
TEST_PROMPT = """Calculate the incident energy for an arc flash with the following parameters:
- System voltage: 480V
- Bolted fault current: 25 kA
- Working distance: 18 inches
- Arc duration: 0.5 seconds

Provide the incident energy in cal/cm² and recommend appropriate PPE category."""


async def test_k2_model(model_name: str) -> dict:
    """Test a single K2 model with the calculation prompt."""
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print(f"{'='*60}")
    
    try:
        # Initialize Kimi provider
        provider = KimiProvider()
        
        # Prepare request
        messages = [
            {"role": "user", "content": TEST_PROMPT}
        ]
        
        # Call model
        print(f"Sending request to {model_name}...")
        response = await provider.chat_completion(
            model=model_name,
            messages=messages,
            temperature=0.0,  # Deterministic for calculations
            max_tokens=2048,
            stream=False
        )
        
        # Extract response
        content = response.get("content", "")
        
        print(f"\nResponse from {model_name}:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        # Try to extract incident energy value
        incident_energy = extract_incident_energy(content)
        
        return {
            "model": model_name,
            "success": True,
            "content": content,
            "incident_energy": incident_energy,
            "error": None
        }
        
    except Exception as e:
        print(f"\n❌ ERROR testing {model_name}: {e}")
        return {
            "model": model_name,
            "success": False,
            "content": None,
            "incident_energy": None,
            "error": str(e)
        }


def extract_incident_energy(content: str) -> str:
    """Extract incident energy value from response."""
    # Look for patterns like "11.2 cal/cm²" or "1.22 cal/cm²"
    import re
    
    # Pattern: number followed by cal/cm² or cal/cm2
    patterns = [
        r'(\d+\.?\d*)\s*cal/cm[²2]',
        r'incident energy[:\s]+(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*calories per square centimeter',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return "NOT FOUND"


async def main():
    """Run K2 consistency test."""
    print("="*60)
    print("K2 MODEL CALCULATION CONSISTENCY TEST")
    print("SAFETY CRITICAL: Arc Flash Calculation")
    print("="*60)
    
    # K2 models to test
    k2_models = [
        "kimi-k2-0905-preview",
        "kimi-k2-turbo-preview",
        "kimi-thinking-preview",  # K2-based thinking model
    ]
    
    # Test all models
    results = []
    for model in k2_models:
        result = await test_k2_model(model)
        results.append(result)
        await asyncio.sleep(1)  # Rate limiting
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY - K2 MODEL CONSISTENCY TEST")
    print("="*60)
    
    incident_energies = {}
    for result in results:
        model = result["model"]
        if result["success"]:
            energy = result["incident_energy"]
            incident_energies[model] = energy
            print(f"\n{model}:")
            print(f"  Incident Energy: {energy} cal/cm²")
            print(f"  Status: ✅ SUCCESS")
        else:
            print(f"\n{model}:")
            print(f"  Status: ❌ FAILED - {result['error']}")
    
    # Check for inconsistencies
    print("\n" + "="*60)
    print("CONSISTENCY ANALYSIS")
    print("="*60)
    
    unique_values = set(incident_energies.values())
    if len(unique_values) == 1:
        print("\n✅ ALL MODELS CONSISTENT")
        print(f"   All models returned: {list(unique_values)[0]} cal/cm²")
    else:
        print("\n🚨 INCONSISTENCY DETECTED!")
        print(f"   Found {len(unique_values)} different values:")
        for value in unique_values:
            models_with_value = [m for m, v in incident_energies.items() if v == value]
            print(f"   - {value} cal/cm²: {', '.join(models_with_value)}")
        
        print("\n⚠️  SAFETY CRITICAL: Different models giving different calculations!")
        print("   This could lead to incorrect PPE specification.")
    
    # Save results
    output_file = project_root / "scripts" / "testing" / "k2_consistency_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Full results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("KIMI_API_KEY"):
        print("❌ ERROR: KIMI_API_KEY not set in environment")
        print("   Please set KIMI_API_KEY in .env file")
        sys.exit(1)
    
    # Run test
    asyncio.run(main())

