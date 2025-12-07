# server/proxy_server.py
import socket, threading, time
from collections import OrderedDict

HOST = '0.0.0.0'
TCP_PORT = 8080
UDP_PORT = 9090

# target web server (ubah sesuai IP server)
WEB_SERVER_IP = '127.0.0.1'
WEB_SERVER_HTTP_PORT = 8000
WEB_SERVER_UDP_PORT = 9000

CACHE = {}  # key: path, value: bytes
CACHE_MAX = 50

def tcp_worker(client_conn, client_addr):
    try:
        req = client_conn.recv(4096)
        first_line = req.decode('utf-8', errors='ignore').splitlines()[0] if req else ''
        print(f"[Proxy-TCP] {client_addr} -> {first_line}")
        # parse path simply
        try:
            path = first_line.split()[1]
        except:
            path = '/'
        # cache check (only for GET / simple)
        if path in CACHE:
            print("[Proxy] CACHE HIT", path)
            client_conn.sendall(CACHE[path])
            return
        # forward to web server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
            s2.settimeout(8)
            s2.connect((WEB_SERVER_IP, WEB_SERVER_HTTP_PORT))
            s2.sendall(req)
            resp = b''
            while True:
                chunk = s2.recv(4096)
                if not chunk:
                    break
                resp += chunk
        # store in cache (naive)
        if len(CACHE) >= CACHE_MAX:
            CACHE.pop(next(iter(CACHE)))  # evict oldest insertion
        CACHE[path] = resp
        client_conn.sendall(resp)
        print(f"[Proxy-TCP] forwarded {len(resp)} bytes")
    except socket.timeout:
        msg = b"HTTP/1.1 504 Gateway Timeout\r\nContent-Length:0\r\n\r\n"
        client_conn.sendall(msg)
    except Exception as e:
        print("[Proxy-TCP] error", e)
        try:
            client_conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length:0\r\n\r\n")
        except:
            pass
    finally:
        client_conn.close()

def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, TCP_PORT))
    s.listen(50)
    print(f"[Proxy-TCP] Listening on {HOST}:{TCP_PORT}")
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=tcp_worker, args=(conn, addr), daemon=True)
        t.start()

def udp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, UDP_PORT))
    print(f"[Proxy-UDP] Listening on {HOST}:{UDP_PORT}")
    while True:
        data, addr = s.recvfrom(65535)
        print(f"[Proxy-UDP] recv {len(data)} from {addr}, forward to server")
        # forward to web server UDP (no retransmission)
        s.sendto(data, (WEB_SERVER_IP, WEB_SERVER_UDP_PORT))

if __name__ == '__main__':
    threading.Thread(target=udp_server, daemon=True).start()
    tcp_server()
