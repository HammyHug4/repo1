# STEP 6 - Docker Benchmark

## 1. Build image

```cmd
docker compose build
```

## 2. Cek container

```cmd
docker compose run --rm benchmark python --version
```

## 3. Jalankan Sequential di Docker

```cmd
docker compose run --rm benchmark python sequential.py
```

## 4. Jalankan Threading 4 thread di Docker

```cmd
docker compose run --rm benchmark python threading_version.py --threads 4
```

## 5. Jalankan Multiprocessing 6 process di Docker

```cmd
docker compose run --rm benchmark python multiprocessing_version.py --processes 6
```

## 6. Catatan

- `transaksi_2gb.csv` tidak disalin ke Docker image karena ukurannya 2 GB.
- File CSV di-mount read-only ke `/app/transaksi_2gb.csv`.
- Ketiga program memakai environment Python yang sama.
- Container dibatasi sampai 6 CPU logical CPUs untuk membuat benchmark lebih terkontrol.
- Jangan menjalankan tiga benchmark sekaligus. Jalankan satu per satu.
- Waktu dari Docker inilah yang akan dipakai sebagai benchmark final setelah ketiganya berhasil.
