import os
from flask import request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from backend.models.admin_model import Admin
from backend.models.petugas_model import PetugasBangsal
from backend.models.supervisor_model import Supervisor
from backend.models.dinas_model import Dinas
from backend.extensions import db

class AuthController:

    # ============================================================
    # KONFIGURASI UPLOAD
    # ============================================================
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', '..', 'uploads')

    def __init__(self):
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)

    # ============================================================
    # HELPER CARI USER BERDASARKAN USERNAME
    # ============================================================
    def find_user_by_username(self, username):
        user = PetugasBangsal.query.filter_by(USERNAME=username).first()
        if user: return user, "Petugas"
        
        user = Supervisor.query.filter_by(USERNAME=username).first()
        if user: return user, "Supervisor"
        
        user = Dinas.query.filter_by(USERNAME=username).first()
        if user: return user, "Dinas"
        
        user = Admin.query.filter_by(USERNAME=username).first()
        if user: return user, "Admin"
        
        return None, None

    # ✅ KUNCI PERBAIKAN 1: Pendeteksi otomatis huruf FOTO besar / foto kecil
    def _get_user_foto(self, user):
        if hasattr(user, 'foto') and user.foto:
            return user.foto
        if hasattr(user, 'FOTO') and user.FOTO:
            return user.FOTO
        return ""

    # ✅ KUNCI PERBAIKAN 2: Penyimpan otomatis ke huruf FOTO besar / foto kecil
    def _set_user_foto(self, user, filename):
        if hasattr(user, 'FOTO'):
            user.FOTO = filename
        else:
            user.foto = filename

    # ============================================================
    # LOGIN
    # ============================================================
    def login(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")

        if not username or not password or not role:
            return jsonify({"status": "error", "message": "Data login tidak lengkap"}), 400

        user = None
        if role == "Admin":
            user = Admin.query.filter_by(USERNAME=username, PASSWORD=password).first()
        elif role == "Petugas":
            user = PetugasBangsal.query.filter_by(USERNAME=username, PASSWORD=password).first()
        elif role == "Supervisor":
            user = Supervisor.query.filter_by(USERNAME=username, PASSWORD=password).first()
        elif role == "Dinas":
            user = Dinas.query.filter_by(USERNAME=username, PASSWORD=password).first()

        if user:
            return jsonify({
                "status": "success",
                "message": f"Login {role} berhasil",
                "role": role,
                "username": user.USERNAME,
                "email": getattr(user, "EMAIL", ""),
                
                # ✅ Menggunakan Helper Pintar
                "foto": self._get_user_foto(user), 
                "no_hp": getattr(user, "NO_HP", "")
            }), 200

        return jsonify({"status": "error", "message": "Username / Password salah"}), 401

    # ============================================================
    # GET PROFILE
    # ============================================================
    def get_profile(self, username):
        user, role = self.find_user_by_username(username)
        if not user:
            return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

        return jsonify({
            "status": "success",
            "username": user.USERNAME,
            "email": getattr(user, "EMAIL", ""),
            "no_hp": getattr(user, "NO_HP", ""),
            
            # ✅ Menggunakan Helper Pintar
            "foto": self._get_user_foto(user), 
            "role": role
        }), 200

    # ============================================================
    # UPLOAD FOTO
    # ============================================================
    def upload_foto(self, username):
        if 'foto' not in request.files:
            return jsonify({"status": "error", "message": "File tidak ditemukan"}), 400
            
        file = request.files['foto']
        if file.filename == '':
            return jsonify({"status": "error", "message": "File kosong"}), 400

        user, role = self.find_user_by_username(username)
        if not user:
            return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

        # Hapus foto lama
        old_photo = self._get_user_foto(user)
        if old_photo:
            old_path = os.path.join(self.UPLOAD_FOLDER, old_photo)
            if os.path.exists(old_path):
                os.remove(old_path)

        # Simpan foto baru
        extension = file.filename.split('.')[-1]
        filename = secure_filename(f"{role}_{username}.{extension}")
        filepath = os.path.join(self.UPLOAD_FOLDER, filename)
        file.save(filepath)

        # ✅ Menyimpan nama foto dengan Helper Pintar
        self._set_user_foto(user, filename)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Upload foto berhasil",
            "path": filename
        }), 200

    # ============================================================
    # GET FOTO
    # ============================================================
    def get_foto(self, filename):
        return send_from_directory(self.UPLOAD_FOLDER, filename)

    # ============================================================
    # DELETE FOTO
    # ============================================================
    def delete_foto(self, username):
        user, role = self.find_user_by_username(username)
        if not user:
            return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

        old_photo = self._get_user_foto(user)
        if old_photo:
            filepath = os.path.join(self.UPLOAD_FOLDER, old_photo)
            if os.path.exists(filepath):
                os.remove(filepath)

        self._set_user_foto(user, "")
        db.session.commit()

        return jsonify({"status": "success", "message": "Foto berhasil dihapus"}), 200

    # ============================================================
    # UPDATE ACCOUNT
    # ============================================================
    def update_account(self):
        data = request.get_json()

        username_lama = data.get("username")
        email = data.get("email")
        username_baru = data.get("new_username")
        
        # ✅ Ambil data phone dari Flutter
        phone = data.get("phone")
        if not phone:
            phone = data.get("no_hp")
            
        password = data.get("password")

        if not username_lama:
            return jsonify({"status": "error", "message": "Username wajib dikirim"}), 400

        user, role = self.find_user_by_username(username_lama)
        if not user:
            return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

        # ================= CEK USERNAME DUPLIKAT =================
        if username_baru and username_baru != username_lama:
            existing_user, _ = self.find_user_by_username(username_baru)
            if existing_user:
                return jsonify({"status": "error", "message": "Username sudah digunakan"}), 400

        # ================= UPDATE EMAIL =================
        if email:
            if hasattr(user, 'EMAIL'): user.EMAIL = email
            elif hasattr(user, 'email'): user.email = email

        # ================= UPDATE USERNAME =================
        if username_baru:
            if hasattr(user, 'USERNAME'): user.USERNAME = username_baru
            elif hasattr(user, 'username'): user.username = username_baru

        # ================= UPDATE NO HP (Anti Error) =================
        # ✅ Otomatis mendeteksi apakah database memakai huruf besar atau kecil
        if phone:
            if hasattr(user, 'NO_HP'): 
                user.NO_HP = phone
            elif hasattr(user, 'no_hp'): 
                user.no_hp = phone

        # ================= UPDATE PASSWORD =================
        if password:
            if hasattr(user, 'PASSWORD'): user.PASSWORD = password
            elif hasattr(user, 'password'): user.password = password

        db.session.commit()

        # Ambil username terakhir untuk dikembalikan ke Flutter
        final_username = getattr(user, 'USERNAME', getattr(user, 'username', username_lama))

        return jsonify({
            "status": "success",
            "message": "Data account berhasil diperbarui",
            "username": final_username
        }), 200

    # ============================================================
    # GET ACCOUNT
    # ============================================================
    def get_account(self, username):
        user, role = self.find_user_by_username(username)
        if not user:
            return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404

        return jsonify({
            "status": "success",
            "username": user.USERNAME,
            "email": getattr(user, 'EMAIL', ""),
            "no_hp": getattr(user, 'NO_HP', ""),
            "foto": self._get_user_foto(user),
            "role": role
        }), 200