import os
from flask import send_from_directory 
from backend import create_app

app = create_app()

# ✅ Mengunci lokasi absolut folder uploads agar Flask tidak tersesat
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# ✅ Menggunakan <path:filename> agar lebih aman membaca ekstensi file
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)