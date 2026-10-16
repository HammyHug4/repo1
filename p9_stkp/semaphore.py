
import threading
import time

kuota_download = threading.Semaphore(2)


def download_file(nama_file):
    print(f"{nama_file} masuk antrean...")
    kuota_download.acquire()
    # --- CRITICAL SECTION START ---
    print(f"[MULAI] {nama_file} sedang didownload...")
    time.sleep(2)
    print(f"[SELESAI] {nama_file} berhasil diunduh.")
    # --- CRITICAL SECTION END ---
    kuota_download.release()


t1 = threading.Thread(target=download_file, args=("Thread 1: Film_A.mp4",))
t2 = threading.Thread(target=download_file, args=("Thread 2: Lagu_B.mp3",))
t3 = threading.Thread(target=download_file, args=("Thread 3: Tugas_C.pdf",))
t4 = threading.Thread(target=download_file, args=("Thread 4: Game_D.zip",))

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()

print("Semua proses download selesai.")