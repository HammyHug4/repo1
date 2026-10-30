import threading
from xmlrpc.server import SimpleXMLRPCServer

users = {
    1: {"id": 1, "nama": "Andi", "umur": 20},
    2: {"id": 2, "nama": "Budi", "umur": 22},
}

db_lock = threading.Lock()

def get_all():
  with db_lock:
    return list(users.values())

def get_by_id(user_id):
  with db_lock:
    return users.get(user_id)

def insert(user_id, nama, umur):
  with db_lock:
    if user_id in users:
      return False

    users[user_id] = {"id": user_id, "nama": nama, "umur": umur}
    return True

def delete(user_id):
  with db_lock:
    if user_id not in users:
      return False

    del users[user_id]
    return True

server = SimpleXMLRPCServer(("0.0.0.0", 8004), allow_none=True)
server.register_function(get_all, "get_all")
server.register_function(get_by_id, "get_by_id")
server.register_function(insert, "insert")
server.register_function(delete, "delete")

print("Database Tier aktif di port 8004", flush=True)
server.serve_forever()
