"""Pembersih teks + pencocok TF-IDF sederhana (dipakai Lapisan 1 dan pencarian dokumen)."""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Kata umum yang tidak membawa makna (kata "ya", "kak" sering bikin salah cocok)
STOPWORD = {"ya", "kak", "dong", "deh", "sih", "nih", "yang", "di", "ke", "dan", "itu", "ini",
            "apa", "bagaimana", "gimana", "tolong", "mau", "saya", "aku", "bisa", "boleh", "kah"}


def bersihkan(teks: str) -> str:
    """huruf kecil, buang tanda baca, buang stopword."""
    teks = re.sub(r"[^\w\s]", " ", teks.lower())
    kata = [k for k in teks.split() if k not in STOPWORD]
    return " ".join(kata)


class PencocokTFIDF:
    """Mencocokkan kalimat pengguna dengan daftar teks memakai TF-IDF + cosine similarity."""

    def __init__(self, teks_list, label_list):
        self.label = label_list
        self.vec = TfidfVectorizer(ngram_range=(1, 2))
        self.matriks = self.vec.fit_transform([bersihkan(t) for t in teks_list])

    def cari(self, pertanyaan: str):
        """Kembalikan (label_terbaik, skor). Skor 0..1."""
        q = bersihkan(pertanyaan)
        if not q:
            return None, 0.0
        skor = cosine_similarity(self.vec.transform([q]), self.matriks)[0]
        i = int(skor.argmax())
        return self.label[i], float(skor[i])
