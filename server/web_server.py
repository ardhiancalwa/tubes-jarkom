import socket
import threading
import time
import os
import sys
from datetime import datetime

HOST = '0.0.0.0'
HTTP_PORT = 8000
UDP_PORT = 9000
ROOT = os.path.join(os.path.dirname(__file__), '')

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


def make_404_response(body_bytes):
    return b"HTTP/1.1 404 Not Found\r\nContent-Length: " + str(len(body_bytes)).encode() + b"\r\n\r\n" + body_bytes


def _parse_request_path(request_line):
    parts = request_line.split()
    return parts[1] if len(parts) > 1 else '/'


def _get_file_path(path):
    if path == '/':
        return os.path.join(ROOT, 'index.html')
    return os.path.join(ROOT, path.lstrip('/'))


def _get_content_type(filepath):
    if filepath.endswith('.html'):
        return 'text/html'
    elif filepath.endswith('.css'):
        return 'text/css'
    elif filepath.endswith('.js'):
        return 'application/javascript'
    elif filepath.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return 'image/jpeg'
    return 'application/octet-stream'


def handle_tcp_client(conn, addr):
    start = time.time()
    try:
        data = conn.recv(4096).decode('utf-8', errors='ignore')
        request_line = data.splitlines()[0] if data else ''
        print(f"[HTTP] {addr} -> {request_line}")
        
        path = _parse_request_path(request_line)
        filepath = _get_file_path(path)
        
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                body = f.read()
            content_type = _get_content_type(filepath)
            resp = make_http_response(body, content_type)
            size = len(body)
        else:
            body = b"<h1>404 Not Found</h1>"
            resp = make_404_response(body)
            size = len(body)
        
        conn.sendall(resp)
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
        payload = b"echo:" + data
        s.sendto(payload, addr)

if __name__ == '__main__':
    mode = 'threaded' if len(sys.argv) < 2 or sys.argv[1] != 'single' else 'single'
    threading.Thread(target=udp_echo_server, daemon=True).start()
    tcp_server(mode=mode)
