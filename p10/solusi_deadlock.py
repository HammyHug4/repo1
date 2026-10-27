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

    time.sleep(1)

    print("Thread 1 (Transfer A -> B): Meminta kunci Rekening B...")
    lock_b.acquire()
    print("Thread 1 (Transfer A -> B): Berhasil mengunci Rekening B.")

    print("Thread 1: Melakukan transfer saldo A ke B...")
    saldo_rekening["Rekening_A"] -= 100000
    saldo_rekening["Rekening_B"] += 100000

    lock_b.release()
    lock_a.release()
    print("Thread 1: Transfer selesai, kunci dilepaskan.\n")


def transfer_dana_2():
    print("Thread 2 (Transfer B -> A): Meminta kunci Rekening A (di awal)...")
    lock_a.acquire()
    print("Thread 2 (Transfer B -> A): Berhasil mengunci Rekening A.")

    time.sleep(1)

    print("Thread 2 (Transfer B -> A): Meminta kunci Rekening B...")
    lock_b.acquire()
    print("Thread 2 (Transfer B -> A): Berhasil mengunci Rekening B.")

    print("Thread 2: Melakukan transfer saldo B ke A...")
    saldo_rekening["Rekening_B"] -= 50000
    saldo_rekening["Rekening_A"] += 50000

    lock_b.release()
    lock_a.release()
    print("Thread 2: Transfer selesai, kunci dilepaskan.\n")


t1 = threading.Thread(target=transfer_dana_1)
t2 = threading.Thread(target=transfer_dana_2)

t1.start()
t2.start()

t1.join()
t2.join()

print("Semua proses transfer selesai dengan aman tanpa Deadlock!")
print("Saldo Akhir:", saldo_rekening)
