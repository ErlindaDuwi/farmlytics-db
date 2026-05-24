import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from backend.models.inputform_model import InputData
from backend.extensions import db

UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def create_input():
    try:
        data = request.get_json() if request.is_json else request.form

        def safe_float(value):
            try: return float(value)
            except: return 0.0

        def safe_int(value):
            try: return int(value)
            except: return 0

        komoditas = data.get("komoditas")
        berat = data.get("berat")
        satuan = data.get("satuan")
        lokasi = data.get("lokasi")
        gagal = data.get("gagal")
        grade = data.get("grade")
        cara_input = data.get("cara_input", "manual")
        
        # ✅ TANGKAP STATUS MASUK / KELUAR
        jenis_transaksi = data.get("jenis_transaksi", "masuk") 
        
        tanggal = data.get("tanggal")

        nama_foto = None
        if 'foto' in request.files:
            file_foto = request.files['foto']
            if file_foto and file_foto.filename != '':
                filename = secure_filename(file_foto.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file_foto.save(file_path)
                nama_foto = filename

        new_data = InputData(
            komoditas=komoditas,
            berat=safe_float(berat),
            satuan=satuan,
            lokasi=lokasi,
            gagal=safe_int(gagal),
            grade=grade,
            cara_input=cara_input,
            jenis_transaksi=jenis_transaksi, # ✅ SIMPAN KE DATABASE
            tanggal=tanggal,
            foto=nama_foto
        )

        db.session.add(new_data)
        db.session.commit()

        return jsonify({"message": "Data berhasil disimpan", "id": new_data.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Gagal menyimpan data", "error": str(e)}), 500