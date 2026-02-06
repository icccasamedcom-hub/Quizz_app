# Backend/routes/user.py - Routes utilisateur (profil, historique, classement)

from flask import Blueprint, render_template, redirect, url_for, session
from datetime import datetime
from bson import ObjectId

from extensions import mongo
from utils import login_required

user_bp = Blueprint('user', __name__)


@user_bp.route('/history')
@login_required
def history():
    """Historique des quiz de l'utilisateur"""
    user_id = ObjectId(session['user']['id'])
    attempts = list(mongo.db.attempts.find({
        'user_id': user_id,
        'completed': True
    }).sort('completed_at', -1))
    
    return render_template('history.html', attempts=attempts)


@user_bp.route('/history/<attempt_id>')
@login_required
def history_detail(attempt_id):
    """Détail d'une tentative passée"""
    attempt = mongo.db.attempts.find_one({
        '_id': ObjectId(attempt_id),
        'user_id': ObjectId(session['user']['id']),
        'completed': True
    })
    
    if not attempt:
        return redirect(url_for('user.history'))
    
    # Reconstruire les résultats détaillés
    detailed_results = []
    for i, question_id in enumerate(attempt['question_ids']):
        question = mongo.db.questions.find_one({'_id': question_id})
        user_answer = attempt['answers'][i] if i < len(attempt['answers']) else None
        
        # Trouver la bonne réponse
        correct_answer = None
        for option in question['options']:
            if option.get('isCorrect'):
                correct_answer = option['text']
                break
        
        detailed_results.append({
            'question': question['question'],
            'options': question['options'],
            'user_answer': user_answer['selected_answer'] if user_answer else None,
            'correct_answer': correct_answer,
            'is_correct': user_answer.get('is_correct', False) if user_answer else False
        })
    
    return render_template('history_detail.html',
                          attempt=attempt,
                          detailed_results=detailed_results)


@user_bp.route('/profile')
@login_required
def profile():
    """Profil de l'utilisateur avec statistiques"""
    user_id = ObjectId(session['user']['id'])
    user = mongo.db.users.find_one({'_id': user_id})
    
    # Statistiques globales
    attempts = list(mongo.db.attempts.find({
        'user_id': user_id,
        'completed': True
    }))
    
    stats = {
        'total_attempts': len(attempts),
        'average_score': sum(a['score'] for a in attempts) / len(attempts) if attempts else 0,
        'best_score': max((a['score'] for a in attempts), default=0),
        'total_time': sum(a.get('duration_seconds', 0) for a in attempts),
        'perfect_scores': sum(1 for a in attempts if a.get('score', 0) == 100)
    }
    
    # Stats par catégorie
    category_stats = {}
    for attempt in attempts:
        cat = attempt.get('category', 'Autre')
        if cat not in category_stats:
            category_stats[cat] = {'count': 0, 'total_score': 0}
        category_stats[cat]['count'] += 1
        category_stats[cat]['total_score'] += attempt.get('score', 0)
    
    for cat in category_stats:
        category_stats[cat]['average'] = (
            category_stats[cat]['total_score'] / category_stats[cat]['count']
        )
    
    return render_template('profile.html', user=user, stats=stats, category_stats=category_stats)


@user_bp.route('/leaderboard')
@login_required
def leaderboard():
    """Classement des utilisateurs"""
    users = list(mongo.db.users.find())
    
    leaderboard_data = []
    for user in users:
        user_id = user['_id']
        attempts = list(mongo.db.attempts.find({
            'user_id': user_id,
            'completed': True
        }))
        
        if attempts:
            total_attempts = len(attempts)
            average_score = sum(a['score'] for a in attempts) / total_attempts
            best_score = max((a['score'] for a in attempts), default=0)
            
            # Ratio simple : Score moyen (pas de bonus arbitraire)
            performance_index = average_score
            
            leaderboard_data.append({
                'name': user['name'],
                'picture': user['picture'],
                'total_attempts': total_attempts,
                'average_score': average_score,
                'best_score': best_score,
                'performance_index': performance_index
            })
    
    # Trier par index de performance (décroissant)
    leaderboard_data.sort(key=lambda x: (x['performance_index'], x['total_attempts']), reverse=True)
    
    return render_template('leaderboard.html', leaderboard=leaderboard_data)
