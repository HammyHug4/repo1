
import os
import time
import threading
import multiprocessing
import psutil


def tugas_thread(nama_proses, nama_thread):
    for i in range(5):
        beban_cpu = sum(x for x in range(50_000_000))
        pid = os.getpid()
        tid = threading.get_native_id()
        core_id = psutil.Process().cpu_num()
        waktu_sekarang = time.strftime('%H:%M:%S', time.localtime())

        print(
            f"[{waktu_sekarang}] | {nama_proses} | {nama_thread} | "
            f"PID: {pid} | TID: {tid} | Core: {core_id} | "
            f"Loop ke-{i} - Selesai menghitung beban!"
        )
        time.sleep(3)


def worker_process(nama_proses):
    t1 = threading.Thread(
        target=tugas_thread,
        args=(nama_proses, "Thread-1")
    )
    t2 = threading.Thread(
        target=tugas_thread,
        args=(nama_proses, "Thread-2")
    )

    t1.start()
    t2.start()

    t1.join()
    t2.join()


if __name__ == "__main__":
    p1 = multiprocessing.Process(
        target=worker_process,
        args=("Process-1",)
    )
    p2 = multiprocessing.Process(
        target=worker_process,
        args=("Process-2",)
    )

    p1.start()
    p2.start()

    p1.join()
    p2.join()
