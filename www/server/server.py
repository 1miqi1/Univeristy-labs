import os
import socket
import threading
import datetime
import time
from urllib.parse import unquote_plus


VISITOR_COUNT = 0
lock = threading.Lock()

MIME_TYPES = {
    ".html": "text/html",
    ".css":  "text/css",
    ".js":   "application/javascript",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".ico":  "image/x-icon",
}

def parse_post_body(request_data):
    # The body is separated from headers by a blank line
    parts = request_data.split("\r\n\r\n", 1)
    if len(parts) < 2:
        return {}
    body = parts[1]
    # TODO: Split body by '&', then each pair by '='.
    # Apply unquote_plus() to both key and value — browsers encode
    # spaces as '+' and special chars as %XX (e.g. "Hello+World%21").
    # Return a dict like {"name": "Alice", "email": "..."}
    cells = body.split('&')
    pairs = [cell.split('=') for cell in cells]
    
    
    out = [[unquote_plus(pair[0]), unquote_plus(pair[1])] for pair in pairs]
    
    return dict(out)


def read_file(path):
    public_root = os.path.abspath("public")
    abs_path    = os.path.abspath(os.path.join("public", path.lstrip("/")))

    # 🔒 Security: reject paths that escape public/
    if not abs_path.startswith(public_root + os.sep):
        return b"<h1>403 Forbidden</h1>", "403 Forbidden", "text/html"

    ext  = os.path.splitext(abs_path)[1].lower()
    mime = MIME_TYPES.get(ext, "application/octet-stream")

    try:
        with open(abs_path, "rb") as f:   # binary mode works for text AND images
            return f.read(), "200 OK", mime
    except FileNotFoundError:
        return b"<h1>404 Not Found</h1>", "404 Not Found", "text/html"

def generate_response(content, status, mime="text/html"):
    if isinstance(content, str):
        content = content.encode()
    response_line    = f"HTTP/1.1 {status}\r\n"
    response_headers = f"Content-Type: {mime}\r\nContent-Length: {len(content)}\r\n\r\n"
    return response_line.encode() + response_headers.encode() + content


def parse_request(request_data):
    if not request_data:
        return ""
    
    # TODO: Split the string into lines
    lines = request_data.split("\n")
    
    # TODO: Take the first line ("GET / HTTP/1.1")
    parts = lines[0].split(" ")
    
    # TODO: Split by spaces and return the middle part ("/")
    path = parts[1]

    return path


def handle_client(client_connection):
    global VISITOR_COUNT
    # Receive raw bytes (buffer size 1024)
    request_data = client_connection.recv(1024).decode('utf-8')
    print(f"--- Received Request ---\n{request_data}\n------------------------")
    
    
    path = parse_request(request_data)
    
    if path == '/submit':
        path = '/confirmation.html'
        submitted = parse_post_body(request_data)
        
    content, status, mime = read_file(path if path != "/" else "/index.html")
    
    
    response = generate_response(content, status, mime)
    client_connection.sendall(response)
    client_connection.close()

def start_server():
    global VISITOR_COUNT
    
    # 1. Create a socket object (IPv4, TCP)
    # AF_INET = IPv4, SOCK_STREAM = TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow the port to be reused immediately (prevents "Address already in use" errors)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # TODO: Bind the socket to 'localhost' and port 8000
    # Hint: bind() takes a tuple: ('host', port)
    server_socket.bind(('localhost', 8000))
    
    # TODO: Start listening for connections (backlog of 5)
    server_socket.listen(5)
    
    
    print("Server running on http://localhost:8000 ...")
    
    while True:
        # TODO: Accept a new connection
        # client_connection, client_address = ...
        
        client_connection, client_address = server_socket.accept()
        
        print(f"Connection received!")
        start_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(f">>> New Connection started at: {start_time}")
        
        
        threading.Thread(
            target=handle_client,
            args=(client_connection,),
        ).start()

if __name__ == '__main__':  
    start_server()