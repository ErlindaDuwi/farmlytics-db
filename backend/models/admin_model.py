from backend.extensions import db

class Admin(db.Model):
    __tablename__ = 'ADMIN'

    ID_ADMIN = db.Column(db.Integer, primary_key=True)
    NAMA = db.Column(db.String(255))
    USERNAME = db.Column(db.String(100))
    PASSWORD = db.Column(db.String(255))