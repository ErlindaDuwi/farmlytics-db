import requests
import json
import re

VALID_KEYS = [
    "komoditas",
    "berat",
    "lokasi",
    "gagal_panen",
    "grade",
    "tanggal"
]

# 🔥 NORMALISASI VALUE
def normalize_value(key, value):
    if value is None:
        return None

    value = str(value).strip()

    if key == "berat":
        match = re.search(r"\d+", value)
        return int(match.group()) if match else None

    if key == "gagal_panen":
        match = re.search(r"\d+", value)
        return int(match.group()) if match else None

    if key == "grade":
        return value.upper()

    return value


# 🔥 CLEAN JSON (VERSI AMAN)
def clean_json(text):
    try:
        if not text:
            return None

        text = text.replace("```json", "").replace("```", "").strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None

        json_str = match.group()

        # 🔥 Pakai JSON repair sederhana
        json_str = re.sub(r'(\w+)\s*:', r'"\1":', json_str)

        # hapus trailing comma
        json_str = re.sub(r',\s*}', '}', json_str)

        data = json.loads(json_str)

        # 🔥 FILTER KEY + NORMALISASI
        clean = {}
        for key in VALID_KEYS:
            clean[key] = normalize_value(key, data.get(key))

        return clean

    except Exception as e:
        print("CLEAN ERROR:", e)
        return None


# 🔥 FALLBACK FLEXIBLE (LEBIH LUAS)
def fallback_manual(text):
    result = {}

    komoditas = re.search(r"(cabai|tomat|padi|jagung)", text, re.I)
    berat = re.search(r"(\d+)\s*kg", text, re.I)
    lokasi = re.search(r"lokasi\s*([A-Za-z ]+)", text, re.I)
    gagal = re.search(r"(\d+)\s*%", text)
    grade = re.search(r"grade\s*([A-C])", text, re.I)
    tanggal = re.search(r"(\d{1,2}\s\w+\s\d{4})", text)

    if komoditas:
        result["komoditas"] = komoditas.group(1).lower()

    if berat:
        result["berat"] = int(berat.group(1))

    if lokasi:
        result["lokasi"] = lokasi.group(1).strip()

    if gagal:
        result["gagal_panen"] = int(gagal.group(1))

    if grade:
        result["grade"] = grade.group(1).upper()

    if tanggal:
        result["tanggal"] = tanggal.group(1)

    return result


# 🔥 REQUEST + PARSING FINAL
def parsing_openclaw(text):
    try:
        prompt = f"""
Keluarkan JSON VALID saja.

Tanpa penjelasan.
Tanpa teks tambahan.
Tanpa field lain.

Gunakan hanya key ini:
komoditas, berat, lokasi, gagal_panen, grade, tanggal

Contoh:
{{
  "komoditas": "tomat",
  "berat": "30 kg",
  "lokasi": "Bandung",
  "gagal_panen": "5%",
  "grade": "A",
  "tanggal": "29 April 2026"
}}

Teks:
{text}
"""

        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 120
                }
            },
            timeout=60
        )

        if response.status_code != 200:
            return {"error": response.text}

        hasil_text = response.json().get("response", "")
        print("RAW AI:", hasil_text)

        # 🔥 PARSE
        hasil_json = clean_json(hasil_text)

        # 🔥 FALLBACK
        if not hasil_json:
            print("⚠️ fallback aktif")
            hasil_json = fallback_manual(text)

        return hasil_json if hasil_json else {
            "error": "Parsing gagal total",
            "raw": hasil_text
        }

    except Exception as e:
        return {"error": str(e)}