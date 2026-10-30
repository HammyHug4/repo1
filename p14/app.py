import socket, socketserver, threading, time

NODES = ["peer1", "peer2"]
name = socket.gethostname()
peers = [n for n in NODES if n != name]
data = {}

def terapkan(k, v, ts, asal):
    if k not in data or (ts, asal) > data[k][1:]:
        data[k] = (v, ts, asal)
        return True

def kirim(peer, line):
    try:
        with socket.create_connection((peer, 3000), timeout=2) as s:
            s.sendall((line + "\n").encode())
    except OSError:
        pass

def repl(rest):
    k, ts, asal, v = rest.split(" ", 3)
    if terapkan(k, v, float(ts), asal):
        print(f"[{name}] replikasi {k}={v} dari {asal}", flush=True)

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            cmd, _, rest = line.decode().strip().partition(" ")
            if cmd == "SET" and " " in rest:
                k, v = rest.split(" ", 1)
                ts = time.time()
                terapkan(k, v, ts, name)
                for p in peers:
                    threading.Thread(target=kirim, args=(p, f"REPL {k} {ts} {name} {v}")).start()
                self.wfile.write(b"OK\n")
                print(f"[{name}] SET {k}={v}", flush=True)
            elif cmd == "GET":
                self.wfile.write(f"{data.get(rest, ('(kosong)',))[0]}\n".encode())
            elif cmd == "REPL":
                repl(rest)
            elif cmd == "SYNC":
                self.wfile.write("".join(f"REPL {k} {ts} {a} {v}\n" for k, (v, ts, a) in data.items()).encode())
            else:
                self.wfile.write(b"ERROR: pakai 'SET key value' atau 'GET key'\n")

def sync(peer):
    while True:
        try:
            with socket.create_connection((peer, 3000), timeout=2) as s:
                s.sendall(b"SYNC\n")
                s.shutdown(socket.SHUT_WR)
                for line in s.makefile():
                    repl(line.strip().split(" ", 1)[1])
            return
        except OSError:
            time.sleep(2)

for p in peers:
    threading.Thread(target=sync, args=(p,), daemon=True).start()
socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True
print(f"[{name}] berjalan di port 3000, peers: {peers}", flush=True)
socketserver.ThreadingTCPServer(("", 3000), Handler).serve_forever()