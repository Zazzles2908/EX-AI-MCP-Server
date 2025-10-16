import json
from websocket import create_connection

def test_docker_daemon():
    uri = "ws://172.17.0.2:8079"

    ws = create_connection(uri, timeout=10)

    try:
        # Send hello
        ws.send(json.dumps({
            "op": "hello",
            "token": "test-token-12345"
        }))

        # Receive hello_ack
        response = ws.recv()
        print("Hello ACK:", response)

        # Call chat tool with a simple prompt
        ws.send(json.dumps({
            "op": "call_tool",
            "request_id": "test-123",
            "name": "chat_EXAI-WS",
            "arguments": {
                "prompt": "What is 2+2? Just give me the number."
            }
        }))

        # Receive call_tool_ack
        ack = ws.recv()
        print("Tool ACK:", ack)

        # Receive call_tool_res
        result = ws.recv()
        print("Tool Result:", result)

        result_data = json.loads(result)
        if result_data.get("content"):
            print("\n=== RESPONSE ===")
            print(result_data["content"][:500])  # First 500 chars
            print(f"\n=== LENGTH: {len(result_data['content'])} chars ===")
            print(f"=== FINISH REASON: {result_data.get('metadata', {}).get('finish_reason', 'unknown')} ===")
    finally:
        ws.close()

if __name__ == "__main__":
    test_docker_daemon()

