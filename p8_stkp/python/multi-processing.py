
import time
import os
import multiprocessing
import psutil


def tugas_proses(nama_proses):
    for i in range(5):
        beban_cpu = sum(x for x in range(50_000_000))
        pid = os.getpid()
        core_id = psutil.Process().cpu_num()
        waktu_sekarang = time.strftime('%H:%M:%S', time.localtime())

        print(
            f"[{waktu_sekarang}] | {nama_proses} | PID: {pid} | "
            f"Core: {core_id} | Loop ke-{i} - Selesai menghitung beban!"
        )


if __name__ == "__main__":
    p1 = multiprocessing.Process(
        target=tugas_proses, args=("Process-1",)
    )
    p2 = multiprocessing.Process(
        target=tugas_proses, args=("Process-2",)
    )

    p1.start()
    p2.start()

    p1.join()
    p2.join()

