#!/usr/bin/env python3
import asyncio
import websockets
import json
import uuid

async def verify_tools():
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
            print(f'✓ Hello Ack: {ack.get("ok")}')

            # List tools
            await ws.send(json.dumps({'op': 'list_tools', 'request_id': req_id}))
            response = json.loads(await ws.recv())

            if 'tools' in response and len(response['tools']) >= 20:
                print(f'✅ VERIFIED: {len(response["tools"])} EXAI tools available')
                print(f'   Tools: {", ".join([t["name"] for t in response["tools"][:5]])} ...')
                return True
            else:
                print(f'❌ FAILED: Only {len(response.get("tools", []))} tools found')
                return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    result = asyncio.run(verify_tools())
    exit(0 if result else 1)
