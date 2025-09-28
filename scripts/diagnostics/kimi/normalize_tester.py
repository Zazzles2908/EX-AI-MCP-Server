import asyncio
import json
import uuid
import websockets

URI = "ws://127.0.0.1:8765"

async def call_kimi_chat_with_tools(messages):
    rid = uuid.uuid4().hex
    payload = {
        "op": "call_tool",
        "request_id": rid,
        "name": "kimi_chat_with_tools",
        "arguments": {"messages": messages, "model": "kimi-k2-0711-preview", "stream": False},
    }
    async with websockets.connect(URI) as ws:
        await ws.send(json.dumps({"op": "hello"}))
        await ws.recv()
        await ws.send(json.dumps(payload))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("op") == "call_tool_res" and msg.get("request_id") == rid:
                return msg

async def main():
    cases = [
        ("empty list", []),
        ("list with empty string", [""]),
        ("list with whitespace", ["   "]),
        ("dict empty content", [{"role":"user","content":""}]),
        ("dict whitespace content", [{"role":"user","content":"   "}]),
        ("mixed valid+empty", ["", {"role":"user","content":"Hello"}, "   "]),
        ("single valid string", "Hello world"),
    ]
    for name, msgs in cases:
        res = await call_kimi_chat_with_tools(msgs)
        print("CASE:", name)
        print(json.dumps(res, ensure_ascii=False)[:500])
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())

