import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("Model:", model)
try:
    r = client.models.generate_content(model=model, contents="Balas satu kata: halo")
    print("BERHASIL:", r.text)
except Exception as e:
    print("GAGAL:", e)