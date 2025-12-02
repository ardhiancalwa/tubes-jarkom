# Client QoS otomatis: latency, jitter, throughput, packet loss

# Simple Client QoS (latency, jitter, throughput, loss)
import socket, time, csv, os
PROXY, TCP, UDP = '127.0.0.1', 8080, 9090
N, SIZE, INT = 50, 256, 0.01
os.makedirs('log', exist_ok=True)

def udp_qos():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    lat, lost = [], 0
    for i in range(N):
        t0 = time.time()
        s.sendto(f'{i}'.encode().ljust(SIZE,b'x'), (PROXY, UDP))
        try:
            d,_ = s.recvfrom(SIZE+10)
            lat.append(time.time()-t0)
        except: lost+=1
        time.sleep(INT)
    s.close()
    thr = (N-lost)*SIZE/(sum(lat) if lat else 1)
    jit = (max(lat)-min(lat))*1000 if lat else 0
    loss = lost/N*100
    avg = sum(lat)/len(lat)*1000 if lat else 0
    print(f"UDP: Thr={thr:.1f}B/s Lat={avg:.1f}ms Loss={loss:.1f}% Jit={jit:.1f}ms")
    with open('log/client_qos.csv','w',newline='') as f:
        csv.writer(f).writerow([thr, avg, loss, jit])

def tcp_http():
    s = socket.socket()
    s.connect((PROXY, TCP))
    s.sendall(b'GET /index.html HTTP/1.1\r\n\r\n')
    r = s.recv(4096)
    print(f"TCP: {len(r)} bytes")
    s.close()

if __name__=='__main__':
    tcp_http()
    udp_qos()
