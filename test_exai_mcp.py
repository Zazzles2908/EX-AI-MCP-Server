#!/usr/bin/env python3
import asyncio
import websockets
import json
import uuid

async def test_exai():
    req_id = str(uuid.uuid4())
    try:
        async with websockets.connect('ws://localhost:8079/ws') as ws:
            # Hello handshake
            await ws.send(json.dumps({
                'op': 'hello',
                'session_id': 'cli-test',
                'token': 'test-token-12345'
            }))
            ack = json.loads(await ws.recv())
            print(f'✅ Hello: {ack.get("ok")}')

            # List tools
            await ws.send(json.dumps({'op': 'list_tools', 'request_id': req_id}))
            response = json.loads(await ws.recv())

            tools = response.get('tools', [])
            print(f'✅ Found {len(tools)} EXAI tools:')
            for i, tool in enumerate(tools[:5], 1):
                print(f'   {i}. {tool["name"]}')
            if len(tools) > 5:
                print(f'   ... and {len(tools) - 5} more')

            return True
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    result = asyncio.run(test_exai())
    exit(0 if result else 1)
