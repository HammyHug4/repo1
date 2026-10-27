import threading
import time
import random

resource_lock = threading.Lock()


def worker(nama_thread, backoff_detik=None):
    print(f"{nama_thread}: Meminta Lock...")

    if not resource_lock.acquire(blocking=False):
        print(f"{nama_thread}: Meminta Lock... Gagal! (Resource sibuk)")

        waktu_tunggu = backoff_detik if backoff_detik else random.uniform(0.2, 1.5)
        print(
            f"{nama_thread}: Tidur selama {waktu_tunggu:.1f} detik "
            f"(Randomized Backoff)..."
        )
        time.sleep(waktu_tunggu)

        print(f"{nama_thread}: Bangun dan Meminta Lock lagi...")
        while not resource_lock.acquire(blocking=False):
            time.sleep(0.1)

    print(f"{nama_thread}: Berhasil memegang lock!")
    try:
        time.sleep(0.3)
    finally:
        resource_lock.release()
        print(f"{nama_thread}: Selesai & Lepas Lock.")


if __name__ == "__main__":
    def thread_1_owner():
        print("Thread 1: Meminta Lock...")
        resource_lock.acquire()
        print("Thread 1: Berhasil memegang lock!")
        try:
            time.sleep(1.0)
        finally:
            resource_lock.release()
            print("Thread 1: Selesai & Lepas Lock.")

    t1 = threading.Thread(target=thread_1_owner, name="T1")
    t2 = threading.Thread(
        target=worker,
        args=("Thread 2", 0.3)
    )  # T2 bangun cepat
    t3 = threading.Thread(
        target=worker,
        args=("Thread 3", 1.2)
    )  # T3 bangun lama

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    print("\nSimulasi selesai dengan sukses!")