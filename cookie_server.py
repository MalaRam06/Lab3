# Simple HTTP server using raw sockets with cookie management

import socket

HOST = "localhost"
PORT = 8080

# Store sessions in memory
sessions = {}

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server running on {HOST}:{PORT}")

while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")

    request = client_socket.recv(1024).decode()
    print("Request:")
    print(request)

    # Parse Cookie header if present
    lines = request.split("\r\n")
    cookie_value = None
    for line in lines:
        if line.startswith("Cookie:"):
            parts = line.split(":")[1].strip().split("=")
            if len(parts) == 2 and parts[0] == "session_id":
                cookie_value = parts[1]

    # Generate response
    if cookie_value and cookie_value in sessions:
        message = f"Welcome back, {sessions[cookie_value]}!"
    else:
        # First-time visitor, assign new session
        cookie_value = "User123"
        sessions[cookie_value] = "Guest"
        message = "Hello, new visitor!"
    
    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Type: text/html\r\n"
    if not cookie_value in sessions or "Hello" in message:
        # Set cookie only for new visitor
        response += f"Set-Cookie: session_id={cookie_value}\r\n"
    response += "\r\n"
    response += f"<html><body><h1>{message}</h1></body></html>"

    # Send response
    client_socket.sendall(response.encode())
    client_socket.close()
