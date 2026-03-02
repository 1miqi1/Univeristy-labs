import socket
import time
import datetime

VISITOR_COUNT = 0

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

def generate_response(content, status_code="200 OK"):
    header = f"HTTP/1.1 {status_code}\r\n"
    header += "Content-Type: text/html\r\n"
    # TODO: Calculate Content-Length (It is crucial!)
    # header += f"Content-Length: {???}\r\n"
    header += f"Content-Length: {len(content)}\r\n"
    
    header += "\r\n" # The blank line
    response_str = header + content
    return response_str.encode('utf-8')

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
        time.sleep(5)
        
        client_connection, client_address = server_socket.accept()
        
        print(f"Connection received!")
        start_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(f">>> New Connection started at: {start_time}")

        # Receive raw bytes (buffer size 1024)
        request_data = client_connection.recv(1024).decode('utf-8')
        print(f"--- Received Request ---\n{request_data}\n------------------------")
        
        path = parse_request(request_data)
        
        if path == "/":
            VISITOR_COUNT += 1
            response = generate_response(f"<h1>Hello from Python! Count: {VISITOR_COUNT}</h1>")
        elif path == "/favicon.ico":
            response = generate_response("<h1>404 Not Found</h1>", status_code=404)
        else:
            response = generate_response(content="",status_code=404)
                

        client_connection.sendall(response)
        
        # Close connection immediately (for now)
        end_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"<<< Finished request at: {end_time}\n")
        client_connection.close()

if __name__ == '__main__':
    start_server()