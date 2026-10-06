#!/usr/bin/env python3
"""
Generator dataset CSV transaksi ~2 GB dengan anomali tersembunyi.

Output utama:
    transaksi_2gb.csv

Ground truth (untuk validasi saja, TIDAK dipakai oleh program deteksi):
    ground_truth_anomali.csv

Semua library yang digunakan adalah standard library Python.
"""

import argparse
import csv
import os
import random
import string
from datetime import datetime, timedelta


HEADER = [
    "id_transaksi",
    "timestamp",
    "id_pelanggan",
    "produk",
    "kategori",
    "jumlah",
    "harga_satuan",
    "total",
    "metode_pembayaran",
    "kota",
]

PRODUK = [
    "Laptop_A", "Laptop_B", "Smartphone_A", "Smartphone_B",
    "Tablet_A", "Monitor_A", "Keyboard_A", "Mouse_A",
    "Headset_A", "Printer_A", "SSD_A", "RAM_A",
    "Flashdisk_A", "Router_A", "Kamera_A", "Smartwatch_A",
    "Powerbank_A", "Speaker_A", "Webcam_A", "Kabel_A",
]

KATEGORI = {
    "Laptop_A": "Elektronik",
    "Laptop_B": "Elektronik",
    "Smartphone_A": "Elektronik",
    "Smartphone_B": "Elektronik",
    "Tablet_A": "Elektronik",
    "Monitor_A": "Komputer",
    "Keyboard_A": "Komputer",
    "Mouse_A": "Komputer",
    "Headset_A": "Aksesoris",
    "Printer_A": "Komputer",
    "SSD_A": "Komputer",
    "RAM_A": "Komputer",
    "Flashdisk_A": "Aksesoris",
    "Router_A": "Jaringan",
    "Kamera_A": "Elektronik",
    "Smartwatch_A": "Elektronik",
    "Powerbank_A": "Aksesoris",
    "Speaker_A": "Elektronik",
    "Webcam_A": "Aksesoris",
    "Kabel_A": "Aksesoris",
}

HARGA = {
    "Laptop_A": 8500000,
    "Laptop_B": 12500000,
    "Smartphone_A": 3500000,
    "Smartphone_B": 7500000,
    "Tablet_A": 4200000,
    "Monitor_A": 2800000,
    "Keyboard_A": 450000,
    "Mouse_A": 250000,
    "Headset_A": 650000,
    "Printer_A": 2200000,
    "SSD_A": 950000,
    "RAM_A": 800000,
    "Flashdisk_A": 150000,
    "Router_A": 550000,
    "Kamera_A": 6800000,
    "Smartwatch_A": 1200000,
    "Powerbank_A": 350000,
    "Speaker_A": 900000,
    "Webcam_A": 500000,
    "Kabel_A": 75000,
}

METODE = ["Transfer", "E-Wallet", "Kartu Kredit", "Kartu Debit", "COD"]
KOTA = [
    "Palembang", "Prabumulih", "Lubuklinggau", "Jambi",
    "Bandar Lampung", "Bengkulu", "Jakarta", "Bandung",
    "Semarang", "Surabaya",
]

ANOMALY_TYPES = [
    "jumlah_nol",
    "jumlah_negatif",
    "harga_negatif",
    "total_salah",
    "jumlah_ekstrem",
    "harga_ekstrem",
    "duplikat_transaksi",
]


def random_timestamp(rng, start_date):
    """Timestamp acak dalam rentang 2 tahun."""
    seconds = rng.randint(0, 2 * 365 * 24 * 60 * 60)
    dt = start_date + timedelta(seconds=seconds)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def normal_transaction(rng, transaction_number, start_date):
    product = rng.choice(PRODUK)
    qty = rng.randint(1, 8)
    price = HARGA[product]

    # Variasi harga normal sekitar harga dasar.
    variation = rng.uniform(0.90, 1.10)
    price = int(round(price * variation / 1000) * 1000)
    total = qty * price

    return [
        f"TRX{transaction_number:09d}",
        random_timestamp(rng, start_date),
        f"CUST{rng.randint(1, 250000):07d}",
        product,
        KATEGORI[product],
        qty,
        price,
        total,
        rng.choice(METODE),
        rng.choice(KOTA),
    ]


def make_anomaly(rng, row, anomaly_type):
    """Mengubah row normal menjadi row anomali."""
    row = list(row)

    if anomaly_type == "jumlah_nol":
        row[5] = 0
        row[7] = 0

    elif anomaly_type == "jumlah_negatif":
        row[5] = -rng.randint(1, 20)
        row[7] = row[5] * row[6]

    elif anomaly_type == "harga_negatif":
        row[6] = -rng.randint(1000, 1000000)
        row[7] = row[5] * row[6]

    elif anomaly_type == "total_salah":
        # Quantity dan harga terlihat normal, tetapi total tidak sesuai.
        row[7] = row[5] * row[6] + rng.choice([-1, 1000, 50000, 999999])

    elif anomaly_type == "jumlah_ekstrem":
        row[5] = rng.randint(10000, 1000000)
        row[7] = row[5] * row[6]

    elif anomaly_type == "harga_ekstrem":
        row[6] = rng.randint(100000000, 999999999)
        row[7] = row[5] * row[6]

    elif anomaly_type == "duplikat_transaksi":
        # ID tetap sama; row identik dengan transaksi sebelumnya.
        pass

    return row


def parse_args():
    parser = argparse.ArgumentParser(
        description="Membuat dataset transaksi CSV ~2 GB dengan anomali."
    )
    parser.add_argument(
        "--output",
        default="transaksi_2gb.csv",
        help="Nama file CSV output."
    )
    parser.add_argument(
        "--target-gb",
        type=float,
        default=2.0,
        help="Target ukuran file dalam GB desimal. Default: 2.0."
    )
    parser.add_argument(
        "--anomaly-rate",
        type=float,
        default=0.002,
        help="Proporsi transaksi anomali. Default 0.002 = 0.2%%."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20261006,
        help="Seed agar data dapat direproduksi."
    )
    parser.add_argument(
        "--ground-truth",
        default="ground_truth_anomali.csv",
        help="File daftar anomali untuk validasi."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not (0 <= args.anomaly_rate <= 1):
        raise ValueError("--anomaly-rate harus antara 0 dan 1.")

    target_bytes = int(args.target_gb * 1_000_000_000)
    rng = random.Random(args.seed)
    start_date = datetime(2025, 1, 1)

    output_path = os.path.abspath(args.output)
    truth_path = os.path.abspath(args.ground_truth)

    # Buffer besar membantu mengurangi overhead I/O tanpa menyimpan dataset
    # 2 GB di RAM.
    with open(output_path, "w", newline="", encoding="utf-8", buffering=1024 * 1024) as f_csv, \
         open(truth_path, "w", newline="", encoding="utf-8", buffering=1024 * 1024) as f_truth:

        writer = csv.writer(f_csv)
        truth_writer = csv.writer(f_truth)

        writer.writerow(HEADER)
        truth_writer.writerow(["id_transaksi", "jenis_anomali"])

        transaction_number = 1
        anomaly_count = 0
        last_normal_row = None
        last_size_report = 0

        while f_csv.tell() < target_bytes:
            row = normal_transaction(
                rng,
                transaction_number,
                start_date
            )

            # Injeksi anomali secara probabilistik.
            if rng.random() < args.anomaly_rate:
                anomaly_type = rng.choice(ANOMALY_TYPES)

                if anomaly_type == "duplikat_transaksi" and last_normal_row is not None:
                    # Duplikat dibuat benar-benar sama dengan row sebelumnya.
                    row = list(last_normal_row)
                else:
                    row = make_anomaly(rng, row, anomaly_type)

                anomaly_count += 1
                truth_writer.writerow([row[0], anomaly_type])
            else:
                last_normal_row = list(row)

            writer.writerow(row)
            transaction_number += 1

            # Progress tiap ~100 MB.
            current_size = f_csv.tell()
            if current_size - last_size_report >= 100_000_000:
                percent = min(100, current_size / target_bytes * 100)
                print(
                    f"[PROGRESS] {current_size / 1_000_000_000:.3f} GB "
                    f"({percent:.1f}%) | transaksi={transaction_number - 1:,} "
                    f"| anomali={anomaly_count:,}",
                    flush=True
                )
                last_size_report = current_size

    final_size = os.path.getsize(output_path)

    print("\n=== SELESAI ===")
    print(f"Dataset       : {output_path}")
    print(f"Ukuran        : {final_size / 1_000_000_000:.4f} GB")
    print(f"Transaksi     : {transaction_number - 1:,}")
    print(f"Anomali       : {anomaly_count:,}")
    print(f"Rasio anomali : {anomaly_count / max(1, transaction_number - 1) * 100:.4f}%")
    print(f"Ground truth  : {truth_path}")
    print("\nCatatan:")
    print("- ground_truth_anomali.csv hanya untuk validasi.")
    print("- Program deteksi pada tugas nanti HANYA membaca transaksi_2gb.csv.")
    print("- Dataset dibuat streaming, jadi tidak dimuat 2 GB sekaligus ke RAM.")


if __name__ == "__main__":
    main()
