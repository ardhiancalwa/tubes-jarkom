# server/web_server.py
import socket, threading, time, os
from datetime import datetime

HOST = '0.0.0.0'
HTTP_PORT = 8000
UDP_PORT = 9000
ROOT = os.path.join(os.path.dirname(__file__), '')

# Simple HTTP response builder
def make_http_response(body_bytes, content_type='text/html'):
    header = (
        "HTTP/1.1 200 OK\r\n"
        f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Content-Type: {content_type}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return header.encode('utf-8') + body_bytes

def handle_tcp_client(conn, addr):
    start = time.time()
    try:
        data = conn.recv(4096).decode('utf-8', errors='ignore')
        request_line = data.splitlines()[0] if data else ''
        print(f"[HTTP] {addr} -> {request_line}")
        # Very simple parsing: GET /path
        parts = request_line.split()
        path = parts[1] if len(parts) > 1 else '/'
        if path == '/':
            filepath = os.path.join(ROOT, 'index.html')
        else:
            filepath = os.path.join(ROOT, path.lstrip('/'))
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                body = f.read()
            content_type = 'text/html' if filepath.endswith('.html') else 'application/octet-stream'
            resp = make_http_response(body, content_type)
            conn.sendall(resp)
            size = len(body)
        else:
            body = b"<h1>404 Not Found</h1>"
            resp = b"HTTP/1.1 404 Not Found\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body
            conn.sendall(resp)
            size = len(body)
        elapsed = time.time() - start
        print(f"[HTTP] {addr[0]} {path} => {size} bytes in {elapsed:.3f}s")
    except Exception as e:
        print("[HTTP] error:", e)
    finally:
        conn.close()

def tcp_server(mode='threaded'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, HTTP_PORT))
    s.listen(5)
    print(f"[HTTP] Listening {HOST}:{HTTP_PORT} mode={mode}")
    while True:
        conn, addr = s.accept()
        if mode == 'single':
            handle_tcp_client(conn, addr)
        else:
            t = threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True)
            t.start()

def udp_echo_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, UDP_PORT))
    print(f"[UDP] Echo listening on {HOST}:{UDP_PORT}")
    while True:
        data, addr = s.recvfrom(65535)
        t = time.time()
        print(f"[UDP] recv {len(data)} bytes from {addr} at {t}")
        # Echo back with timestamp
        payload = b"echo:" + data
        s.sendto(payload, addr)

if __name__ == '__main__':
    import sys
    mode = 'threaded' if len(sys.argv) < 2 or sys.argv[1] != 'single' else 'single'
    # start UDP thread
    threading.Thread(target=udp_echo_server, daemon=True).start()
    tcp_server(mode=mode)
