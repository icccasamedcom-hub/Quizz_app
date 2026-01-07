# Backend/routes/auth.py - Routes d'authentification

from flask import Blueprint, render_template, redirect, url_for, session
from datetime import datetime
from bson import ObjectId

from extensions import mongo, get_google

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Page d'accueil - redirection si connecté"""
    if 'user' in session:
        return redirect(url_for('quiz.dashboard'))
    return render_template('index.html')


@auth_bp.route('/login')
def login():
    """Initie le processus de connexion OAuth Google"""
    redirect_uri = url_for('auth.authorize', _external=True)
    return get_google().authorize_redirect(redirect_uri)


@auth_bp.route('/authorize')
def authorize():
    """Callback OAuth Google"""
    try:
        token = get_google().authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            # Vérifier si l'utilisateur existe
            user = mongo.db.users.find_one({'email': user_info['email']})
            
            if not user:
                # Créer un nouveau compte
                user_data = {
                    'email': user_info['email'],
                    'name': user_info.get('name', ''),
                    'picture': user_info.get('picture', ''),
                    'created_at': datetime.utcnow(),
                    'last_login': datetime.utcnow()
                }
                result = mongo.db.users.insert_one(user_data)
                user_data['_id'] = result.inserted_id
                user = user_data
            else:
                # Mettre à jour la dernière connexion
                mongo.db.users.update_one(
                    {'_id': user['_id']},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
            
            # Créer la session
            session['user'] = {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'picture': user['picture']
            }
            
            return redirect(url_for('quiz.dashboard'))
    except Exception as e:
        print(f"Erreur d'authentification: {e}")
    
    return redirect(url_for('auth.index'))



@auth_bp.route('/login/dev')
def login_dev():
    """Route de connexion développeur (Bypass OAuth)"""
    # Créer un utilisateur fictif pour le développement
    user_data = {
        'email': 'dev@test.com',
        'name': 'Testeur Mobile',
        'picture': 'https://ui-avatars.com/api/?name=Test+Mobile&background=random',
        'created_at': datetime.utcnow(),
        'last_login': datetime.utcnow(),
        'is_dev': True
    }
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = mongo.db.users.find_one({'email': user_data['email']})
    
    if existing_user:
        user_id = existing_user['_id']
        mongo.db.users.update_one(
            {'_id': user_id},
            {'$set': {'last_login': datetime.utcnow()}}
        )
    else:
        result = mongo.db.users.insert_one(user_data)
        user_id = result.inserted_id
        
    # Créer la session
    session['user'] = {
        'id': str(user_id),
        'email': user_data['email'],
        'name': user_data['name'],
        'picture': user_data['picture']
    }
    
    return redirect(url_for('quiz.dashboard'))


@auth_bp.route('/logout')
def logout():
    """Déconnexion de l'utilisateur"""
    session.pop('user', None)
    return redirect(url_for('auth.index'))
