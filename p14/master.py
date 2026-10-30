import socketserver
data, slaves = {}, []
class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            p = line.decode().strip().split(" ", 2)
            if p[0] == "SLAVE":
                self.wfile.write("".join(f"SET {k} {v}\n" for k, v in data.items()).encode())
                slaves.append(self.wfile)
            elif p[0] == "SET" and len(p) == 3:
                data[p[1]] = p[2]
                for s in slaves[:]:
                    try:
                        s.write(f"SET {p[1]} {p[2]}\n".encode())
                    except Exception:
                        slaves.remove(s)
                self.wfile.write(b"OK\n")
                print(f"[MASTER] SET {p[1]}={p[2]}", flush=True)
            elif p[0] == "GET" and len(p) > 1:
                self.wfile.write(f"{data.get(p[1], '(kosong)')}\n".encode())
            else:
                self.wfile.write(b"ERROR: pakai 'SET key value' atau 'GET key'\n")

socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True
print("[MASTER] berjalan di port 3000", flush=True)
socketserver.ThreadingTCPServer(("", 3000), Handler).serve_forever()