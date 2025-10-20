import socket

# Test raw TCP connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect(('localhost', 8079))
    print("TCP connection successful!")
    
    # Send HTTP upgrade request
    request = (
        "GET / HTTP/1.1\r\n"
        "Host: localhost:8079\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    s.sendall(request.encode())
    print("Sent WebSocket upgrade request")
    
    # Receive response
    response = s.recv(4096)
    print(f"Response: {response.decode()}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    s.close()

