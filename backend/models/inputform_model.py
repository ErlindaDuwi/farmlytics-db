from backend.extensions import db
from datetime import datetime

class InputData(db.Model):
    __tablename__ = 'input_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    komoditas = db.Column(db.String(100), nullable=False)
    berat = db.Column(db.Float, nullable=True)
    satuan = db.Column(db.String(20))
    lokasi = db.Column(db.String(150), nullable=True)
    gagal = db.Column(db.Integer, nullable=True)
    grade = db.Column(db.Enum('A', 'B', 'C'), nullable=True)
    cara_input = db.Column(db.String(20), default='manual')
    
    # ✅ INI YANG BIKIN ERROR (KEMARIN HILANG DARI FILEMU)
    jenis_transaksi = db.Column(db.String(20), default='masuk') 
    
    tanggal = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    foto = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<InputData {self.komoditas}>"