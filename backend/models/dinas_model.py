from backend.extensions import db

class Dinas(db.Model):
    __tablename__ = 'dinas'

    ID_DINAS = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NAMA_INSTANSI = db.Column(db.String(255), nullable=False)
    USERNAME = db.Column(db.String(100), unique=True, nullable=False)
    EMAIL = db.Column(db.String(255), nullable=True)
    PASSWORD = db.Column(db.String(255), nullable=False)
    NO_HP = db.Column(db.String(15), nullable=True)
    
    # ✅ Kolom foto pastikan huruf kecil agar dikenali saat upload
    foto = db.Column(db.String(255), nullable=True) 

    def __repr__(self):
        return f"<Dinas {self.USERNAME}>"