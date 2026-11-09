# Chatbot Layanan Akademik Prodi (FAQ TF-IDF + Gemini)

Chatbot dua lapis:
1. **Lapisan 1 – FAQ cepat (TF-IDF).** Pertanyaan yang sering muncul dijawab dari `data/faq.json` (jawaban sudah diverifikasi).
2. **Lapisan 2 – Gemini + dokumen resmi.** Pertanyaan rumit dijawab Gemini, tetapi HANYA dari `data/dokumen.json`. Kalau tidak ada di dokumen, bot menolak dan mengarahkan ke admin.

## Cara menjalankan
```
python -m venv .venv
.venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # Mac/Linux: cp .env.example .env  lalu isi GEMINI_API_KEY
python main.py --tiruan         # tanpa kunci API (LLM tiruan)
python main.py                  # dengan Gemini asli
python -m pytest                # jalankan tes
```
## Struktur
- `app/teks.py` pembersih teks + TF-IDF
- `app/lapisan1_faq.py` Lapisan 1
- `app/lapisan2_llm.py` Lapisan 2 (Gemini)
- `app/chatbot.py` penggabung
- `data/` FAQ dan dokumen resmi (ISI DENGAN DATA ASLI PRODI)
- `tests/` tes otomatis

Kunci API ada di `.env` (tidak ikut ke GitHub).
