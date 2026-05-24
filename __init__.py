from flask import Flask
from backend.config import Config
from backend.extensions import db, migrate, cors
from backend.models.lokasi_model import Lokasi
from backend.models.petugas_model import PetugasBangsal
from backend.models.admin_model import Admin
from backend.models.supervisor_model import Supervisor
from backend.models.dinas_model import Dinas

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from backend.models import user_model  # WAJIB ADA

    return app