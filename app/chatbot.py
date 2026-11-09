"""Gabungan: Lapisan 1 (FAQ TF-IDF) -> Lapisan 2 (Gemini + dokumen) -> penolakan sopan."""
from .lapisan1_faq import FAQ
from .lapisan2_llm import PencariDokumen, GeminiAsli, jawab_dengan_llm

PESAN_TOLAK = ("Maaf, saya belum menemukan jawaban resmi untuk pertanyaan itu. "
               "Silakan hubungi admin prodi di info@unp.ac.id atau 0751 7053902.")


class ChatbotAkademik:
    def __init__(self, llm=None):
        self.faq = FAQ()
        self.pencari = PencariDokumen()
        self.llm = llm  # boleh None => Lapisan 2 mati, langsung tolak

    def tanya(self, pertanyaan: str):
        """Return (jawaban, sumber). sumber: 'FAQ' | 'LLM' | 'TOLAK'."""
        jawab, skor = self.faq.jawab(pertanyaan)
        if jawab:
            return jawab, f"FAQ (skor {skor:.2f})"
        if self.llm is not None:
            try:
                jawab, info = jawab_dengan_llm(pertanyaan, self.pencari, self.llm)
            except Exception as e:  # jaringan putus, kuota habis, dll.
                return PESAN_TOLAK, f"TOLAK (error LLM: {type(e).__name__})"
            if jawab:
                return jawab, f"LLM ({info})"
            return PESAN_TOLAK, f"TOLAK ({info})"
        return PESAN_TOLAK, "TOLAK (LLM mati)"
