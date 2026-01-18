import socket

HOST = "127.0.0.1"
PORT = 5000

with socket.create_connection((HOST, PORT), timeout=10) as s:
    s.sendall(b"AUTH?\n")
    print("Server replied:", s.recv(1024).decode().strip())
