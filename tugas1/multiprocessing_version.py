#!/usr/bin/env python3
"""
STEP 5 - Multiprocessing FINAL
Tugas 1 - Sistem Terdistribusi dan Komputasi Paralel

Deteksi anomali pada transaksi_2gb.csv menggunakan multiprocessing.

Perbaikan final:
- File dibagi berdasarkan rentang byte.
- Setiap process membaca bagian file masing-masing.
- Worker menggunakan readline(), sehingga aman menggunakan f.tell().
- Duplikat dideteksi berdasarkan ID terbesar yang sudah terlihat di bagian
  tersebut, bukan hanya membandingkan dengan baris sebelumnya.
- Karena ID normal pada dataset generator selalu meningkat, setiap ID yang
  muncul kembali akan bernilai <= ID terbesar yang sudah pernah dibaca.
- Tidak perlu menyimpan jutaan ID dalam set.
"""

import argparse
import csv
import multiprocessing as mp
import os
import time


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
    return int(id_transaksi[3:])


def cek_nilai(jumlah, harga, total):
    anomali = []

    if jumlah == 0:
        anomali.append("jumlah_nol")

    if jumlah < 0:
        anomali.append("jumlah_negatif")

    if harga < 0:
        anomali.append("harga_negatif")

    if total != jumlah * harga:
        anomali.append("total_salah")

    if jumlah > BATAS_JUMLAH_EKSTREM:
        anomali.append("jumlah_ekstrem")

    if harga > BATAS_HARGA_EKSTREM:
        anomali.append("harga_ekstrem")

    return anomali


def cari_batas(file_path, jumlah_process):
    """Membagi file menjadi beberapa rentang byte yang dimulai dari awal baris."""
    ukuran = os.path.getsize(file_path)

    with open(file_path, "rb") as f:
        # Lewati header.
        f.readline()
        data_start = f.tell()

        if data_start >= ukuran:
            return []

        batas = [data_start]

        for i in range(1, jumlah_process):
            target = data_start + ((ukuran - data_start) * i // jumlah_process)

            f.seek(target)

            # Jika target berada di tengah baris, buang baris parsial.
            f.readline()

            posisi = f.tell()

            if posisi < ukuran:
                batas.append(posisi)

        batas.append(ukuran)

    # Hilangkan batas yang sama.
    batas_unik = []

    for posisi in batas:
        if not batas_unik or posisi != batas_unik[-1]:
            batas_unik.append(posisi)

    return [
        (batas_unik[i], batas_unik[i + 1])
        for i in range(len(batas_unik) - 1)
        if batas_unik[i] < batas_unik[i + 1]
    ]


def proses_bagian(args):
    """
    Worker multiprocessing.

    Deteksi duplikat menggunakan id_terbesar:
    - ID normal meningkat: 1, 2, 3, 4, ...
    - Jika ID yang muncul <= ID terbesar sebelumnya, ID tersebut pernah muncul.
    """
    file_path, start, end = args

    rincian = {jenis: 0 for jenis in JENIS_ANOMALI}

    jumlah_baris = 0
    jumlah_anomali = 0

    id_terbesar = None

    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8",
        buffering=1024 * 1024,
    ) as f:

        f.seek(start)

        while True:
            # readline() digunakan agar f.tell() tetap aman.
            line = f.readline()

            if not line:
                break

            posisi_akhir = f.tell()

            # Baris di luar rentang menjadi milik bagian berikutnya.
            if posisi_akhir > end:
                break

            try:
                fields = next(csv.reader([line]))
            except csv.Error:
                continue

            if len(fields) != 10:
                continue

            try:
                id_transaksi = fields[0]
                jumlah = int(fields[5])
                harga = int(fields[6])
                total = int(fields[7])
                id_sekarang = nomor_id(id_transaksi)
            except (ValueError, IndexError):
                continue

            jumlah_baris += 1

            jenis_anomali = cek_nilai(
                jumlah,
                harga,
                total,
            )

            # DETEKSI DUPLIKAT FINAL:
            #
            # Generator membuat ID transaksi normal meningkat.
            # Jika ID sekarang <= ID terbesar yang sudah pernah dibaca
            # dalam bagian ini, berarti ID tersebut muncul kembali.
            if id_terbesar is not None and id_sekarang <= id_terbesar:
                jenis_anomali.append("duplikat_transaksi")

            if jenis_anomali:
                jumlah_anomali += 1

                for jenis in jenis_anomali:
                    rincian[jenis] += 1

            if id_terbesar is None or id_sekarang > id_terbesar:
                id_terbesar = id_sekarang

    return {
        "start": start,
        "end": end,
        "baris": jumlah_baris,
        "anomali": jumlah_anomali,
        "rincian": rincian,
    }


def proses_multiprocessing(jumlah_process):
    if not os.path.exists(FILE_DATASET):
        print(f"ERROR: File '{FILE_DATASET}' tidak ditemukan.")
        print("Pastikan file berada satu folder dengan program.")
        return

    if jumlah_process < 1:
        print("ERROR: jumlah process minimal 1.")
        return

    ukuran = os.path.getsize(FILE_DATASET)
    bagian = cari_batas(FILE_DATASET, jumlah_process)

    if not bagian:
        print("ERROR: Dataset tidak dapat dibagi.")
        return

    print("=" * 65)
    print("MULTIPROCESSING - DETEKSI ANOMALI")
    print("=" * 65)
    print(f"Dataset : {FILE_DATASET}")
    print(f"Ukuran  : {ukuran / 1_000_000_000:.4f} GB")
    print(f"Process : {jumlah_process}")
    print(f"Bagian  : {len(bagian)}")
    print()

    tugas = [
        (FILE_DATASET, start, end)
        for start, end in bagian
    ]

    waktu_mulai = time.perf_counter()

    with mp.Pool(processes=jumlah_process) as pool:
        hasil = pool.map(
            proses_bagian,
            tugas,
            chunksize=1,
        )

    jumlah_baris = sum(
        hasil_bagian["baris"]
        for hasil_bagian in hasil
    )

    jumlah_anomali = sum(
        hasil_bagian["anomali"]
        for hasil_bagian in hasil
    )

    jumlah_per_jenis = {
        jenis: sum(
            hasil_bagian["rincian"][jenis]
            for hasil_bagian in hasil
        )
        for jenis in JENIS_ANOMALI
    }

    waktu_selesai = time.perf_counter()
    waktu_eksekusi = waktu_selesai - waktu_mulai

    print("=" * 65)
    print("HASIL")
    print("=" * 65)
    print(f"Jumlah transaksi        : {jumlah_baris:,}")
    print(f"Jumlah transaksi anomali: {jumlah_anomali:,}")
    print()
    print("Rincian anomali:")

    for jenis in JENIS_ANOMALI:
        print(
            f"  {jenis:22s}: "
            f"{jumlah_per_jenis[jenis]:,}"
        )

    print()
    print(f"Jumlah process : {jumlah_process}")
    print(f"Waktu eksekusi : {waktu_eksekusi:.4f} detik")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(
        description="Deteksi anomali transaksi menggunakan multiprocessing."
    )

    parser.add_argument(
        "--processes",
        type=int,
        default=6,
        help="Jumlah process. Contoh: --processes 6",
    )

    args = parser.parse_args()

    # Wajib untuk multiprocessing pada Windows.
    mp.freeze_support()

    proses_multiprocessing(args.processes)


if __name__ == "__main__":
    main()
