from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models.admin_model import Admin
from backend.models.petugas_model import PetugasBangsal
from backend.models.supervisor_model import Supervisor
from backend.models.dinas_model import Dinas
import traceback

user_bp = Blueprint('user_routes', __name__)

# ==========================================
# HELPER PINTAR: Mencari Kolom Secara Otomatis
# ==========================================
def get_id_aman(obj):
    for col in ['ID_PETUGAS_BANGSAL', 'id_petugas_bangsal', 'ID_ADMIN', 'id_admin', 'ID_SUPERVISOR', 'id_supervisor', 'ID_DINAS', 'id_dinas', 'id', 'ID']:
        if hasattr(obj, col): return getattr(obj, col)
    return 0

def get_nama_aman(obj):
    for col in ['NAMA', 'nama', 'NAMA_INSTANSI', 'nama_instansi', 'USERNAME', 'username']:
        if hasattr(obj, col): return getattr(obj, col)
    return "-"

def get_col_aman(obj, col_upper, col_lower):
    return getattr(obj, col_upper, getattr(obj, col_lower, ''))

def get_model_and_id_col(role):
    if role == "Admin": return Admin, "ID_ADMIN"
    if role == "Petugas": return PetugasBangsal, "ID_PETUGAS_BANGSAL"
    if role == "Supervisor": return Supervisor, "ID_SUPERVISOR"
    if role == "Dinas": return Dinas, "ID_DINAS"
    return None, None

# ==========================================
# GET: AMBIL SEMUA USER (DIJAMIN BEBAS 500)
# ==========================================
@user_bp.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = []
        for a in Admin.query.all():
            users.append({"id": get_id_aman(a), "name": get_nama_aman(a), "username": get_col_aman(a, 'USERNAME', 'username'), "email": get_col_aman(a, 'EMAIL', 'email'), "phone": get_col_aman(a, 'NO_HP', 'no_hp'), "password": get_col_aman(a, 'PASSWORD', 'password'), "foto": get_col_aman(a, 'FOTO', 'foto'), "role": "Admin"})
            
        for p in PetugasBangsal.query.all():
            users.append({"id": get_id_aman(p), "name": get_nama_aman(p), "username": get_col_aman(p, 'USERNAME', 'username'), "email": get_col_aman(p, 'EMAIL', 'email'), "phone": get_col_aman(p, 'NO_HP', 'no_hp'), "password": get_col_aman(p, 'PASSWORD', 'password'), "foto": get_col_aman(p, 'FOTO', 'foto'), "role": "Petugas"})
            
        for s in Supervisor.query.all():
            users.append({"id": get_id_aman(s), "name": get_nama_aman(s), "username": get_col_aman(s, 'USERNAME', 'username'), "email": get_col_aman(s, 'EMAIL', 'email'), "phone": get_col_aman(s, 'NO_HP', 'no_hp'), "password": get_col_aman(s, 'PASSWORD', 'password'), "foto": get_col_aman(s, 'FOTO', 'foto'), "role": "Supervisor"})
            
        for d in Dinas.query.all():
            users.append({"id": get_id_aman(d), "name": get_nama_aman(d), "username": get_col_aman(d, 'USERNAME', 'username'), "email": get_col_aman(d, 'EMAIL', 'email'), "phone": get_col_aman(d, 'NO_HP', 'no_hp'), "password": get_col_aman(d, 'PASSWORD', 'password'), "foto": get_col_aman(d, 'FOTO', 'foto'), "role": "Dinas"})
            
        return jsonify(users), 200
    except Exception as e:
        print("ERROR GET USERS:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# ==========================================
# POST, PUT, DELETE (TETAP SAMA)
# ==========================================
@user_bp.route('/api/users', methods=['POST'])
def add_user():
    data = request.json
    role = data.get('role')
    Model, _ = get_model_and_id_col(role)
    if not Model: return jsonify({"error": "Role tidak valid"}), 400
        
    try:
        new_user = Model()
        if hasattr(new_user, 'USERNAME'): new_user.USERNAME = data.get('username')
        if hasattr(new_user, 'PASSWORD'): new_user.PASSWORD = data.get('password')
        if hasattr(new_user, 'EMAIL'): new_user.EMAIL = data.get('email')
        
        if hasattr(new_user, 'no_hp'): new_user.no_hp = data.get('phone')
        elif hasattr(new_user, 'NO_HP'): new_user.NO_HP = data.get('phone')
        
        if role == "Dinas" and hasattr(new_user, 'NAMA_INSTANSI'): new_user.NAMA_INSTANSI = data.get('name')
        elif hasattr(new_user, 'NAMA'): new_user.NAMA = data.get('name')
            
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User berhasil ditambahkan"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Gagal simpan (mungkin username duplikat)"}), 500

@user_bp.route('/api/users/<int:id>/<role>', methods=['PUT'])
def update_user(id, role):
    data = request.json
    Model, id_col = get_model_and_id_col(role)
    if not Model: return jsonify({"error": "Role tidak valid"}), 400
        
    try:
        user = Model.query.filter(getattr(Model, id_col) == id).first()
        if not user: return jsonify({"error": "User tidak ditemukan"}), 404
            
        if hasattr(user, 'USERNAME'): user.USERNAME = data.get('username')
        if hasattr(user, 'PASSWORD'): user.PASSWORD = data.get('password')
        if hasattr(user, 'EMAIL'): user.EMAIL = data.get('email')
        
        if hasattr(user, 'no_hp'): user.no_hp = data.get('phone')
        elif hasattr(user, 'NO_HP'): user.NO_HP = data.get('phone')
        
        if role == "Dinas" and hasattr(user, 'NAMA_INSTANSI'): user.NAMA_INSTANSI = data.get('name')
        elif hasattr(user, 'NAMA'): user.NAMA = data.get('name')
            
        db.session.commit()
        return jsonify({"message": "User berhasil diupdate"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route('/api/users/<int:id>/<role>', methods=['DELETE'])
def delete_user(id, role):
    Model, id_col = get_model_and_id_col(role)
    if not Model: return jsonify({"error": "Role tidak valid"}), 400
        
    try:
        user = Model.query.filter(getattr(Model, id_col) == id).first()
        if not user: return jsonify({"error": "User tidak ditemukan"}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User berhasil dihapus"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500