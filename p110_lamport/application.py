import os
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from lamport import LamportClock

clock = LamportClock("APPLICATION")

database = xmlrpc.client.ServerProxy(
    f"http://{os.environ.get('DB_HOST', 'database')}:8004/",
    allow_none=True
)

def panggil_database(nama_fungsi, *args):
    ts = clock.kirim("database")
    resp = getattr(database, nama_fungsi)(ts, *args)
    clock.terima("database", resp["ts"])
    return resp["hasil"]

def buat_handler(nama_rpc, fungsi_db):
    def handler(ts, *args):
        clock.terima("presentation", ts)
        hasil = panggil_database(fungsi_db, *args)
        ts_balas = clock.kirim("presentation")
        return {"ts": ts_balas, "hasil": hasil}
    return handler

server = SimpleXMLRPCServer(
    ("0.0.0.0", 8000),
    allow_none=True,
    logRequests=False
)

server.register_function(buat_handler("tampilkan_users", "get_all"), "tampilkan_users")
server.register_function(buat_handler("cari_user", "get_by_id"), "cari_user")
server.register_function(buat_handler("tambah_user", "insert"), "tambah_user")
server.register_function(buat_handler("hapus_user", "delete"), "hapus_user")

print("Application Server berjalan di port 8000", flush=True)
server.serve_forever()
