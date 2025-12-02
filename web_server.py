# Web Server untuk TCP (HTTP) dan UDP (Echo)
# Mode: Single-threaded & Multi-threaded

# Simple Web Server (TCP/UDP, single/multi-thread)
import socket, threading, time, os
HOST, TCP_PORT, UDP_PORT = '0.0.0.0', 8000, 9000
HTML = 'index.html'
LOG = 'log/webserver.log'
os.makedirs('log', exist_ok=True)

def log(ip, f, sz, t):
    with open(LOG, 'a') as x: x.write(f"{ip} {f} {sz} {t:.4f}\n")

def handle(conn, addr):
    t0 = time.time()
    req = conn.recv(1024).decode()
    f = req.split()[1][1:] if req else HTML
    if not os.path.exists(f):
        r = "HTTP/1.1 404\r\n\r\n404".encode()
    else:
        r = b"HTTP/1.1 200\r\n\r\n" + open(f, 'rb').read()
    conn.sendall(r)
    log(addr[0], f, len(r), time.time()-t0)
    conn.close()

def tcp(mode):
    s = socket.socket()
    s.bind((HOST, TCP_PORT))
    s.listen(5)
    print(f"TCP {TCP_PORT} {mode}")
    while True:
        c,a = s.accept()
        if mode=='single': handle(c,a)
        else: threading.Thread(target=handle, args=(c,a), daemon=True).start()

def udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, UDP_PORT))
    print(f"UDP {UDP_PORT}")
    while True:
        d,a = s.recvfrom(4096)
        s.sendto(d,a)
        log(a[0], 'UDP', len(d), 0)

if __name__=='__main__':
    import sys
    threading.Thread(target=udp, daemon=True).start()
    tcp('threaded' if '--threaded' in sys.argv else 'single')
