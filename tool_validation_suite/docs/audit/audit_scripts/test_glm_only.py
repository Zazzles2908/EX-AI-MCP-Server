"""Quick test for GLM analyze tool only"""
import sys
sys.path.insert(0, 'tool_validation_suite')

from utils.mcp_client import MCPClient

def test_glm_analyze():
    """Test analyze tool with GLM model"""
    print("\n" + "="*60)
    print("Testing analyze tool with GLM...")
    print("="*60)
    
    client = MCPClient()
    
    arguments = {
        "step": "Analyze the provided code for potential improvements",
        "step_number": 1,
        "total_steps": 1,
        "next_step_required": False,
        "findings": "Initial code review requested",
        "relevant_files": ["tool_validation_suite/fixtures/sample_code.py"],
        "model": "glm-4.5-flash"
    }
    
    try:
        result = client.call_tool("analyze", arguments)
        print(f"\n✅ Test PASSED!")
        print(f"Result length: {len(str(result))} chars")
        print(f"Result preview: {str(result)[:500]}...")
        return True
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_glm_analyze()
    sys.exit(0 if success else 1)

