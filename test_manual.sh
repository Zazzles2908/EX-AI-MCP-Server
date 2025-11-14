#!/bin/bash
cd C:/Project/EX-AI-MCP-Server
python scripts/runtime/run_ws_shim.py &
SHIM_PID=$!
echo "Shim PID: $SHIM_PID"
sleep 3
echo "Sending initialize..."
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}'
sleep 2
echo "Sending initialized..."
echo '{"jsonrpc":"2.0","method":"notifications/initialized"}'
sleep 2
echo "Sending tools/list..."
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
sleep 5
kill $SHIM_PID 2>/dev/null
