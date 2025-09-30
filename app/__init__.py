import logging
from flask import Flask, g
from .db import SessionLocal

def create_app() -> Flask:
    app = Flask(__name__)

    # ---- Sessão por request (simples) ----
    @app.before_request
    def _before_request():
        g.db = SessionLocal()

    @app.teardown_request
    def _teardown_request(exception=None):
        db = g.pop("db", None)
        if db is not None:
            try:
                if exception:
                    db.rollback()
                db.close()
            except Exception as e:
                app.logger.error(f"[DB] erro ao fechar sessão: {e}")

    # ---- Logs básicos no STDOUT ----
    gunicorn_logger = logging.getLogger("gunicorn.error")
    if gunicorn_logger.handlers:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # ---- Blueprints ----
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
