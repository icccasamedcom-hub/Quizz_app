# Backend/extensions.py - Extensions Flask (MongoDB, OAuth)

from flask_pymongo import PyMongo
from authlib.integrations.flask_client import OAuth

# Instances des extensions
mongo = PyMongo()
oauth = OAuth()


def init_extensions(app):
    """Initialise les extensions Flask"""
    # MongoDB
    mongo.init_app(app)
    
    # OAuth
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )


def get_google():
    """Retourne le client OAuth Google"""
    return oauth.google
