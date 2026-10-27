# import xmlrpc.client

# proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

# no_rek = "12345"
# print(f"Meminta pengecekan saldo untuk rekening: {no_rek} via RPC...")

# # Memanggil fungsi di server seolah-olah fungsi lokal
# hasil_saldo = proxy.cek_saldo(no_rek)

# print(f"Hasil dari Server - Saldo Anda: Rp {hasil_saldo:,}")


import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

no_rek = "12345"

print("=== SISTEM BANK RPC ===")
print("1. Cek saldo")
print("2. Setor saldo")

pilihan = input("Pilih menu (1/2): ")

if pilihan == "1":
    hasil_saldo = proxy.cek_saldo(no_rek)

    if isinstance(hasil_saldo, int):
        print(f"Saldo Anda: Rp {hasil_saldo:,}")
    else:
        print(hasil_saldo)

elif pilihan == "2":
    jumlah = int(input("Masukkan jumlah setoran: Rp "))

    hasil = proxy.setor_saldo(no_rek, jumlah)

    if isinstance(hasil, dict):
        print(hasil["pesan"])
        print(f"Saldo setelah setor: Rp {hasil['saldo']:,}")
    else:
        print(hasil)

else:
    print("Pilihan tidak valid.")
