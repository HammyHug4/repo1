import threading
import time

saldo_rekening = {
    "Rekening_A": 1000000,
    "Rekening_B": 500000,
    "Rekening_C": 750000
}

lock_a = threading.Lock()
lock_b = threading.Lock()
lock_c = threading.Lock()


def transfer_dana_1():
    print("Thread 1 (Transfer A -> B): Meminta kunci Rekening A...")
    lock_a.acquire()
    print("Thread 1 (Transfer A -> B): Berhasil mengunci Rekening A.")

    time.sleep(1)  # Simulasi jeda / proses verifikasi data

    print("Thread 1 (Transfer A -> B): Meminta kunci Rekening B...")
    lock_b.acquire()  # <--- DEADLOCK TERJADI DI SINI JIKA KUNCI SEDANG DIPEGANG THREAD 2
    print("Thread 1 (Transfer A -> B): Berhasil mengunci Rekening B.")

    # Proses Transfer (Critical Section)
    print("Thread 1: Melakukan transfer saldo A ke B...")

    # Melepaskan kunci
    lock_b.release()
    lock_a.release()
    print("Thread 1: Transfer selesai, kunci dilepaskan.")


def transfer_dana_2():
    """
    Worker 2: Transfer dari Rekening B ke Rekening C
    Urutan penguncian terbalik: Kunci Rekening B dulu, baru Rekening C
    (Catatan: Untuk memicu deadlock murni dengan Thread 1, kita buat
    Worker 2 memegang B dan meminta A, atau mensimulasikan persilangan akses ke Rekening B)
    """
    print("Thread 2 (Transfer B -> A): Meminta kunci Rekening B...")
    lock_b.acquire()
    print("Thread 2 (Transfer B -> A): Berhasil mengunci Rekening B.")

    time.sleep(1)  # Simulasi jeda

    print("Thread 2 (Transfer B -> A): Meminta kunci Rekening A...")
    lock_a.acquire()  # <--- DEADLOCK TERJADI DI SINI KARENA SALING TUNGGU DENGAN THREAD 1
    print("Thread 2 (Transfer B -> A): Berhasil mengunci Rekening A.")

    # Proses Transfer (Critical Section)
    print("Thread 2: Melakukan transfer saldo B ke A...")

    # Melepaskan kunci
    lock_a.release()
    lock_b.release()
    print("Thread 2: Transfer selesai, kunci dilepaskan.")


# Menjalankan dua thread transfer secara bersamaan
t1 = threading.Thread(target=transfer_dana_1)
t2 = threading.Thread(target=transfer_dana_2)

t1.start()
t2.start()

t1.join()
t2.join()

print("Semua proses transfer selesai (Baris ini tidak akan pernah tercetak karena Deadlock!).")