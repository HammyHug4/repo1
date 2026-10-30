import socket, socketserver, threading, time, sys, os, json

NODES = ["peer1", "peer2"]
name = socket.gethostname()
peers = [n for n in NODES if n != name]

DATA_FILE = f"app/p13/data_{name}.json"

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        data = {}
else:
    data = {}

def simpan_ke_disk():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"[{name}] Gagal menyimpan data ke disk: {e}", flush=True)

IS_PARTITIONED = "--partition" in sys.argv or os.environ.get("PARTITION") == "true"

def terapkan(k, v, ts, asal):
    if k not in data or (ts, asal) > tuple(data[k][1:]):
        data[k] = [v, ts, asal]
        simpan_ke_disk()
        return True
    return False

def kirim(peer, line):
    if IS_PARTITIONED:
        return
    try:
        with socket.create_connection((peer, 3000), timeout=2) as s:
            s.sendall((line + "\n").encode())
    except OSError:
        pass

def repl(rest):
    if IS_PARTITIONED:
        return
    parts = rest.split(" ", 3)
    if len(parts) == 4:
        k, ts, asal, v = parts
        if terapkan(k, v, float(ts), asal):
            print(f"[{name}] [AP Mode] Replikasi sukses: {k}={v} dari {asal}", flush=True)

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            cmd, _, rest = line.decode().strip().partition(" ")
            if cmd == "SET" and " " in rest:
                k, v = rest.split(" ", 1)
                ts = time.time()
                terapkan(k, v, ts, name)
                if not IS_PARTITIONED:
                    for p in peers:
                        threading.Thread(target=kirim, args=(p, f"REPL {k} {ts} {name} {v}")).start()
                    print(f"[{name}] SET {k}={v} berhasil diproses dan disebar.", flush=True)
                    self.wfile.write(b"OK (Disimpan & Disebar)\n")
                else:
                    print(f"[{name}] [PARTITIONED] SET {k}={v} disimpan lokal. Gagal sebar karena terisolasi.", flush=True)
                    self.wfile.write(b"OK (Disimpan secara lokal - Terisolasi / AP Mode)\n")
                
            elif cmd == "GET":
                item = data.get(rest)
                val = item[0] if item else "(kosong)"
                status = " [Data Lokal / Stale - Terisolasi]" if IS_PARTITIONED else " [Data Sinkron]"
                self.wfile.write(f"{val}{status}\n".encode())
                
            elif cmd == "REPL":
                if not IS_PARTITIONED:
                    repl(rest)
            elif cmd == "SYNC":
                if not IS_PARTITIONED:
                    sync_data = "".join(f"REPL {k} {ts} {a} {v}\n" for k, (v, ts, a) in data.items())
                    self.wfile.write(sync_data.encode())
            else:
                self.wfile.write(b"ERROR: pakai 'SET key value' atau 'GET key'\n")

def sync(peer):
    while True:
        if IS_PARTITIONED:
            time.sleep(2)
            continue
        try:
            with socket.create_connection((peer, 3000), timeout=2) as s:
                s.sendall(b"SYNC\n")
                s.shutdown(socket.SHUT_WR)
                for line in s.makefile():
                    if not IS_PARTITIONED:
                        line_str = line.strip()
                        if line_str.startswith("REPL "):
                            repl(line_str.split(" ", 1)[1])
            return
        except OSError:
            time.sleep(2)

for p in peers:
    threading.Thread(target=sync, args=(p,), daemon=True).start()

socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True

status_str = " [TERISOLASI / PARTITIONED]" if IS_PARTITIONED else " [NORMAL]"
print(f"[{name}]{status_str} berjalan di port 3000, peers: {peers}", flush=True)
socketserver.ThreadingTCPServer(("", 3000), Handler).serve_forever()