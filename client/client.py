# client/client.py
import socket, time, threading, csv, statistics
from datetime import datetime

# CONFIG: ubah sesuai topologi
PROXY_IP = '127.0.0.1'
PROXY_TCP_PORT = 8080
PROXY_UDP_PORT = 9090

SERVER_IP = '127.0.0.1'
SERVER_TCP_PORT = 8000
SERVER_UDP_PORT = 9000

def http_request_via_proxy(path='/', use_proxy=True):
    target_ip = PROXY_IP if use_proxy else SERVER_IP
    target_port = PROXY_TCP_PORT if use_proxy else SERVER_TCP_PORT
    req = f"GET {path} HTTP/1.1\r\nHost: example\r\nConnection: close\r\n\r\n".encode()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((target_ip, target_port))
        s.sendall(req)
        resp = b''
        while True:
            chunk = s.recv(4096)
            if not chunk: break
            resp += chunk
    # for browser mode you can save to file and open
    return resp

def udp_qos_test(target_ip, target_port, count=20, size=64, interval=0.05):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    seq = 0
    rtt_list = []
    received = 0
    send_times = {}
    for i in range(count):
        seq += 1
        payload = f"{seq}|{time.time()}".encode().ljust(size, b'.')
        send_times[seq] = time.time()
        s.sendto(payload, (target_ip, target_port))
        try:
            data, addr = s.recvfrom(65535)
            t = time.time()
            # try parse echoed seq
            parts = data.decode(errors='ignore').split('|')
            # fallback: compute rtt from stored send time
            rtt = t - send_times.get(seq, send_times[list(send_times.keys())[0]])
            rtt_list.append(rtt)
            received += 1
        except socket.timeout:
            # packet lost (no response)
            pass
        time.sleep(interval)
    s.close()
    lost = count - received
    loss_pct = (lost / count) * 100.0
    avg_latency = statistics.mean(rtt_list) if rtt_list else None
    jitter = statistics.pstdev(rtt_list) if len(rtt_list) > 1 else 0.0
    total_bytes = received * size
    duration = sum(rtt_list) if rtt_list else 0.000001
    throughput_bps = (total_bytes * 8) / duration if duration > 0 else 0
    # return metrics
    return {
        'sent': count, 'recv': received, 'loss_pct': loss_pct,
        'avg_latency_s': avg_latency, 'jitter_s': jitter, 'throughput_bps': throughput_bps
    }

def multi_client_http_sim(n_clients=5, use_proxy=True):
    results = []
    def worker(i):
        print(f"[CL-{i}] starting http request")
        resp = http_request_via_proxy('/', use_proxy=use_proxy)
        size = len(resp)
        print(f"[CL-{i}] got {size} bytes")
        results.append((i, size))
    threads = []
    for i in range(n_clients):
        t = threading.Thread(target=worker, args=(i+1,), daemon=True)
        threads.append(t); t.start()
    for t in threads: t.join()
    return results

def save_csv(filename, rows, header=None):
    with open(filename, 'w', newline='') as f:
        w = csv.writer(f)
        if header: w.writerow(header)
        w.writerows(rows)

if __name__ == '__main__':
    # Contoh: jalankan satu percobaan UDP ke proxy (yang meneruskan ke server)
    print("=== UDP QoS test via PROXY (9090) ===")
    metrics = udp_qos_test(PROXY_IP, PROXY_UDP_PORT, count=20, size=128, interval=0.05)
    print(metrics)
    # Simpan log csv singkat
    save_csv('qos_result.csv', [[k, v] for k, v in metrics.items()])
    # Contoh HTTP direct & via proxy
    print("=== HTTP via PROXY ===")
    r = http_request_via_proxy('/', use_proxy=True)
    print("len:", len(r))
    print("=== Multi-client HTTP (5 clients) via PROXY ===")
    multi_client_http_sim(5, use_proxy=True)
    print("Selesai.")
