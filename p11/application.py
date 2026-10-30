from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

database = xmlrpc.client.ServerProxy(
    "http://database:8004/",
    allow_none=True
)

def tampilkan_users():
    return database.get_all()

def cari_user(user_id):
    return database.get_by_id(user_id)

def tambah_user(user_id, nama, umur):
    return database.insert(user_id, nama, umur)

def hapus_user(user_id):
    return database.delete(user_id)

server = SimpleXMLRPCServer(
    ("0.0.0.0", 8000),
    allow_none=True
)

server.register_function(tampilkan_users, "tampilkan_users")
server.register_function(cari_user, "cari_user")
server.register_function(tambah_user, "tambah_user")
server.register_function(hapus_user, "hapus_user")

print("Application Server berjalan di port 8000", flush=True)
server.serve_forever()
