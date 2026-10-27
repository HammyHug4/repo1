import threading
import time

resource_lock = threading.Lock()


def thread_1_worker():
    print("Thread 1: Meminta Lock...")
    resource_lock.acquire()
    print("Thread 1: Berhasil memegang lock! (Sedang bekerja selama 3 detik...)")
    try:
        time.sleep(3.0)
    finally:
        resource_lock.release()
        print("Thread 1: Lock dilepaskan.")


def thread_2_worker():
    time.sleep(0.1)

    print("Thread 2: Meminta Lock...")
    if not resource_lock.acquire(blocking=False):
        print("Thread 2: Gagal! (Lock sedang dipegang Thread lain)")

    print("Thread 2: Tidur 1 detik... (Mengalah)")
    time.sleep(1.0)

    print("Thread 2: Meminta Lock lagi...")
    if not resource_lock.acquire(blocking=False):
        print("Thread 2: Gagal lagi! (Resource sibuk)")


def thread_3_worker():
    time.sleep(0.1)

    print("Thread 3: Meminta Lock...")
    if not resource_lock.acquire(blocking=False):
        print("Thread 3: Gagal! (Lock sedang dipegang Thread lain)")

    print("Thread 3: Tidur 1 detik... (Mengalah)")
    time.sleep(1.0)

    print("Thread 3: Meminta Lock lagi...")
    if not resource_lock.acquire(blocking=False):
        print("Thread 3: Gagal lagi! (Resource sibuk)")


if __name__ == "__main__":
    # Menjalankan thread sesuai diagram
    t1 = threading.Thread(target=thread_1_worker, name="T1")
    t2 = threading.Thread(target=thread_2_worker, name="T2")
    t3 = threading.Thread(target=thread_3_worker, name="T3")

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    print("Simulasi selesai.")