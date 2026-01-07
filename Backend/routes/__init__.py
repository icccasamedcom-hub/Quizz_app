# Backend/routes/__init__.py - Enregistrement des blueprints

from .auth import auth_bp
from .quiz import quiz_bp
from .user import user_bp


def register_blueprints(app):
    """Enregistre tous les blueprints de l'application"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(user_bp)
