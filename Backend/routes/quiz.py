# Backend/routes/quiz.py - Routes du quiz

import random
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from datetime import datetime
from bson import ObjectId

from extensions import mongo
from utils import login_required
from config import Config

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord principal"""
    user_id = ObjectId(session['user']['id'])
    attempts = list(mongo.db.attempts.find({
        'user_id': user_id,
        'completed': True
    }))
    
    stats = {
        'total_attempts': len(attempts),
        'average_score': sum(a['score'] for a in attempts) / len(attempts) if attempts else 0,
        'best_score': max((a['score'] for a in attempts), default=0)
    }
    
    # Statistiques par catégorie
    category_stats = {}
    for category in Config.CATEGORIES:
        cat_attempts = [a for a in attempts if a.get('category') == category]
        if cat_attempts:
            category_stats[category] = {
                'count': len(cat_attempts),
                'average': sum(a['score'] for a in cat_attempts) / len(cat_attempts)
            }
    
    return render_template('dashboard.html', stats=stats, category_stats=category_stats)


@quiz_bp.route('/quiz/select')
@login_required
def quiz_select():
    """Page de sélection catégorie et niveau"""
    # Compter les questions par catégorie et niveau
    categories_data = []
    for category in Config.CATEGORIES:
        cat_data = {
            'name': category,
            'levels': {}
        }
        for difficulty in Config.DIFFICULTIES:
            count = mongo.db.questions.count_documents({
                'category': category,
                'difficulty': difficulty
            })
            cat_data['levels'][difficulty] = count
        cat_data['total'] = sum(cat_data['levels'].values())
        categories_data.append(cat_data)
    
    return render_template('quiz_select.html', 
                          categories=categories_data,
                          difficulties=Config.DIFFICULTIES)


@quiz_bp.route('/api/quiz/start', methods=['POST'])
@login_required
def start_quiz():
    """Démarre un nouveau quiz avec catégorie et niveau sélectionnés"""
    data = request.json
    category = data.get('category')
    difficulty = data.get('difficulty')
    
    # Validation
    if category not in Config.CATEGORIES:
        return jsonify({'error': 'Catégorie invalide'}), 400
    if difficulty not in Config.DIFFICULTIES:
        return jsonify({'error': 'Niveau invalide'}), 400
    
    # Récupérer les questions correspondantes
    questions = list(mongo.db.questions.find({
        'category': category,
        'difficulty': difficulty
    }))
    
    if len(questions) < Config.QUESTIONS_PER_QUIZ:
        return jsonify({
            'error': f'Pas assez de questions disponibles ({len(questions)} trouvées, {Config.QUESTIONS_PER_QUIZ} requises)'
        }), 400
    
    # Sélectionner 10 questions aléatoires
    selected_questions = random.sample(questions, Config.QUESTIONS_PER_QUIZ)
    
    # Créer la tentative
    attempt = {
        'user_id': ObjectId(session['user']['id']),
        'category': category,
        'difficulty': difficulty,
        'question_ids': [q['_id'] for q in selected_questions],
        'started_at': datetime.utcnow(),
        'completed': False,
        'current_question': 0,
        'answers': []
    }
    
    result = mongo.db.attempts.insert_one(attempt)
    
    return jsonify({'attempt_id': str(result.inserted_id)})


@quiz_bp.route('/quiz/attempt/<attempt_id>')
@login_required
def quiz_attempt(attempt_id):
    """Affiche la question courante du quiz"""
    attempt = mongo.db.attempts.find_one({
        '_id': ObjectId(attempt_id),
        'user_id': ObjectId(session['user']['id'])
    })
    
    if not attempt or attempt['completed']:
        return redirect(url_for('quiz.dashboard'))
    
    current_idx = attempt['current_question']
    total_questions = len(attempt['question_ids'])
    
    if current_idx >= total_questions:
        return redirect(url_for('quiz.complete_quiz', attempt_id=attempt_id))
    
    # Récupérer la question courante
    question_id = attempt['question_ids'][current_idx]
    question = mongo.db.questions.find_one({'_id': question_id})
    
    if not question:
        return redirect(url_for('quiz.dashboard'))
    
    progress_percentage = int((current_idx + 1) / total_questions * 100)
    
    return render_template('quiz_question.html',
                          attempt=attempt,
                          question=question,
                          question_number=current_idx + 1,
                          total_questions=total_questions,
                          progress_percentage=progress_percentage)


@quiz_bp.route('/quiz/attempt/<attempt_id>/previous', methods=['POST'])
@login_required
def previous_question(attempt_id):
    """Revient à la question précédente"""
    attempt = mongo.db.attempts.find_one({
        '_id': ObjectId(attempt_id),
        'user_id': ObjectId(session['user']['id'])
    })
    
    if not attempt or attempt['completed']:
        return jsonify({'error': 'Tentative invalide'}), 400
    
    # Vérifier si on peut reculer
    if attempt['current_question'] > 0:
        mongo.db.attempts.update_one(
            {'_id': ObjectId(attempt_id)},
            {'$inc': {'current_question': -1}}
        )
        return jsonify({'success': True})
    
    return jsonify({'error': 'Impossible de reculer'}), 400


@quiz_bp.route('/quiz/attempt/<attempt_id>/answer', methods=['POST'])
@login_required
def submit_answer(attempt_id):
    """Soumet une réponse à une question"""
    data = request.json
    attempt = mongo.db.attempts.find_one({
        '_id': ObjectId(attempt_id),
        'user_id': ObjectId(session['user']['id'])
    })
    
    if not attempt or attempt['completed']:
        return jsonify({'error': 'Tentative invalide'}), 400
    
    # Récupérer la question pour vérifier la réponse
    current_idx = attempt['current_question']
    question_id = attempt['question_ids'][current_idx]
    question = mongo.db.questions.find_one({'_id': question_id})
    
    # Trouver la bonne réponse
    correct_answer = None
    for option in question['options']:
        if option.get('isCorrect'):
            correct_answer = option['text']
            break
            
    # Vérifier si on met à jour une réponse existante ou si on en ajoute une nouvelle
    answer = {
        'question_id': str(question_id),
        'selected_answer': data['answer'],
        'correct_answer': correct_answer,
        'is_correct': data['answer'] == correct_answer,
        'answered_at': datetime.utcnow()
    }
    
    # Si l'utilisateur répond à nouveau à la même question (cas du retour arrière)
    # On doit mettre à jour la réponse dans le tableau 'answers' si elle existe déjà pour cet index
    # Note: Dans cette implémentation simple, 'answers' est une liste append-only.
    # Pour gérer le retour arrière proprement, on devrait idéalement utiliser un index ou map par question_id.
    # Ici, nous allons simplement mettre à jour answer à l'index current_idx si possible, sinon append.
    
    if current_idx < len(attempt['answers']):
        # Mise à jour réponse existante
        mongo.db.attempts.update_one(
            {'_id': ObjectId(attempt_id)},
            {
                '$set': {f'answers.{current_idx}': answer},
                '$inc': {'current_question': 1}
            }
        )
    else:
        # Nouvelle réponse
        mongo.db.attempts.update_one(
            {'_id': ObjectId(attempt_id)},
            {
                '$push': {'answers': answer},
                '$inc': {'current_question': 1}
            }
        )
    
    return jsonify({'success': True, 'is_correct': answer['is_correct']})


@quiz_bp.route('/quiz/attempt/<attempt_id>/complete')
@login_required
def complete_quiz(attempt_id):
    """Affiche les résultats du quiz"""
    attempt = mongo.db.attempts.find_one({
        '_id': ObjectId(attempt_id),
        'user_id': ObjectId(session['user']['id'])
    })
    
    if not attempt:
        return redirect(url_for('quiz.dashboard'))
    
    # Calculer le score
    total_questions = len(attempt['question_ids'])
    correct_answers = sum(1 for a in attempt['answers'] if a.get('is_correct'))
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Calculer la durée
    duration = datetime.utcnow() - attempt['started_at']
    
    # Mettre à jour la tentative si pas déjà complétée
    if not attempt['completed']:
        mongo.db.attempts.update_one(
            {'_id': ObjectId(attempt_id)},
            {
                '$set': {
                    'completed': True,
                    'completed_at': datetime.utcnow(),
                    'score': score,
                    'correct_answers': correct_answers,
                    'total_questions': total_questions,
                    'duration_seconds': int(duration.total_seconds())
                }
            }
        )
    
    # Construire les résultats détaillés
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
            'is_correct': user_answer['is_correct'] if user_answer else False
        })
    
    return render_template('quiz_results.html',
                          attempt=attempt,
                          score=score,
                          correct_answers=correct_answers,
                          total_questions=total_questions,
                          duration=duration,
                          detailed_results=detailed_results)
