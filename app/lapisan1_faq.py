"""LAPISAN 1: jawaban cepat dari FAQ yang sudah diverifikasi (TF-IDF, Modul 5)."""
import json
from pathlib import Path
from .teks import PencocokTFIDF

ADA_DI = Path(__file__).resolve().parent.parent / "data" / "faq.json"
AMBANG_FAQ = 0.6  # makin tinggi = makin ketat (lebih sedikit salah jawab)


class FAQ:
    def __init__(self, path=ADA_DI):
        self.data = {d["id"]: d for d in json.loads(Path(path).read_text(encoding="utf-8"))}
        teks, label = [], []
        for d in self.data.values():
            for p in d["pertanyaan"]:
                teks.append(p)
                label.append(d["id"])
        self.pencocok = PencocokTFIDF(teks, label)

    def jawab(self, pertanyaan: str, ambang=AMBANG_FAQ):
        """Return (jawaban atau None, skor)."""
        label, skor = self.pencocok.cari(pertanyaan)
        if label is not None and skor >= ambang:
            return self.data[label]["jawaban"], skor
        return None, skor
