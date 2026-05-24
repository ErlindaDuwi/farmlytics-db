from flask import Blueprint
from backend.controllers.input_controller import create_input

input_bp = Blueprint('input_bp', __name__)

@input_bp.route('/input_data', methods=['POST'])
def input_data():
    return create_input()