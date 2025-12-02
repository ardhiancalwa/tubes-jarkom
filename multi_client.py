import threading
from client_qos import tcp_http, udp_qos
def run(): tcp_http(); udp_qos()
threads = [threading.Thread(target=run) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()