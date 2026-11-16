"""LAPISAN 2: untuk pertanyaan kompleks. Gemini HANYA boleh memakai dokumen resmi."""
import json
import os
from pathlib import Path
from .teks import PencocokTFIDF

ADA_DI = Path(__file__).resolve().parent.parent / "data" / "dokumen.json"
AMBANG_DOKUMEN = 0.10  # di bawah ini = dianggap tidak ada dokumen yang relevan
JUMLAH_DOKUMEN = 3     # berapa dokumen teratas yang diberikan ke Gemini

ATURAN_LLM = (
    "Kamu adalah asisten layanan akademik program studi. "
    "Jawab HANYA berdasarkan bagian 'DOKUMEN RESMI' yang diberikan (boleh menggabungkan beberapa dokumen). "
    "DILARANG memakai pengetahuan di luar dokumen, menebak, atau mengarang. "
    "Jika jawabannya tidak ada di dokumen, jawab persis: TIDAK_ADA_DI_DOKUMEN. "
    "Jawab singkat dalam Bahasa Indonesia dan sebutkan judul dokumen yang dipakai."
)
TANDA_TIDAK_ADA = "TIDAK_ADA_DI_DOKUMEN"


class PencariDokumen:
    def __init__(self, path=ADA_DI):
        self.dok = {d["id"]: d for d in json.loads(Path(path).read_text(encoding="utf-8"))}
        self.pencocok = PencocokTFIDF([d["judul"] + " " + d["isi"] for d in self.dok.values()],
                                      list(self.dok.keys()))

    def cari(self, pertanyaan, ambang=AMBANG_DOKUMEN, k=JUMLAH_DOKUMEN):
        """Return (daftar dokumen teratas yang skornya >= ambang, skor tertinggi)."""
        hasil = self.pencocok.cari_banyak(pertanyaan, k)
        dok = [self.dok[label] for label, skor in hasil if skor >= ambang]
        return dok, (hasil[0][1] if hasil else 0.0)


class GeminiAsli:
    """Pemanggil Gemini sungguhan. Kunci dibaca dari file .env (bukan ditulis di kode)."""

    def __init__(self):
        from dotenv import load_dotenv
        from google import genai
        load_dotenv()
        kunci = os.getenv("GEMINI_API_KEY")
        if not kunci or kunci.startswith("isi_kunci"):
            raise RuntimeError("GEMINI_API_KEY belum diisi di file .env")
        self.client = genai.Client(api_key=kunci)
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    def __call__(self, pertanyaan: str, dokumen: list) -> str:
        from google.genai import types
        bagian = [f"[Dokumen {i}] Judul: {d['judul']}\nIsi: {d['isi']}" for i, d in enumerate(dokumen, 1)]
        isi = "DOKUMEN RESMI\n" + "\n\n".join(bagian) + f"\n\nPERTANYAAN: {pertanyaan}"
        r = self.client.models.generate_content(
            model=self.model, contents=isi,
            config=types.GenerateContentConfig(system_instruction=ATURAN_LLM, temperature=0.0))
        return (r.text or "").strip()


def jawab_dengan_llm(pertanyaan, pencari: PencariDokumen, llm):
    """Return (jawaban atau None, info). None = harus ditolak."""
    dok, skor = pencari.cari(pertanyaan)
    if not dok:
        return None, f"tidak ada dokumen relevan (skor {skor:.2f})"
    judul = " | ".join(d["judul"] for d in dok)
    teks = llm(pertanyaan, dok)
    if not teks or TANDA_TIDAK_ADA in teks:
        return None, f"LLM menyatakan tidak ada di dokumen: {judul}"
    return teks, f"dokumen: {judul}"
