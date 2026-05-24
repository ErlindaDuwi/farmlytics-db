from backend import db

class Lokasi(db.Model):
    __tablename__ = 'LOKASI'

    ID_LOKASI = db.Column(db.Integer, primary_key=True)
    NAMA_LOKASI = db.Column(db.String(255))