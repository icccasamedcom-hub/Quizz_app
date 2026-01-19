
# 📚 Quiz App - Application Web Interactive

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Une application web moderne pour créer et partager des quiz interactifs avec authentification Google OAuth 2.0.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Structure du projet](#-structure-du-projet)
- [Prérequis](#-prérequis)
- [Installation](#-guide-dinstallation)
- [Configuration Google OAuth](#-configuration-google-oauth)
- [Structure de la base de données](#-structure-de-la-base-de-données)
- [Sécurité](#-sécurité)
- [Déploiement](#-déploiement-production)
- [Support](#-support-et-maintenance)
- [Licence](#-licence)

## ✨ Fonctionnalités

- ✅ Authentification OAuth 2.0 avec Google
- ✅ Création et gestion de compte utilisateur
- ✅ Liste des quiz disponibles
- ✅ Participation aux quiz avec progression
- ✅ Calcul automatique des scores
- ✅ Affichage des résultats détaillés
- ✅ Historique complet des tentatives
- ✅ Profil utilisateur avec statistiques
- ✅ Design responsive et moderne
- ✅ Protection des routes avec décorateur @login_required

## 📁 Structure du projet

```
quiz-app/
│
├── Backend/
│   ├── app.py                  # Application Flask principale
│   ├── config.py               # Configuration de l'app
│   ├── extensions.py           # Extensions Flask
│   ├── utils.py                # Fonctions utilitaires
│   ├── import_questions.py     # Import des questions
│   └── routes/
│       ├── auth.py             # Routes d'authentification
│       ├── quiz.py             # Routes des quiz
│       └── user.py             # Routes utilisateur
│
├── Templates/
│   ├── base.html               # Template de base
│   ├── index.html              # Page d'accueil
│   ├── dashboard.html          # Tableau de bord
│   ├── quiz_detail.html        # Détail d'un quiz
│   ├── quiz_question.html      # Page de question
│   ├── quiz_results.html       # Résultats du quiz
│   ├── history.html            # Historique des tentatives
│   ├── history_detail.html     # Détail d'une tentative
│   ├── leaderboard.html        # Classement des utilisateurs
│   └── profile.html            # Profil utilisateur
│
├── static/
│   ├── css/
│   │   └── style.css           # Styles personnalisés
│   └── js/
│       ├── app.js              # Scripts généraux
│       ├── quiz_detail.js      # Scripts quiz détail
│       ├── quiz_question.js    # Scripts questions
│
├── docs/
│   ├── Documentation_technique.md
│   └── quiz_icc_mongodb.json   # Données d'exemple
│
├── app.py                      # Point d'entrée (symlink)
├── config.py                   # Configuration globale
├── requirements.txt            # Dépendances Python
├── .env.example                # Exemple de configuration
└── README.md                   # Ce fichier
```

## 🚀 Prérequis

## 1. Prérequis

- Python 3.8 ou supérieur
- MongoDB 4.4 ou supérieur
- Compte Google Cloud Platform

## 2. Configuration Google OAuth

### Étape 1 : Créer un projet Google Cloud
1. Allez sur https://console.cloud.google.com/
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API "Google+ API"

### Étape 2 : Configurer l'écran de consentement OAuth
1. Dans le menu, allez à "APIs & Services" > "OAuth consent screen"
2. Sélectionnez "External" et cliquez sur "Create"
3. Remplissez les informations :
   - Nom de l'application : "Quiz App"
   - Email de support utilisateur : votre email
   - Domaine autorisé : localhost (en développement)
4. Ajoutez les scopes : email, profile, openid
5. Ajoutez vos emails de test

### Étape 3 : Créer les identifiants OAuth
1. Allez à "APIs & Services" > "Credentials"
2. Cliquez sur "Create Credentials" > "OAuth 2.0 Client ID"
3. Type d'application : "Web application"
4. Nom : "Quiz App Web Client"
5. URIs de redirection autorisés :
   - http://localhost:5000/authorize
   - http://127.0.0.1:5000/authorize
6. Notez le Client ID et le Client Secret

## 3. Installation de l'application

### Étape 1 : Cloner et configurer
```bash
# Créer le répertoire du projet
mkdir quiz-app
cd quiz-app

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur Mac/Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 2 : Configurer les variables d'environnement
```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer .env avec vos valeurs
# SECRET_KEY : générer une clé aléatoire (ex: python -c "import secrets; print(secrets.token_hex(32))")
# GOOGLE_CLIENT_ID : votre Client ID Google
# GOOGLE_CLIENT_SECRET : votre Client Secret Google
# MONGO_URI : URI de connexion MongoDB
```

### Étape 3 : Démarrer MongoDB
```bash
# Sur Windows (si installé en tant que service)
net start MongoDB

# Sur Mac (avec Homebrew)
brew services start mongodb-community

# Sur Linux (avec systemd)
sudo systemctl start mongod

# Ou avec Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Étape 4 : Initialiser la base de données
```bash
# Démarrer l'application
python app.py

# Dans un navigateur, accédez à :
# http://localhost:5000/init-sample-data
# Cela créera des quiz d'exemple
```

### Étape 5 : Lancer l'application
```bash
python app.py
```

L'application sera accessible à : http://localhost:5000



## 4. Fonctionnalités implémentées

✅ Authentification OAuth 2.0 avec Google
✅ Création et gestion de compte utilisateur
✅ Liste des quiz disponibles
✅ Participation aux quiz avec progression
✅ Calcul automatique des scores
✅ Affichage des résultats détaillés
✅ Historique complet des tentatives
✅ Profil utilisateur avec statistiques
✅ Design responsive et moderne
✅ Protection des routes avec décorateur @login_required

## 🔒 Sécurité

- Les mots de passe ne sont pas stockés (OAuth uniquement)
- Les sessions sont sécurisées avec une clé secrète
- Protection CSRF native de Flask
- Validation des entrées utilisateur
- Requêtes MongoDB paramétrées contre les injections

## 5. Tests

Pour tester l'application :

1. Créez un compte Google de test
2. Connectez-vous à l'application
3. Testez chaque fonctionnalité :
   - Connexion/Déconnexion
   - Participation à un quiz
   - Consultation de l'historique
   - Visualisation du profil

## 6. Déploiement (Production)

Pour déployer en production :

1. Utilisez un serveur WSGI comme Gunicorn
2. Configurez un reverse proxy (Nginx)
3. Utilisez HTTPS avec Let's Encrypt
4. Mettez à jour les URIs de redirection Google OAuth
5. Utilisez MongoDB Atlas pour la base de données
6. Configurez les variables d'environnement sur le serveur

Exemple avec Gunicorn :
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 7. Support et Maintenance

- Vérifiez régulièrement les logs
- Sauvegardez la base de données MongoDB
- Mettez à jour les dépendances Python
- Surveillez l'utilisation de l'API Google OAuth

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
