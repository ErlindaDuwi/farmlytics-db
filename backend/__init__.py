from flask import Flask
from flask_cors import CORS
from backend.extensions import db

def create_app():
    app = Flask(__name__)

    # Load config
    app.config.from_object('backend.config.Config')

    # Init extensions
    db.init_app(app)
    CORS(app)

    from backend.routes.auth_routes import auth_bp
    from backend.routes.input_routes import input_bp
    from backend.routes.history_routes import history_bp
    from backend.routes.voice_routes import voice_bp
    from backend.routes.user_routes import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(input_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(voice_bp)
    app.register_blueprint(user_bp)

    return app