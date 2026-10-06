FROM python:3.13-slim

WORKDIR /app

# Semua program hanya menggunakan standard library Python.
COPY sequential.py .
COPY threading_version.py .
COPY multiprocessing_version.py .
COPY benchmark_per_core.py .

# Dataset 2 GB tidak dimasukkan ke image.
# Dataset akan di-mount melalui docker-compose.yml.
CMD ["python", "--version"]
