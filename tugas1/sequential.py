#!/usr/bin/env python3
"""
STEP 3 - Sequential Murni
Tugas 1 - Sistem Terdistribusi dan Komputasi Paralel

Memproses transaksi_2gb.csv secara berurutan (baris demi baris)
untuk mendeteksi anomali.

Library yang digunakan hanya standard library Python.
Tidak menggunakan pandas/numpy/library pihak ketiga.

ATURAN ANOMALI:
1. jumlah == 0
2. jumlah < 0
3. harga_satuan < 0
4. total != jumlah * harga_satuan
5. jumlah > 1000
6. harga_satuan > 50.000.000
7. id_transaksi duplikat

CATATAN DUPLIKAT:
Dataset generator membuat ID transaksi normal secara berurutan.
Jika ID yang sedang dibaca lebih kecil atau sama dengan ID terbesar
yang sudah pernah dibaca, berarti ID tersebut muncul kembali.
Cara ini mendeteksi duplikat tanpa menyimpan jutaan ID dalam set,
sehingga lebih hemat RAM untuk dataset 2 GB.
"""

import csv
import os
import time


FILE_DATASET = "transaksi_2gb.csv"

# Batas anomali sesuai STEP 2.
BATAS_JUMLAH_EKSTREM = 1000
BATAS_HARGA_EKSTREM = 50_000_000


def nomor_id(id_transaksi):
    """
    Mengambil nomor dari ID transaksi.

    Contoh:
        TRX000000123 -> 123
    """
    return int(id_transaksi[3:])


def cek_anomali(row, id_terbesar):
    """
    Memeriksa satu transaksi berdasarkan 7 aturan anomali.

    Parameter:
        row          : data satu transaksi.
        id_terbesar  : nomor ID terbesar yang sudah pernah diproses.

    Return:
        (list_anomali, nomor_id_sekarang)
    """
    anomali = []

    id_transaksi = row["id_transaksi"]
    jumlah = int(row["jumlah"])
    harga_satuan = int(row["harga_satuan"])
    total = int(row["total"])

    id_sekarang = nomor_id(id_transaksi)

    # 1. Jumlah nol
    if jumlah == 0:
        anomali.append("jumlah_nol")

    # 2. Jumlah negatif
    if jumlah < 0:
        anomali.append("jumlah_negatif")

    # 3. Harga negatif
    if harga_satuan < 0:
        anomali.append("harga_negatif")

    # 4. Total tidak sesuai
    if total != jumlah * harga_satuan:
        anomali.append("total_salah")

    # 5. Jumlah ekstrem
    if jumlah > BATAS_JUMLAH_EKSTREM:
        anomali.append("jumlah_ekstrem")

    # 6. Harga ekstrem
    if harga_satuan > BATAS_HARGA_EKSTREM:
        anomali.append("harga_ekstrem")

    # 7. Duplikat transaksi
    #
    # ID normal pada dataset dibuat menaik.
    # Jika ID sekarang <= ID terbesar yang sudah pernah muncul,
    # berarti ID tersebut merupakan ID yang muncul kembali.
    if id_terbesar is not None and id_sekarang <= id_terbesar:
        anomali.append("duplikat_transaksi")

    return anomali, id_sekarang


def proses_sequential():
    if not os.path.exists(FILE_DATASET):
        print(f"ERROR: File '{FILE_DATASET}' tidak ditemukan.")
        print("Pastikan sequential.py berada satu folder dengan" \
        " transaksi_2gb.csv.")
        return

    jumlah_baris = 0
    jumlah_anomali = 0

    jumlah_per_jenis = {
        "jumlah_nol": 0,
        "jumlah_negatif": 0,
        "harga_negatif": 0,
        "total_salah": 0,
        "jumlah_ekstrem": 0,
        "harga_ekstrem": 0,
        "duplikat_transaksi": 0,
    }

    # Menyimpan hanya satu nilai integer, bukan jutaan ID.
    id_terbesar = None

    ukuran_file = os.path.getsize(FILE_DATASET)

    print("=" * 65)
    print("SEQUENTIAL - DETEKSI ANOMALI")
    print("=" * 65)
    print(f"Dataset : {FILE_DATASET}")
    print(f"Ukuran  : {ukuran_file / 1_000_000_000:.4f} GB")
    print()

    waktu_mulai = time.perf_counter()

    # Streaming:
    # file dibaca satu baris pada satu waktu sehingga 2 GB
    # tidak dimuat sekaligus ke RAM.
    with open(
        FILE_DATASET,
        "r",
        newline="",
        encoding="utf-8",
        buffering=1024 * 1024,
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            jumlah_baris += 1

            jenis_anomali, id_sekarang = cek_anomali(
                row,
                id_terbesar
            )

            if jenis_anomali:
                jumlah_anomali += 1

                for jenis in jenis_anomali:
                    jumlah_per_jenis[jenis] += 1

            # Hanya update ID terbesar jika ID sekarang lebih besar.
            if id_terbesar is None or id_sekarang > id_terbesar:
                id_terbesar = id_sekarang

    waktu_selesai = time.perf_counter()
    waktu_eksekusi = waktu_selesai - waktu_mulai

    print("=" * 65)
    print("HASIL")
    print("=" * 65)
    print(f"Jumlah transaksi        : {jumlah_baris:,}")
    print(f"Jumlah transaksi anomali: {jumlah_anomali:,}")
    print()
    print("Rincian anomali:")

    for jenis, jumlah in jumlah_per_jenis.items():
        print(f"  {jenis:22s}: {jumlah:,}")

    print()
    print(f"Waktu eksekusi : {waktu_eksekusi:.4f} detik")
    print("=" * 65)


if __name__ == "__main__":
    proses_sequential()
