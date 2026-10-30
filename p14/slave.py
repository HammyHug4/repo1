import socket, socketserver, threading, time
data = {}
def sync():
    while True:
        try:
            with socket.create_connection(("master", 3000)) as s:
                s.sendall(b"SLAVE\n")
                for line in s.makefile():
                    _, k, v = line.strip().split(" ", 2)
                    data[k] = v
                    print(f"[SLAVE] replikasi {k}={v}", flush=True)
        except OSError:
            pass
        time.sleep(2)

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            p = line.decode().strip().split(" ", 2)
            if p[0] == "GET" and len(p) > 1:
                self.wfile.write(f"{data.get(p[1], '(kosong)')}\n".encode())
            else:
                self.wfile.write(b"ERROR: slave read-only, hanya GET\n")

threading.Thread(target=sync, daemon=True).start()
socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True
print("[SLAVE] berjalan di port 3000", flush=True)
socketserver.ThreadingTCPServer(("", 3000), Handler).serve_forever()