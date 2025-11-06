#!/usr/bin/env python3
import socket

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    result = s.connect_ex(("127.0.0.1", 8079))
    s.close()
    if result == 0:
        print("SUCCESS: Port 8079 is LISTENING!")
        exit(0)
    else:
        print("FAILED: Port 8079 is NOT listening")
        exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
