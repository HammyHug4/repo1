# from xmlrpc.server import SimpleXMLRPCServer


# def cek_saldo(nomor_rekening):
#     database_rekening = {
#         "12345": 5500000,
#         "67890": 1250000
#     }
#     return database_rekening.get(
#         str(nomor_rekening),
#         "Rekening tidak ditemukan"
#     )


# server = SimpleXMLRPCServer(
#     ("localhost", 8000),
#     allow_none=True
# )
# print("Server Bank RPC berjalan di port 8000...")
# server.register_function(cek_saldo, "cek_saldo")
# server.serve_forever()


from xmlrpc.server import SimpleXMLRPCServer

database_rekening = {
    "12345": 5500000,
    "67890": 1250000
}


def cek_saldo(nomor_rekening):
    return database_rekening.get(
        str(nomor_rekening),
        "Rekening tidak ditemukan"
    )


def setor_saldo(nomor_rekening, jumlah):
    nomor_rekening = str(nomor_rekening)

    if nomor_rekening not in database_rekening:
        return "Rekening tidak ditemukan"

    if not isinstance(jumlah, int) or isinstance(jumlah, bool) or jumlah <= 0:
        return "Jumlah setor harus berupa bilangan bulat positif"

    database_rekening[nomor_rekening] += jumlah

    return {
        "status": "berhasil",
        "pesan": "Setor tunai berhasil",
        "saldo": database_rekening[nomor_rekening]
    }


server = SimpleXMLRPCServer(
    ("localhost", 8000),
    allow_none=True
)

server.register_function(cek_saldo, "cek_saldo")
server.register_function(setor_saldo, "setor_saldo")

print("Server Bank RPC berjalan di port 8000...")
server.serve_forever()
