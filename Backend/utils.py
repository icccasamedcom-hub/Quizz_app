# Backend/utils.py - Fonctions utilitaires

from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """Décorateur pour protéger les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function


def format_duration(seconds):
    """Formate une durée en secondes en format lisible"""
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m"
