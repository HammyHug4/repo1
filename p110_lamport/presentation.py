import os
import xmlrpc.client
from lamport import LamportClock

clock = LamportClock("PRESENTATION")

server = xmlrpc.client.ServerProxy(
    f"http://{os.environ.get('APP_HOST', 'application')}:8000/",
    allow_none=True
)

def panggil(nama_rpc, *args):
    print(f"\n--- Lamport trace: {nama_rpc} ---", flush=True)
    ts = clock.kirim("application")
    resp = getattr(server, nama_rpc)(ts, *args)
    clock.terima("application", resp["ts"])
    print("--- selesai ---", flush=True)
    return resp["hasil"]

while True:
    print("\n=== APLIKASI ===")
    print("1. Tampilkan semua user")
    print("2. Cari user berdasarkan ID")
    print("3. Tambah user")
    print("4. Hapus user")
    print("5. Keluar")

    try:
        pilihan = input("Pilih menu: ")
    except EOFError:
        break

    try:
        if pilihan == "1":
            users = panggil("tampilkan_users")

            for user in users:
                print(user)

        elif pilihan == "2":
            user_id = int(input("Masukkan ID: "))
            user = panggil("cari_user", user_id)

            print(user if user else "User tidak ditemukan")

        elif pilihan == "3":
            user_id = int(input("ID: "))
            nama = input("Nama: ")
            umur = int(input("Umur: "))

            hasil = panggil("tambah_user", user_id, nama, umur)

            if hasil:
                print("User berhasil ditambahkan")
            else:
                print("ID sudah digunakan")

        elif pilihan == "4":
            user_id = int(input("ID yang akan dihapus: "))
            hasil = panggil("hapus_user", user_id)

            if hasil:
                print("User berhasil dihapus")
            else:
                print("User tidak ditemukan")

        elif pilihan == "5":
            print("Program selesai.")
            break

        else:
            print("Pilihan tidak valid.")

    except ConnectionRefusedError:
        print("Koneksi gagal. Pastikan kedua server aktif.")

    except Exception as e:
        print("Terjadi kesalahan:", e)
