import os
from werkzeug.utils import secure_filename
from flask import request, jsonify
from backend.models.inputform_model import InputData
from backend.extensions import db
from backend.services.openclaw_service import parsing_openclaw

import re
from datetime import datetime

# Setup folder uploads
UPLOAD_FOLDER = 'uploads'

#  ambil angka (10 kg → 10, 50% → 50)
def extract_number(value):
    if not value:
        return None
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else None

# 🔥 ambil grade (grade A → A)
def clean_grade(value):
    if not value:
        return None
    match = re.search(r"[A-C]", str(value).upper())
    return match.group() if match else None

# 🔥 parsing tanggal super aman (Support Bahasa Indonesia)
def parse_tanggal(value):
    if not value:
        return None
    
    # Mapping bulan ke angka agar seragam format YYYY-MM-DD
    bulan_map = {
        "januari": "01", "februari": "02", "maret": "03", "april": "04",
        "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
        "september": "09", "oktober": "10", "november": "11", "desember": "12",
        "may": "05", "august": "08", "october": "10", "december": "12" # jaga-jaga english
    }
    
    try:
        val = str(value).strip().lower()
        parts = val.split()
        
        if len(parts) >= 3:
            hari = parts[0].zfill(2)  # 3 -> 03
            bulan_str = parts[1]
            tahun = parts[2]
            
            bulan = bulan_map.get(bulan_str, "01") # default 01 jika typo
            return f"{tahun}-{bulan}-{hari}" # Output: 2026-05-03
            
        return str(value)
    except Exception as e:
        print("⚠️ GAGAL PARSE TANGGAL:", e)
        return str(value)

# ✅ INI YANG DIPANGGIL ROUTE
def save_voice():
    try:
        # 🔹 Tangkap dari form-data karena Flutter ngirim gambar & teks barengan
        text = request.form.get("text")
        
        # Fallback jaga-jaga kalau ngetest via Postman pakai JSON
        if not text:
            req = request.get_json(silent=True)
            if req and "text" in req:
                text = req.get("text")
            else:
                return jsonify({"error": "text tidak ditemukan"}), 400

        print("📥 TEXT MASUK:", text)

        hasil = parsing_openclaw(text)

        print("🤖 HASIL OPENCLAW:", hasil)

        if not hasil or "error" in hasil:
            return jsonify(hasil), 400

        # 🔥 CLEAN DATA SESUAI DB
        komoditas = hasil.get("komoditas")
        berat = extract_number(hasil.get("berat"))
        lokasi = hasil.get("lokasi")
        gagal = extract_number(hasil.get("gagal_panen"))
        grade = clean_grade(hasil.get("grade"))
        tanggal = parse_tanggal(hasil.get("tanggal"))

        print("📦 DATA CLEAN:", komoditas, berat, lokasi, gagal, grade, tanggal)

        # ❗ VALIDASI MINIMAL
        if not komoditas:
            return jsonify({"error": "komoditas kosong"}), 400

        # 🔥 TANGKAP FILE FOTO JIKA ADA
        foto_filename = ""
        if 'foto' in request.files:
            file_foto = request.files['foto']
            if file_foto and file_foto.filename != '':
                # Pastikan folder uploads ada
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                    
                foto_filename = secure_filename(file_foto.filename)
                file_foto.save(os.path.join(UPLOAD_FOLDER, foto_filename))

        # 🔥 SIMPAN KE DATABASE
        new_data = InputData(
            komoditas=komoditas,
            berat=berat,
            lokasi=lokasi,
            gagal=gagal,
            grade=grade,
            tanggal=tanggal,
            cara_input="voice",
            foto=foto_filename # ✅ SIMPAN NAMA FOTO
        )

        db.session.add(new_data)
        db.session.commit()

        return jsonify({
            "message": "Data berhasil disimpan",
            "data": {
                "komoditas": komoditas,
                "berat": berat,
                "lokasi": lokasi,
                "gagal": gagal,
                "grade": grade,
                "tanggal": str(tanggal),
                "cara_input": "voice",
                "foto": foto_filename
            }
        }), 200

    except Exception as e:
        print("❌ CONTROLLER ERROR:", str(e))
        db.session.rollback() # Rollback jika DB gagal
        return jsonify({"error": str(e)}), 500