import os
import time

class LamportClock:
    def __init__(self, nama):
        self.nama = nama
        self.waktu = 0
        self.offset = int(os.environ.get("OFFSET", "0"))

    def jam_fisik(self):
        t = time.time() + self.offset
        return time.strftime("%H:%M:%S", time.localtime(t))

    def _log(self, pesan):
        print(
            f"{pesan}",
            flush=True,
        )

    def kirim(self, tujuan):
        lama = self.waktu
        self.waktu += 1
        self._log(f"KIRIM  ke {tujuan:<12}  L = {lama}+1 = {self.waktu}")
        return self.waktu

    def terima(self, asal, ts_masuk):
        lama = self.waktu
        self.waktu = max(lama, ts_masuk) + 1
        self._log(
            f"TERIMA dari {asal:<12} "
            f"L = max({lama}, {ts_masuk})+1 = {self.waktu}"
        )
        return self.waktu
