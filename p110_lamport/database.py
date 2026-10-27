from xmlrpc.server import SimpleXMLRPCServer
from lamport import LamportClock

clock = LamportClock("DATABASE")

users = {
    1: {"id": 1, "nama": "Andi", "umur": 20},
    2: {"id": 2, "nama": "Budi", "umur": 22},
}

def get_all():
    return list(users.values())

def get_by_id(user_id):
    return users.get(user_id)

def insert(user_id, nama, umur):
    if user_id in users:
        return False

    users[user_id] = {
        "id": user_id,
        "nama": nama,
        "umur": umur
    }
    return True

def delete(user_id):
    if user_id not in users:
        return False

    del users[user_id]
    return True

def dengan_lamport(fungsi):
    def wrapper(ts, *args):
        clock.terima("application", ts)
        hasil = fungsi(*args)
        ts_balas = clock.kirim("application")
        return {"ts": ts_balas, "hasil": hasil}
    return wrapper

server = SimpleXMLRPCServer(
    ("0.0.0.0", 8004),
    allow_none=True,
    logRequests=False
)

server.register_function(dengan_lamport(get_all), "get_all")
server.register_function(dengan_lamport(get_by_id), "get_by_id")
server.register_function(dengan_lamport(insert), "insert")
server.register_function(dengan_lamport(delete), "delete")

print("Database Tier aktif di port 8004", flush=True)
server.serve_forever()
