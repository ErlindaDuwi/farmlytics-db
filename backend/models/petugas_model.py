from backend.extensions import db

class PetugasBangsal(db.Model):
    __tablename__ = 'PETUGAS_BANGSAL'

    ID_PETUGAS_BANGSAL = db.Column(db.Integer, primary_key=True)
    ID_LOKASI = db.Column(db.Integer)
    EMAIL = db.Column(db.String(255))   
    USERNAME = db.Column(db.String(100))
    PASSWORD = db.Column(db.String(255))
    no_hp = db.Column(db.String(15))
    foto = db.Column(db.String(255))