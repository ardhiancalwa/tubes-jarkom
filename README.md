# Tugas Besar Jaringan Komputer
## Implementasi Proxy Server, Socket Programming, dan Analisis QoS

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Deskripsi Proyek

Proyek ini mengimplementasikan sistem jaringan komputer lengkap yang terdiri dari **Web Server**, **Proxy Server**, dan **Client** menggunakan Socket Programming dengan bahasa Python. Sistem ini dirancang untuk mendemonstrasikan komunikasi jaringan menggunakan protokol TCP dan UDP, serta melakukan analisis Quality of Service (QoS) menggunakan Wireshark.

### Tujuan Pembelajaran
- Memahami konsep Socket Programming (TCP/UDP)
- Implementasi Proxy Server dengan mekanisme caching
- Pengukuran dan analisis QoS (Throughput, Latency, Jitter, Packet Loss)
- Multi-threading untuk menangani koneksi concurrent
- Network packet analysis menggunakan Wireshark

---

## 🏗️ Arsitektur Sistem

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Client    │ ◄─────► │ Proxy Server │ ◄─────► │ Web Server  │
│             │         │              │         │             │
│ TCP: 8080   │         │ TCP: 8080    │         │ TCP: 8000   │
│ UDP: 9090   │         │ UDP: 9090    │         │ UDP: 9000   │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │                        │
      │                   ┌────▼────┐                   │
      │                   │  Cache  │                   │
      │                   │  & Log  │                   │
      │                   └─────────┘                   │
      │                                                  │
      └──────────────────────┬───────────────────────────┘
                      ┌──────▼───────┐
                      │  Wireshark   │
                      │ QoS Analysis │
                      └──────────────┘
```

### Komponen Sistem

#### 1. **Web Server** (`web_server.py`)
- Menyediakan layanan HTTP pada port **8000** (TCP)
- Echo server UDP pada port **9000**
- Support single-thread dan multi-thread mode
- Melayani file statis (HTML, CSS, gambar)
- Logging otomatis untuk setiap request

#### 2. **Proxy Server** (`proxy_server.py`)
- Perantara antara Client dan Web Server
- TCP port **8080** untuk HTTP forwarding
- UDP port **9090** untuk QoS testing
- Mekanisme caching sederhana (HIT/MISS)
- Error handling (502 Bad Gateway, 504 Timeout)
- Multi-threading untuk concurrent connections

#### 3. **Client** (`client_qos.py`)
- Melakukan request HTTP ke Proxy
- Pengujian QoS melalui UDP
- Menghitung metrik: Throughput, Latency, Jitter, Packet Loss
- Export hasil ke CSV

#### 4. **Multi Client** (`multi_client.py`)
- Simulasi 5 client concurrent
- Stress testing untuk performa jaringan

---

## 🛠️ Requirements

### Software
- **Python 3.7+**
- **Wireshark** (untuk analisis packet)
- **Text Editor/IDE** (VS Code, PyCharm, dll)

### Hardware
- Minimal 2 laptop (untuk topologi 2 anggota)
- Optimal 3 laptop (untuk topologi 3 anggota)
- WiFi hotspot atau router

### Python Libraries
Semua library yang digunakan adalah built-in Python:
- `socket` - Socket programming
- `threading` - Multi-threading
- `time` - Time measurement
- `csv` - Export hasil QoS
- `os` - File operations

---

## 📦 Instalasi

### 1. Clone atau Download Project
```bash
git clone <repository-url>
cd tubes-jarkom
```

### 2. Struktur Direktori
```
tubes-jarkom/
├── web_server.py          # Web Server (TCP/UDP)
├── proxy_server.py        # Proxy Server dengan cache
├── client_qos.py          # Client QoS testing
├── multi_client.py        # Multiple client simulator
├── index.html             # Halaman HTML sample
├── log/                   # Folder untuk log files (auto-created)
│   ├── webserver.log
│   ├── proxyserver.log
│   └── client_qos.csv
└── README.md              # Dokumentasi ini
```

### 3. Persiapan Jaringan
1. Aktifkan WiFi hotspot dari HP atau gunakan router
2. Hubungkan semua laptop ke jaringan yang sama
3. Catat IP address masing-masing laptop:
   ```bash
   # Linux/Mac
   ifconfig
   
   # Windows
   ipconfig
   ```

---

## 🚀 Cara Menjalankan

### Topologi 3 Anggota (Recommended)

#### **Laptop A - Web Server**
```bash
# Mode Single-Thread
python web_server.py

# Mode Multi-Thread (Recommended untuk QoS testing)
python web_server.py --threaded
```

Output:
```
TCP 8000 threaded
UDP 9000
```

#### **Laptop B - Proxy Server**
**PENTING:** Edit `proxy_server.py` terlebih dahulu:
```python
WS_IP = '192.168.x.x'  # Ganti dengan IP Laptop A (Web Server)
```

Jalankan:
```bash
python proxy_server.py
```

Output:
```
TCP 8080
UDP 9090
```

#### **Laptop C - Client**

**PENTING:** Edit `client_qos.py` terlebih dahulu:
```python
PROXY = '192.168.x.x'  # Ganti dengan IP Laptop B (Proxy Server)
```

**Single Client Testing:**
```bash
python client_qos.py
```

**Multi Client Testing (5 concurrent clients):**
```bash
python multi_client.py
```

Output contoh:
```
TCP: 450 bytes
UDP: Thr=12800.5B/s Lat=15.3ms Loss=2.0% Jit=8.5ms
```

---

## 📊 Analisis QoS dengan Wireshark

### 1. Setup Wireshark di Laptop Proxy
```bash
# Jalankan Wireshark
sudo wireshark  # Linux/Mac
# atau buka dari aplikasi di Windows
```

### 2. Filter yang Berguna
```
# Filter semua traffic ke/dari Web Server
ip.addr == 192.168.x.x

# Filter hanya TCP traffic
tcp.port == 8080 || tcp.port == 8000

# Filter hanya UDP traffic  
udp.port == 9090 || udp.port == 9000

# Filter HTTP traffic
http
```

### 3. Metrik QoS yang Diukur

#### **Throughput** (Bytes/second)
- Kecepatan transfer data
- Formula: `Total Data / Total Time`

#### **Latency** (milliseconds)
- Waktu round-trip pengiriman paket
- Formula: `RTT = Time_received - Time_sent`

#### **Packet Loss** (%)
- Persentase paket yang hilang
- Formula: `(Lost_packets / Total_packets) × 100`

#### **Jitter** (milliseconds)
- Variasi delay antar paket
- Formula: `Max_latency - Min_latency`

### 4. Ekspor Hasil
Client otomatis menyimpan hasil QoS di:
```
log/client_qos.csv
```

Format: `Throughput, Latency, Packet_Loss, Jitter`

---

## 🔧 Konfigurasi Advanced

### Web Server Configuration
Edit `web_server.py`:
```python
HOST = '0.0.0.0'         # Listen on all interfaces
TCP_PORT = 8000          # HTTP port
UDP_PORT = 9000          # UDP echo port
HTML = 'index.html'      # Default HTML file
```

### Proxy Server Configuration
Edit `proxy_server.py`:
```python
HOST = '0.0.0.0'
TCP_PORT = 8080
UDP_PORT = 9090
WS_IP = '127.0.0.1'      # ⚠️ GANTI dengan IP Web Server
WS_TCP = 8000
WS_UDP = 9000
```

### Client QoS Configuration
Edit `client_qos.py`:
```python
PROXY = '127.0.0.1'      # ⚠️ GANTI dengan IP Proxy Server
TCP = 8080
UDP = 9090
N = 50                   # Jumlah paket UDP untuk testing
SIZE = 256               # Ukuran paket (bytes)
INT = 0.01               # Interval antar paket (seconds)
```

---

## 📝 Log Files

### Web Server Log (`log/webserver.log`)
Format: `IP File Size Time`
```
192.168.1.10 index.html 450 0.0023
192.168.1.10 UDP 256 0.0000
```

### Proxy Server Log (`log/proxyserver.log`)
Format: `Source Destination Protocol Status Size Time`
```
192.168.1.10 192.168.1.5 TCP HIT 450 0.0015
192.168.1.10 192.168.1.5 TCP MISS 450 0.0234
192.168.1.10 192.168.1.5 UDP FWD 256 0.0000
```

Status codes:
- `HIT` - Data dari cache
- `MISS` - Data dari Web Server
- `FWD` - UDP forwarded
- `ERR` - Error terjadi

### Client QoS Log (`log/client_qos.csv`)
```csv
12800.5,15.3,2.0,8.5
```
Format: `Throughput,Latency,Loss,Jitter`

---

## 🧪 Skenario Testing

### 1. Basic Connectivity Test
```bash
# Test HTTP request
curl http://<PROXY_IP>:8080/index.html

# Test dengan browser
http://<PROXY_IP>:8080/index.html
```

### 2. Single Client QoS Test
```bash
python client_qos.py
```
- Jalankan Wireshark di Proxy
- Capture selama 10-20 detik
- Analisis hasil

### 3. Multi Client Load Test
```bash
python multi_client.py
```
- Simulasi 5 client bersamaan
- Monitor performa Proxy dan Web Server
- Bandingkan QoS vs single client

### 4. Cache Performance Test
```bash
# Request pertama (MISS)
python client_qos.py

# Request kedua (HIT) - seharusnya lebih cepat
python client_qos.py
```

### 5. Browser Test
Buka di browser:
```
http://<PROXY_IP>:8080/index.html
```

---

## 🐛 Troubleshooting

### Problem: "Connection refused"
**Solusi:**
- Pastikan server sudah running
- Cek IP address sudah benar
- Cek firewall tidak blocking port
```bash
# Linux: Allow ports
sudo ufw allow 8000
sudo ufw allow 8080
sudo ufw allow 9000
sudo ufw allow 9090
```

### Problem: "Address already in use"
**Solusi:**
```bash
# Kill process yang menggunakan port
# Linux/Mac
sudo lsof -i :8000
sudo kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Problem: Packet Loss tinggi (>10%)
**Solusi:**
- Pindah lebih dekat ke router
- Gunakan WiFi 5GHz jika tersedia
- Kurangi jumlah concurrent clients
- Periksa koneksi jaringan lain

### Problem: Cache tidak berfungsi
**Solusi:**
- Pastikan request HTTP identik (termasuk headers)
- Cek log proxy untuk status HIT/MISS
- Restart proxy server untuk clear cache

### Problem: Wireshark tidak menangkap paket
**Solusi:**
- Pilih interface yang benar (WiFi/Ethernet)
- Jalankan dengan sudo/admin privileges
- Gunakan filter yang tepat

---

## 📈 Tips Optimasi Performa

1. **Gunakan Threading Mode** di Web Server untuk performa lebih baik
2. **Tuning Timeout** - Sesuaikan timeout di proxy (default 5 detik)
3. **Packet Size** - Ukuran paket optimal 256-512 bytes untuk QoS testing
4. **Network Optimization**:
   - Gunakan jaringan dedicated (tidak ada device lain)
   - Hindari streaming/download saat testing
   - Sinkronkan waktu antar laptop

---

## 📚 Referensi

### Socket Programming
- [Python Socket Documentation](https://docs.python.org/3/library/socket.html)
- [Real Python - Socket Programming](https://realpython.com/python-sockets/)

### Threading
- [Python Threading Guide](https://docs.python.org/3/library/threading.html)

### Wireshark
- [Wireshark User Guide](https://www.wireshark.org/docs/wsug_html_chunked/)
- [Display Filters Reference](https://www.wireshark.org/docs/dfref/)

### QoS Metrics
- RFC 2544 - Benchmarking Methodology
- ITU-T Y.1540 - IP Packet Transfer Performance

---