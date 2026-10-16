#!/usr/bin/env python3
"""
STEP 4 - Threading / Concurrency
Tugas 1 - Sistem Terdistribusi dan Komputasi Paralel

Memproses transaksi_2gb.csv menggunakan beberapa thread.

Library:
- csv
- os
- time
- threading
- concurrent.futures

Tidak menggunakan pandas/numpy/library pihak ketiga.

PENTING:
- Aturan deteksi sama persis dengan sequential.py.
- Dataset tidak dimuat 2 GB sekaligus ke RAM.
- File dibagi berdasarkan posisi byte, lalu setiap thread membaca bagian
  file masing-masing.
- Default menggunakan 4 thread.
"""

import argparse
import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor


FILE_DATASET = "transaksi_2gb.csv"

BATAS_JUMLAH_EKSTREM = 1000
BATAS_HARGA_EKSTREM = 50_000_000

JENIS_ANOMALI = (
    "jumlah_nol",
    "jumlah_negatif",
    "harga_negatif",
    "total_salah",
    "jumlah_ekstrem",
    "harga_ekstrem",
    "duplikat_transaksi",
)


def nomor_id(id_transaksi):
    """TRX000000123 -> 123."""
    return int(id_transaksi[3:])


def cek_anomali(row, id_terbesar):
    """Memeriksa tujuh aturan anomali."""
    anomali = []

    id_transaksi = row["id_transaksi"]
    jumlah = int(row["jumlah"])
    harga_satuan = int(row["harga_satuan"])
    total = int(row["total"])

    id_sekarang = nomor_id(id_transaksi)

    if jumlah == 0:
        anomali.append("jumlah_nol")

    if jumlah < 0:
        anomali.append("jumlah_negatif")

    if harga_satuan < 0:
        anomali.append("harga_negatif")

    if total != jumlah * harga_satuan:
        anomali.append("total_salah")

    if jumlah > BATAS_JUMLAH_EKSTREM:
        anomali.append("jumlah_ekstrem")

    if harga_satuan > BATAS_HARGA_EKSTREM:
        anomali.append("harga_ekstrem")

    # Karena ID normal dibuat menaik, ID yang kembali ke nilai yang
    # lebih kecil/sama dari ID terbesar yang sudah dibaca adalah duplikat.
    if id_terbesar is not None and id_sekarang <= id_terbesar:
        anomali.append("duplikat_transaksi")

    return anomali, id_sekarang


def cari_batas_chunk(ukuran_file, jumlah_thread):
    """
    Membagi file berdasarkan byte.

    Setiap thread mendapat [awal, akhir).
    Batas akhir tidak harus tepat di akhir baris karena worker akan
    mengabaikan baris pertama/terakhir yang terpotong.
    """
    ukuran_chunk = ukuran_file // jumlah_thread
    batas = []

    for i in range(jumlah_thread):
        awal = i * ukuran_chunk
        akhir = ukuran_file if i == jumlah_thread - 1 else (i + 1) * ukuran_chunk
        batas.append((awal, akhir))

    return batas


def baca_id_sebelum_posisi(path, posisi):
    """
    Mendapatkan ID terbesar/ID terakhir yang valid sebelum posisi byte.

    Fungsi ini hanya dipakai untuk menentukan konteks duplikat di awal
    setiap chunk. Data utama tetap diproses oleh thread.
    """
    if posisi <= 0:
        return None

    with open(path, "rb") as file:
        file.seek(posisi)

        # Posisi berada di tengah baris. Buang sisa baris tersebut.
        file.readline()

        # Baca satu baris lengkap setelah posisi.
        # Kita sebenarnya membutuhkan ID sebelum posisi, sehingga cara
        # yang lebih aman adalah mencari newline sebelumnya dengan
        # membaca blok kecil dari belakang.
        probe_start = max(0, posisi - 4096)
        file.seek(probe_start)
        data = file.read(posisi - probe_start)

        if not data:
            return None

        # Cari newline terakhir sebelum posisi.
        idx = data.rfind(b"\n")
        if idx == -1:
            return None

        baris_sebelum = data[:idx].splitlines()
        if not baris_sebelum:
            return None

        # Jika posisi tepat setelah newline, baris terakhir dari blok
        # adalah baris sebelum posisi.
        try:
            teks = baris_sebelum[-1].decode("utf-8")
            id_transaksi = teks.split(",", 1)[0]
            if id_transaksi == "id_transaksi":
                return None
            return nomor_id(id_transaksi)
        except (UnicodeDecodeError, ValueError):
            return None


def proses_chunk(args):
    """
    Worker thread.

    args = (nomor_thread, path, awal, akhir, id_terbesar_awal)
    """
    nomor_thread, path, awal, akhir, id_terbesar_awal = args

    hasil = {
        "baris": 0,
        "anomali": 0,
        "per_jenis": {jenis: 0 for jenis in JENIS_ANOMALI},
    }

    id_terbesar = id_terbesar_awal

    with open(
        path,
        "r",
        newline="",
        encoding="utf-8",
        buffering=1024 * 1024,
    ) as file:

        file.seek(awal)

        # Chunk selain chunk pertama mungkin dimulai di tengah baris.
        if awal > 0:
            file.readline()

        while True:
            posisi_sekarang = file.tell()

            if posisi_sekarang >= akhir:
                break

            baris = file.readline()

            if not baris:
                break

            # Jangan menggunakan header sebagai data.
            if baris.startswith("id_transaksi,"):
                continue

            row_values = next(csv.reader([baris]))

            if len(row_values) != 10:
                continue

            row = {
                "id_transaksi": row_values[0],
                "jumlah": row_values[5],
                "harga_satuan": row_values[6],
                "total": row_values[7],
            }

            hasil["baris"] += 1

            jenis_anomali, id_sekarang = cek_anomali(
                row,
                id_terbesar,
            )

            if jenis_anomali:
                hasil["anomali"] += 1

                for jenis in jenis_anomali:
                    hasil["per_jenis"][jenis] += 1

            if id_terbesar is None or id_sekarang > id_terbesar:
                id_terbesar = id_sekarang

    return nomor_thread, hasil


def buat_argumen_worker(path, batas):
    """
    Menentukan ID konteks sebelum setiap chunk.

    Karena dataset generator membuat ID transaksi menaik dan hanya
    menyisipkan duplikat, ID terbesar tepat sebelum awal chunk dapat
    diperoleh dari area sebelum batas tersebut.
    """
    args = []

    for i, (awal, akhir) in enumerate(batas):
        if i == 0:
            id_awal = None
        else:
            id_awal = baca_id_sebelum_posisi(path, awal)

        args.append((i + 1, path, awal, akhir, id_awal))

    return args


def proses_threading(jumlah_thread):
    if not os.path.exists(FILE_DATASET):
        print(f"ERROR: File '{FILE_DATASET}' tidak ditemukan.")
        print("Pastikan threading_version.py berada satu folder dengan transaksi_2gb.csv.")
        return

    if jumlah_thread < 1:
        print("ERROR: jumlah thread minimal 1.")
        return

    ukuran_file = os.path.getsize(FILE_DATASET)

    print("=" * 65)
    print("THREADING - DETEKSI ANOMALI")
    print("=" * 65)
    print(f"Dataset : {FILE_DATASET}")
    print(f"Ukuran  : {ukuran_file / 1_000_000_000:.4f} GB")
    print(f"Thread  : {jumlah_thread}")
    print()

    batas = cari_batas_chunk(ukuran_file, jumlah_thread)
    worker_args = buat_argumen_worker(FILE_DATASET, batas)

    waktu_mulai = time.perf_counter()

    with ThreadPoolExecutor(max_workers=jumlah_thread) as executor:
        hasil_workers = list(executor.map(proses_chunk, worker_args))

    waktu_selesai = time.perf_counter()
    waktu_eksekusi = waktu_selesai - waktu_mulai

    # Gabungkan hasil thread secara deterministik.
    hasil_workers.sort(key=lambda x: x[0])

    jumlah_baris = 0
    jumlah_anomali = 0
    jumlah_per_jenis = {jenis: 0 for jenis in JENIS_ANOMALI}

    for _, hasil in hasil_workers:
        jumlah_baris += hasil["baris"]
        jumlah_anomali += hasil["anomali"]

        for jenis in JENIS_ANOMALI:
            jumlah_per_jenis[jenis] += hasil["per_jenis"][jenis]

    print("=" * 65)
    print("HASIL")
    print("=" * 65)
    print(f"Jumlah transaksi        : {jumlah_baris:,}")
    print(f"Jumlah transaksi anomali: {jumlah_anomali:,}")
    print()
    print("Rincian anomali:")

    for jenis in JENIS_ANOMALI:
        print(f"  {jenis:22s}: {jumlah_per_jenis[jenis]:,}")

    print()
    print(f"Jumlah thread : {jumlah_thread}")
    print(f"Waktu eksekusi : {waktu_eksekusi:.4f} detik")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(
        description="Deteksi anomali transaksi menggunakan threading."
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Jumlah thread. Default: 4."
    )

    args = parser.parse_args()
    proses_threading(args.threads)


if __name__ == "__main__":
    main()
