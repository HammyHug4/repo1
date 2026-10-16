import time
import os
import psutil

for i in range(5):
    beban_cpu = sum(x for x in range(50_000_000))
    pid = os.getpid()
    core_id = psutil.Process().cpu_num()
    waktu_sekarang = time.strftime('%H:%M:%S', time.localtime())
    print(f"[{waktu_sekarang}] | PID: {pid} | Core: {core_id} | Loop ke-{i} - Selesai menghitung beban!")
