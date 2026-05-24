import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from backend.models.inputform_model import InputData
from backend.extensions import db

# Setup folder uploads
UPLOAD_FOLDER = 'uploads'

# 🔹 ambil semua data input → untuk history
def get_history_data():
    data = InputData.query.order_by(
        InputData.tanggal.desc()
    ).all()

    result = []

    for item in data:
        result.append({
            "id": item.id,
            "komoditas": item.komoditas,
            "berat": item.berat,

            # ✅ kirim satuan ke flutter
            "satuan": item.satuan if item.satuan else "Kg",

            "lokasi": item.lokasi,
            "gagal": item.gagal,
            "grade": item.grade,
            "cara_input": item.cara_input,
            
            # ✅ INI SANGAT PENTING AGAR FLUTTER TAHU INI BARANG MASUK/KELUAR
            "jenis_transaksi": item.jenis_transaksi if item.jenis_transaksi else "masuk",

            "tanggal": (
                str(item.tanggal)
                if item.tanggal
                else "-"
            ),

            # waktu input
            "created_at": (
                item.created_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
                if item.created_at
                else "-"
            ),

            "foto": (
                item.foto
                if item.foto
                else ""
            )
        })

    return result


# 🔹 total summary
def get_summary():
    total_inputan = db.session.query(
        db.func.count(InputData.id)
    ).scalar() or 0

    total_berat = db.session.query(
        db.func.sum(InputData.berat)
    ).scalar() or 0

    return {
        "total_inputan": total_inputan,
        "total_berat": total_berat
    }


# 🔹 DELETE API: Menghapus data beserta file fotonya
def delete_history_data(id):
    try:
        data = InputData.query.get(id)

        if not data:
            return jsonify({
                "error": "Data tidak ditemukan"
            }), 404

        # Hapus file foto fisik
        if data.foto:
            file_path = os.path.join(
                UPLOAD_FOLDER,
                data.foto
            )

            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(data)
        db.session.commit()

        return jsonify({
            "message": "Data berhasil dihapus"
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "error": str(e)
        }), 500


# 🔹 UPDATE API: Mengubah data dan foto baru
def update_history_data(id):
    try:
        data = InputData.query.get(id)

        if not data:
            return jsonify({
                "error": "Data tidak ditemukan"
            }), 404

        # Tangkap data form baru
        komoditas = request.form.get("komoditas")
        berat = request.form.get("berat")
        satuan = request.form.get("satuan")
        lokasi = request.form.get("lokasi")
        gagal = request.form.get("gagal")
        grade = request.form.get("grade")
        tanggal = request.form.get("tanggal")
        jenis_transaksi = request.form.get("jenis_transaksi") # ✅ tangkap update transaksi

        # Update nilai jika datanya dikirim
        if komoditas:
            data.komoditas = komoditas

        if berat:
            data.berat = float(berat)

        if satuan:
            data.satuan = satuan

        if lokasi:
            data.lokasi = lokasi

        if gagal:
            data.gagal = int(gagal)

        if grade:
            data.grade = grade

        if tanggal:
            data.tanggal = tanggal
            
        if jenis_transaksi:
            data.jenis_transaksi = jenis_transaksi

        # Tangkap file foto baru
        if 'foto' in request.files:
            file_foto = request.files['foto']

            if (
                file_foto and
                file_foto.filename != ''
            ):

                # Hapus foto lama
                if data.foto:
                    old_path = os.path.join(
                        UPLOAD_FOLDER,
                        data.foto
                    )

                    if os.path.exists(old_path):
                        os.remove(old_path)

                # Simpan foto baru
                filename = secure_filename(
                    file_foto.filename
                )

                file_foto.save(
                    os.path.join(
                        UPLOAD_FOLDER,
                        filename
                    )
                )

                # Update nama foto
                data.foto = filename

        db.session.commit()

        return jsonify({
            "message": "Data berhasil diupdate"
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "error": str(e)
        }), 500