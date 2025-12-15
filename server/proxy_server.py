import socket
import threading

HOST = '0.0.0.0'
TCP_PORT = 8080
UDP_PORT = 9090

WEB_SERVER_IP = '10.159.54.112'
WEB_SERVER_HTTP_PORT = 8000
WEB_SERVER_UDP_PORT = 9000

CACHE = {}  
CACHE_MAX = 50

def tcp_worker(client_conn, client_addr):
    try:
        req = client_conn.recv(4096)
        first_line = req.decode('utf-8', errors='ignore').splitlines()[0] if req else ''
        print(f"[Proxy-TCP] {client_addr} -> {first_line}")
        
        path = _parse_request_path(first_line)
        
        if path in CACHE:
            print("[Proxy] CACHE HIT", path)
            client_conn.sendall(CACHE[path])
            return
        
        resp = _forward_to_webserver(req)
        _cache_response(path, resp)
        client_conn.sendall(resp)
        print(f"[Proxy-TCP] forwarded {len(resp)} bytes")
        
    except socket.timeout:
        client_conn.sendall(b"HTTP/1.1 504 Gateway Timeout\r\nContent-Length:0\r\n\r\n")
    except Exception as e:
        print("[Proxy-TCP] error", e)
        try:
            client_conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length:0\r\n\r\n")
        except:
            pass
    finally:
        client_conn.close()

def _parse_request_path(first_line):
    try:
        return first_line.split()[1]
    except:
        return '/'

def _forward_to_webserver(req):
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
    return resp


def _cache_response(path, resp):
    if len(CACHE) >= CACHE_MAX:
        CACHE.pop(next(iter(CACHE)))
    CACHE[path] = resp


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
        _forward_udp_request(s, data, addr)

def _forward_udp_request(socket_obj, data, client_addr):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s2:
            s2.settimeout(2)
            s2.sendto(data, (WEB_SERVER_IP, WEB_SERVER_UDP_PORT))
            response, _ = s2.recvfrom(65535)
            socket_obj.sendto(response, client_addr)
            print(f"[Proxy-UDP] forwarded {len(response)} bytes back to {client_addr}")
    except socket.timeout:
        print(f"[Proxy-UDP] timeout waiting response from web server")
    except Exception as e:
        print(f"[Proxy-UDP] error: {e}")

if __name__ == '__main__':
    threading.Thread(target=udp_server, daemon=True).start()
    tcp_server()
