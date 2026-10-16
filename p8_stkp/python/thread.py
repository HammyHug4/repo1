
import time
import os
import threading
import psutil


def tugas_thread():
    for i in range(5):
        beban_cpu = sum(x for x in range(50_000_000))
        pid = os.getpid()
        tid = threading.get_native_id()
        core_id = psutil.Process().cpu_num()
        waktu_sekarang = time.strftime('%H:%M:%S', time.localtime())

        print(
            f"[{waktu_sekarang}] | PID: {pid} | TID: {tid} | "
            f"Core: {core_id} | Loop ke-{i} - Selesai menghitung beban!"
        )


if __name__ == "__main__":
    tugas_thread()
