import asyncio
import websockets
import json
import uuid

async def test_chat():
    uri = 'ws://127.0.0.1:8765'
    try:
        # Connect with auth token
        async with websockets.connect(uri, additional_headers={'Authorization': 'Bearer test-token-12345'}) as ws:
            # Send hello message first
            hello_msg = {
                'jsonrpc': '2.0',
                'id': str(uuid.uuid4()),
                'method': 'hello',
                'params': {}
            }
            await ws.send(json.dumps(hello_msg))
            hello_response = await ws.recv()
            print('✅ Hello sent')

            # Initialize
            init_msg = {
                'jsonrpc': '2.0',
                'id': str(uuid.uuid4()),
                'method': 'initialize',
                'params': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {},
                    'clientInfo': {'name': 'test-client', 'version': '1.0.0'}
                }
            }
            await ws.send(json.dumps(init_msg))
            response = await ws.recv()
            print('✅ Connected successfully')
            
            # Call chat tool
            chat_msg = {
                'jsonrpc': '2.0',
                'id': str(uuid.uuid4()),
                'method': 'tools/call',
                'params': {
                    'name': 'chat',
                    'arguments': {
                        'prompt': 'Based on the MCP file handling analysis, what is the recommended approach for handling file uploads from MCP clients? Answer in 2 sentences.',
                        'model': 'kimi-k2-0905-preview',
                        'thinking_mode': 'high',
                        'use_websearch': True
                    }
                }
            }
            await ws.send(json.dumps(chat_msg))
            print('📤 Chat request sent, waiting for response...')
            
            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=60)
            result = json.loads(response)
            print('\n=== CHAT RESPONSE ===')
            if 'result' in result:
                content = result['result'].get('content', [])
                for item in content:
                    if item.get('type') == 'text':
                        print(item.get('text', ''))
            else:
                print('❌ Error:', result.get('error', 'Unknown error'))
    except Exception as e:
        print(f'❌ Error: {type(e).__name__}: {e}')

if __name__ == '__main__':
    asyncio.run(test_chat())

