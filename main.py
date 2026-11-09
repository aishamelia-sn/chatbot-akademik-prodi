"""Jalankan chatbot di terminal.  python main.py        -> pakai Gemini asli
                                  python main.py --tiruan -> LLM tiruan (tanpa kunci API)"""
import sys
from app.chatbot import ChatbotAkademik


def llm_tiruan(pertanyaan, dokumen):
    """LLM palsu untuk latihan tanpa kunci: cuma mengutip isi dokumen."""
    return f"[TIRUAN] Menurut '{dokumen['judul']}': {dokumen['isi']}"


def main():
    if "--tiruan" in sys.argv:
        llm = llm_tiruan
    else:
        try:
            from app.lapisan2_llm import GeminiAsli
            llm = GeminiAsli()
        except Exception as e:
            print(f"(Gemini belum aktif: {e}. Lapisan 2 dimatikan.)")
            llm = None
    bot = ChatbotAkademik(llm=llm)
    print("Chatbot Akademik Prodi. Ketik 'keluar' untuk berhenti.")
    while True:
        q = input("Kamu : ").strip()
        if q.lower() in {"keluar", "exit", "quit"}:
            print("Bot  : Sampai jumpa!")
            break
        if not q:
            continue
        jawab, sumber = bot.tanya(q)
        print(f"Bot  : {jawab}\n       (sumber: {sumber})")


if __name__ == "__main__":
    main()
