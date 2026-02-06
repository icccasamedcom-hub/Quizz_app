# Backend/app.py - Point d'entrée de l'application Flask (version refactorisée)

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from extensions import mongo, init_extensions
from routes import register_blueprints


def create_app():
    """Factory pattern pour créer l'application Flask"""
    app = Flask(__name__, template_folder='../Templates', static_folder='../static')
    
    # Charger la configuration
    app.config.from_object(Config)
    app.config['MONGO_URI'] = Config.MONGO_URI
    app.config['GOOGLE_CLIENT_ID'] = Config.GOOGLE_CLIENT_ID
    app.config['GOOGLE_CLIENT_SECRET'] = Config.GOOGLE_CLIENT_SECRET
    
    # Initialiser les extensions
    init_extensions(app)
    
    # Enregistrer les blueprints
    register_blueprints(app)
    
    # Support Proxy pour Railway/Render (HTTPS)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    return app


# Créer l'application
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)