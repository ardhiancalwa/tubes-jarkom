# Proxy Server TCP/UDP dengan cache dan error handling

# Simple Proxy Server (TCP/UDP, cache, error, log)
import socket, threading, os
HOST, TCP_PORT, UDP_PORT = '0.0.0.0', 8080, 9090
WS_IP, WS_TCP, WS_UDP = '127.0.0.1', 8000, 9000
LOG = 'log/proxyserver.log'
os.makedirs('log', exist_ok=True)
cache = {}

def log(s,d,p,c,z,t):
    with open(LOG,'a') as x: x.write(f"{s} {d} {p} {c} {z} {t:.4f}\n")

def tcp():
    s = socket.socket()
    s.bind((HOST, TCP_PORT))
    s.listen(10)
    print(f"TCP {TCP_PORT}")
    while True:
        c,a = s.accept()
        threading.Thread(target=handle_tcp, args=(c,a), daemon=True).start()

def handle_tcp(conn, addr):
    req = conn.recv(4096)
    k = req.decode(errors='ignore').split()[0] if req else ''
    if k in cache:
        r, status = cache[k], 'HIT'
    else:
        try:
            ws = socket.create_connection((WS_IP, WS_TCP), timeout=5)
            ws.sendall(req)
            r = ws.recv(4096)
            ws.close()
            cache[k] = r
            status = 'MISS'
        except:
            r = b"HTTP/1.1 502\r\n\r\n502"
            status = 'ERR'
    conn.sendall(r)
    log(addr[0], WS_IP, 'TCP', status, len(r), 0)
    conn.close()

def udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, UDP_PORT))
    print(f"UDP {UDP_PORT}")
    while True:
        d,a = s.recvfrom(4096)
        ws = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ws.sendto(d, (WS_IP, WS_UDP))
        try:
            ws.settimeout(2)
            r,_ = ws.recvfrom(4096)
            s.sendto(r,a)
            status = 'FWD'
        except:
            status = 'ERR'
        log(a[0], WS_IP, 'UDP', status, len(d), 0)
        ws.close()

if __name__=='__main__':
    threading.Thread(target=udp, daemon=True).start()
    tcp()
