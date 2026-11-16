"""LAPISAN 1: jawaban cepat dari FAQ yang sudah diverifikasi (TF-IDF, Modul 5)."""
import json
from pathlib import Path
from .teks import PencocokTFIDF, bersihkan

ADA_DI = Path(__file__).resolve().parent.parent / "data" / "faq.json"
AMBANG_FAQ = 0.7  # makin tinggi = makin ketat (lebih sedikit salah jawab)


class FAQ:
    def __init__(self, path=ADA_DI):
        self.data = {d["id"]: d for d in json.loads(Path(path).read_text(encoding="utf-8"))}
        teks, label = [], []
        self.kata_entri = {}  # semua kata yang dikenal tiap entri (untuk mode "ketat")
        for d in self.data.values():
            self.kata_entri[d["id"]] = set()
            for p in d["pertanyaan"]:
                teks.append(p)
                label.append(d["id"])
                self.kata_entri[d["id"]] |= set(bersihkan(p).split())
        self.pencocok = PencocokTFIDF(teks, label)

    def jawab(self, pertanyaan: str, ambang=AMBANG_FAQ):
        """Return (jawaban atau None, skor)."""
        label, skor = self.pencocok.cari(pertanyaan)
        if label is not None and skor >= ambang:
            # Mode "ketat" (tulis "ketat": true di faq.json): jawaban umum hanya untuk
            # pertanyaan umum. Kalau ada kata baru (hari, semester, nama matkul...),
            # pertanyaannya spesifik, jadi serahkan ke Lapisan 2.
            if self.data[label].get("ketat"):
                kata_baru = set(bersihkan(pertanyaan).split()) - self.kata_entri[label]
                if kata_baru:
                    return None, skor
            return self.data[label]["jawaban"], skor
        return None, skor
