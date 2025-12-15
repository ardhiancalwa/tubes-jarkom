import socket
import time
import threading
import csv
import statistics

PROXY_IP = '10.21.200.2'
PROXY_TCP_PORT = 8080
PROXY_UDP_PORT = 9090

SERVER_IP = '10.21.200.112'
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
        resp = _receive_all(s)
    
    return resp

def _receive_all(sock):
    data = b''
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data

def udp_qos_test(target_ip, target_port, count=20, size=64, interval=0.05):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)
    
    seq = 0
    rtt_list = []
    received = 0
    send_times = {}
    
    print(f"[QoS] Sending {count} packets to {target_ip}:{target_port}")
    
    for i in range(count):
        seq += 1
        payload = f"{seq}|{time.time()}".encode().ljust(size, b'.')
        send_times[seq] = time.time()
        
        try:
            s.sendto(payload, (target_ip, target_port))
        except Exception as e:
            print(f"[QoS] send error: {e}")
            continue
        
        try:
            data, addr = s.recvfrom(65535)
            t = time.time()
            rtt = _calculate_rtt(data, send_times, seq)
            
            if rtt > 0:
                rtt_list.append(rtt)
                received += 1
                print(f"[QoS] recv seq={seq} rtt={rtt*1000:.2f}ms")
        
        except socket.timeout:
            print(f"[QoS] timeout seq={seq}")
        except Exception as e:
            print(f"[QoS] recv error: {e}")
        
        time.sleep(interval)
    
    s.close()
    
    return _compute_qos_metrics(count, received, rtt_list, size)

def _calculate_rtt(data, send_times, seq):
    try:
        echo_seq = int(data.decode(errors='ignore').split('|')[0])
        rtt = time.time() - send_times.get(echo_seq, send_times[seq])
    except:
        rtt = time.time() - send_times[seq]
    
    return rtt

def _compute_qos_metrics(count, received, rtt_list, size):
    lost = count - received
    loss_pct = (lost / count) * 100.0 if count > 0 else 0
    
    if rtt_list:
        avg_latency = statistics.mean(rtt_list)
        jitter = statistics.pstdev(rtt_list) if len(rtt_list) > 1 else 0.0
        min_rtt = min(rtt_list)
        max_rtt = max(rtt_list)
    else:
        avg_latency = jitter = min_rtt = max_rtt = 0
    
    total_bytes = received * size
    duration = max(rtt_list) if rtt_list else 0.001
    throughput_bps = (total_bytes * 8) / duration if duration > 0 else 0
    
    return {
        'sent': count,
        'recv': received,
        'loss_pct': loss_pct,
        'avg_latency_ms': avg_latency * 1000,
        'min_latency_ms': min_rtt * 1000,
        'max_latency_ms': max_rtt * 1000,
        'jitter_ms': jitter * 1000,
        'throughput_kbps': throughput_bps / 1000
    }

def multi_client_http_sim(n_clients=5, use_proxy=True):
    results = []
    threads = []
    
    def worker(client_id):
        print(f"[CL-{client_id}] starting http request")
        resp = http_request_via_proxy('/', use_proxy=use_proxy)
        size = len(resp)
        print(f"[CL-{client_id}] got {size} bytes")
        results.append((client_id, size))
    
    for i in range(n_clients):
        t = threading.Thread(target=worker, args=(i + 1,), daemon=True)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    return results

def save_csv(filename, rows, header=None):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(rows)

if __name__ == '__main__':
    print("=== UDP QoS test via PROXY (9090) ===")
    metrics = udp_qos_test(PROXY_IP, PROXY_UDP_PORT, count=20, size=128, interval=0.05)
    print(metrics)
    save_csv('qos_result.csv', [[k, v] for k, v in metrics.items()])
    
    print("=== HTTP via PROXY ===")
    r = http_request_via_proxy('/', use_proxy=True)
    print("len:", len(r))
    
    print("=== Multi-client HTTP (5 clients) via PROXY ===")
    multi_client_http_sim(5, use_proxy=True)
    print("Selesai.")
