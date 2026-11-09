from app.chatbot import ChatbotAkademik, PESAN_TOLAK
from app.lapisan2_llm import TANDA_TIDAK_ADA


def llm_kutip(q, dok):
    return "Menurut " + dok["judul"] + ": " + dok["isi"]


def llm_tak_tahu(q, dok):
    return TANDA_TIDAK_ADA


def llm_error(q, dok):
    raise ConnectionError("putus")


def test_faq_dijawab_cepat_tanpa_llm():
    bot = ChatbotAkademik(llm=llm_error)  # kalau LLM dipanggil, tes ini gagal
    jawab, sumber = bot.tanya("Kak, alamat kampus dimana ya?")
    assert "Air Tawar" in jawab and sumber.startswith("FAQ")


def test_pertanyaan_kompleks_pakai_dokumen():
    bot = ChatbotAkademik(llm=llm_kutip)
    jawab, sumber = bot.tanya("Berapa lama maksimal cuti akademik?")
    assert "dua semester" in jawab and sumber.startswith("LLM")


def test_tanpa_dokumen_relevan_llm_tidak_dipanggil():
    bot = ChatbotAkademik(llm=llm_error)
    jawab, sumber = bot.tanya("Siapa presiden pertama Indonesia?")
    assert jawab == PESAN_TOLAK and "tidak ada dokumen" in sumber


def test_llm_bilang_tidak_tahu_ditolak():
    bot = ChatbotAkademik(llm=llm_tak_tahu)
    jawab, _ = bot.tanya("Berapa lama maksimal cuti akademik?")
    assert jawab == PESAN_TOLAK


def test_llm_error_tidak_bikin_crash():
    bot = ChatbotAkademik(llm=llm_error)
    jawab, sumber = bot.tanya("Berapa lama maksimal cuti akademik?")
    assert jawab == PESAN_TOLAK and "error" in sumber


def test_llm_mati():
    jawab, _ = ChatbotAkademik(llm=None).tanya("syarat seminar proposal skripsi")
    assert jawab == PESAN_TOLAK


def test_cuti_kuliah_tidak_salah_masuk_faq_jadwal():
    bot = ChatbotAkademik(llm=llm_kutip)
    _, sumber = bot.tanya("boleh cuti kuliah nggak")
    assert sumber.startswith("LLM")


def test_variasi_kalimat_faq():
    bot = ChatbotAkademik(llm=llm_error)
    for q in ["kampus di mana sih", "cara isi krs", "email admin", "kapan krs dibuka"]:
        assert bot.tanya(q)[1].startswith("FAQ"), q
