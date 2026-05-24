from flask import Blueprint
from backend.controllers.voice_controller import save_voice

voice_bp = Blueprint('voice_bp', __name__)

@voice_bp.route('/input', methods=['POST'])
def input_voice():
    return save_voice()