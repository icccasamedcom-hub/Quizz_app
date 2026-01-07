# Backend/config.py - Configuration de l'application

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


class Config:
    """Configuration de l'application Flask"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'votre-clé-secrète-très-sécurisée')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/quiz_app')
    
    # OAuth Google
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Quiz settings
    QUESTIONS_PER_QUIZ = 10
    
    # Catégories et niveaux disponibles
    CATEGORIES = ['Vision', 'Valeurs', 'Mission']
    DIFFICULTIES = ['Facile', 'Intermédiaire', 'Difficile']
