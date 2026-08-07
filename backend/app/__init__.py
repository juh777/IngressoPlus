from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    from app.models import usuario, evento  # noqa: F401 - garante que os models sejam registrados

    from app.controllers.usuario_controller import usuario_bp
    from app.controllers.evento_controller import evento_bp

    app.register_blueprint(usuario_bp, url_prefix="/api/usuarios")
    app.register_blueprint(evento_bp, url_prefix="/api/eventos")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
