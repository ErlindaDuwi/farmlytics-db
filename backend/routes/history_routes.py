from flask import Blueprint, jsonify
from backend.controllers.history_controller import (
    get_history_data, 
    get_summary,
    delete_history_data,
    update_history_data
)

history_bp = Blueprint('history_bp', __name__)

# 🔹 ambil data history
@history_bp.route('/history', methods=['GET'])
def history():
    return jsonify(get_history_data()), 200

# 🔹 ambil total
@history_bp.route('/history/summary', methods=['GET'])
def summary():
    return jsonify(get_summary()), 200

# 🔹 hapus data
@history_bp.route('/delete_data/<int:id>', methods=['DELETE'])
def delete_data(id):
    return delete_history_data(id)

# 🔹 update data
@history_bp.route('/update_data/<int:id>', methods=['PUT'])
def update_data(id):
    return update_history_data(id)