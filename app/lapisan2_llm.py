"""LAPISAN 2: untuk pertanyaan kompleks. Gemini HANYA boleh memakai dokumen resmi."""
import json
import os
from pathlib import Path
from .teks import PencocokTFIDF

ADA_DI = Path(__file__).resolve().parent.parent / "data" / "dokumen.json"
AMBANG_DOKUMEN = 0.15  # di bawah ini = dianggap tidak ada dokumen yang relevan

ATURAN_LLM = (
    "Kamu adalah asisten layanan akademik program studi. "
    "Jawab HANYA berdasarkan bagian 'DOKUMEN RESMI' yang diberikan. "
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

    def cari(self, pertanyaan, ambang=AMBANG_DOKUMEN):
        """Return (dokumen atau None, skor)."""
        label, skor = self.pencocok.cari(pertanyaan)
        if label is not None and skor >= ambang:
            return self.dok[label], skor
        return None, skor


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

    def __call__(self, pertanyaan: str, dokumen: dict) -> str:
        from google.genai import types
        isi = (f"DOKUMEN RESMI\nJudul: {dokumen['judul']}\nIsi: {dokumen['isi']}\n\n"
               f"PERTANYAAN: {pertanyaan}")
        r = self.client.models.generate_content(
            model=self.model, contents=isi,
            config=types.GenerateContentConfig(system_instruction=ATURAN_LLM, temperature=0.0))
        return (r.text or "").strip()


def jawab_dengan_llm(pertanyaan, pencari: PencariDokumen, llm):
    """Return (jawaban atau None, info). None = harus ditolak."""
    dok, skor = pencari.cari(pertanyaan)
    if dok is None:
        return None, f"tidak ada dokumen relevan (skor {skor:.2f})"
    teks = llm(pertanyaan, dok)
    if not teks or TANDA_TIDAK_ADA in teks:
        return None, f"LLM menyatakan tidak ada di dokumen '{dok['judul']}'"
    return teks, f"dokumen: {dok['judul']}"
