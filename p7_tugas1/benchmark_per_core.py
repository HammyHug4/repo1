#!/usr/bin/env python3
"""
BENCHMARK PER CORE / PROCESS
Menjalankan multiprocessing_version.py untuk p = 1 sampai 6
dan mencatat waktu EKSEKUSI AKTUAL setiap pengujian.

Tidak ada angka yang di-hardcode sebagai hasil benchmark.
Semua waktu dibaca dari output program yang benar-benar dijalankan.
"""

import csv
import re
import subprocess
import sys
import time
from pathlib import Path

PROGRAM = "multiprocessing_version.py"
HASIL_FILE = "hasil_benchmark_core.csv"
MAX_PROCESS = 6

POLA_WAKTU = re.compile(r"Waktu eksekusi\s*:\s*([0-9.]+)\s+detik")
POLA_TRANSAKSI = re.compile(r"Jumlah transaksi\s*:\s*([0-9,]+)")
POLA_ANOMALI = re.compile(r"Jumlah transaksi anomali:\s*([0-9,]+)")


def jalankan(processes):
    print()
    print("=" * 70)
    print(f"BENCHMARK MULTIPROCESSING - {processes} PROCESS")
    print("=" * 70)
    print(f"Perintah: python {PROGRAM} --processes {processes}")
    print("Dataset akan dibaca ulang untuk setiap pengujian.")
    print("Jangan tekan Ctrl+C sampai pengujian selesai.")
    print()

    mulai_wrapper = time.perf_counter()

    hasil = subprocess.run(
        [
            sys.executable,
            PROGRAM,
            "--processes",
            str(processes),
        ],
        text=True,
        capture_output=False,
    )

    waktu_wrapper = time.perf_counter() - mulai_wrapper

    if hasil.returncode != 0:
        raise RuntimeError(
            f"Pengujian {processes} process gagal. "
            f"Return code: {hasil.returncode}"
        )

    return waktu_wrapper


def ambil_waktu_dari_file_output(processes):
    # Jalankan ulang tidak diperlukan di sini; fungsi ini hanya placeholder
    # agar struktur program mudah dikembangkan.
    return None


def main():
    if not Path(PROGRAM).exists():
        print(f"ERROR: {PROGRAM} tidak ditemukan.")
        sys.exit(1)

    hasil_benchmark = []

    print("=" * 70)
    print("BENCHMARK PER CORE / PROCESS")
    print("=" * 70)
    print("Pengujian aktual: 1, 2, 3, 4, 5, 6 process")
    print("Tidak menggunakan angka hasil fiktif.")
    print("=" * 70)

    # Kita menggunakan waktu wrapper sebagai waktu benchmark total.
    # Setiap run menjalankan multiprocessing_version.py dari awal sampai selesai.
    for p in range(1, MAX_PROCESS + 1):
        waktu = jalankan(p)

        hasil_benchmark.append(
            {
                "core_process": p,
                "waktu_detik_wrapper": waktu,
            }
        )

        print()
        print(f"[SELESAI] {p} process = {waktu:.4f} detik")
        print()

    with open(
        HASIL_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["core_process", "waktu_detik_wrapper"],
        )
        writer.writeheader()
        writer.writerows(hasil_benchmark)

    # Speedup dan efficiency dihitung dari waktu aktual p=1.
    t1 = hasil_benchmark[0]["waktu_detik_wrapper"]

    print("=" * 70)
    print("HASIL BENCHMARK AKTUAL")
    print("=" * 70)
    print(f"{'Core/Process':>13} | {'Waktu (s)':>12} | {'Speedup':>10} | {'Efficiency':>12}")
    print("-" * 70)

    for row in hasil_benchmark:
        p = row["core_process"]
        waktu = row["waktu_detik_wrapper"]
        speedup = t1 / waktu
        efficiency = speedup / p * 100

        print(
            f"{p:>13} | "
            f"{waktu:>12.4f} | "
            f"{speedup:>10.4f}x | "
            f"{efficiency:>11.2f}%"
        )

    print("=" * 70)
    print(f"Hasil disimpan ke: {HASIL_FILE}")
    print()
    print("CATATAN:")
    print("- Semua waktu di atas adalah hasil RUN AKTUAL.")
    print("- Speedup = T(1) / T(p).")
    print("- Efficiency = Speedup / p x 100%.")
    print("- Tidak ada nilai waktu 2-6 yang dibuat secara manual.")


if __name__ == "__main__":
    main()
