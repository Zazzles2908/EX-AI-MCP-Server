import sys
import asyncio
sys.path.append('/app')
from tools.registry import get_tool_registry

async def test_chat():
    try:
        registry = get_tool_registry()
        chat_tool = registry.get_tool('chat')
        
        print('Testing chat tool with simple prompt...')
        
        # Test basic chat functionality
        result = await chat_tool.execute({
            'prompt': 'Hello, how are you?'
        })
        
        print(f'Chat result type: {type(result)}')
        if hasattr(result, 'content') and result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    try:
                        # Try to parse as JSON first
                        import json
                        parsed = json.loads(content.text)
                        if 'status' in parsed and parsed['status'] == 'error':
                            print(f'Chat error: {parsed.get("content", "Unknown error")}')
                        else:
                            print(f'Chat response: {content.text[:200]}...')
                    except:
                        print(f'Chat response: {content.text[:200]}...')
                else:
                    print(f'Content: {content}')
        else:
            print(f'Full result: {result}')
            
    except Exception as e:
        print(f'Chat tool execution failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat())