# Backend/import_questions.py - Script d'import des questions depuis le fichier JSON

import json
import os
import ssl
import certifi
from pymongo import MongoClient
from datetime import datetime

# Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://icccasamedcom_db_user:j8SGJVHplY9Nt5Sj@cluster0.3v9elbn.mongodb.net/quiz_app?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true')
JSON_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'quiz_icc_mongodb.json')


def import_questions():
    """Importe les questions du fichier JSON vers MongoDB"""
    
    # Connexion à MongoDB avec SSL désactivé pour tests
    try:
        # Créer un contexte SSL qui n'est pas vérifie les certificats
        import ssl
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000
        )
        # Test de connexion
        client.admin.command('ping')
        print("✅ Connexion à MongoDB Atlas réussie!")
    except Exception as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")
        print("\n💡 Vérifiez:")
        print("   1. Que votre IP est autorisée dans MongoDB Atlas (Network Access)")
        print("   2. Que vos identifiants sont correctes")
        print("   3. Que votre pare-feu autorise les connexions sortantes sur le port 27017")
        print(f"\n🔍 URI utilisé: {MONGO_URI[:50]}...")
        return
    
    db = client.get_database()
    
    # Lire le fichier JSON
    print(f"📂 Lecture du fichier: {JSON_FILE}")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    print(f"📋 {len(questions_data)} questions trouvées dans le fichier")
    
    # Vérifier si des questions existent déjà
    existing_count = db.questions.count_documents({})
    if existing_count > 0:
        print(f"⚠️  {existing_count} questions existent déjà dans la base de données")
        response = input("Voulez-vous supprimer les questions existantes et les remplacer ? (o/n): ")
        if response.lower() != 'o':
            print("❌ Import annulé")
            return
        db.questions.delete_many({})
        print("🗑️  Questions existantes supprimées")
    
    # Préparer les questions pour l'import
    questions_to_insert = []
    stats = {
        'categories': {},
        'difficulties': {}
    }
    
    for q in questions_data:
        question = {
            'category': q['category'],
            'difficulty': q['difficulty'],
            'points': q.get('points', 1),
            'question': q['question'],
            'options': q['options'],
            'created_at': datetime.utcnow()
        }
        questions_to_insert.append(question)
        
        # Stats
        cat = q['category']
        diff = q['difficulty']
        stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
        stats['difficulties'][diff] = stats['difficulties'].get(diff, 0) + 1
    
    # Insérer les questions
    result = db.questions.insert_many(questions_to_insert)
    print(f"✅ {len(result.inserted_ids)} questions importées avec succès!")
    
    # Créer les index
    db.questions.create_index('category')
    db.questions.create_index('difficulty')
    db.questions.create_index([('category', 1), ('difficulty', 1)])
    print("📇 Index créés sur 'category' et 'difficulty'")
    
    # Afficher les statistiques
    print("\n📊 Statistiques d'import:")
    print("\nPar catégorie:")
    for cat, count in sorted(stats['categories'].items()):
        print(f"  - {cat}: {count} questions")
    
    print("\nPar niveau de difficulté:")
    for diff, count in sorted(stats['difficulties'].items()):
        print(f"  - {diff}: {count} questions")
    
    # Détail par combinaison catégorie/niveau
    print("\nDétail par catégorie et niveau:")
    pipeline = [
        {'$group': {
            '_id': {'category': '$category', 'difficulty': '$difficulty'},
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id.category': 1, '_id.difficulty': 1}}
    ]
    for doc in db.questions.aggregate(pipeline):
        print(f"  - {doc['_id']['category']} / {doc['_id']['difficulty']}: {doc['count']} questions")
    
    client.close()
    print("\n🎉 Import terminé!")


if __name__ == '__main__':
    import_questions()
