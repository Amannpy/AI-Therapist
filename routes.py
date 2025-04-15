from flask import render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app import app, db
from models import User, Assessment, ChatMessage, EmotionRecord
# Switch from OpenAI to Gemini
from utils.gemini_helper import get_ai_response
from utils.emotion_detection import detect_emotion
from utils.rag import get_therapy_resources
from utils.crisis_detection import detect_crisis
import json
from datetime import datetime, timedelta

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=True)
        flash('Login successful!', 'success')
        
        # Check if user needs assessment
        last_assessment = Assessment.query.filter_by(user_id=user.id).order_by(Assessment.created_at.desc()).first()
        if not last_assessment or (datetime.utcnow() - last_assessment.created_at) > timedelta(days=7):
            return redirect(url_for('assessment'))
        
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords must match', 'danger')
            return redirect(url_for('register'))
            
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's assessment history
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).all()
    
    # Get emotion records for charts
    emotion_records = EmotionRecord.query.filter_by(user_id=current_user.id).order_by(EmotionRecord.created_at.desc()).limit(30).all()
    
    # Get average assessment score
    avg_score = 0
    if assessments:
        avg_score = sum([a.score for a in assessments]) / len(assessments)
    
    # Format data for chart.js
    assessment_dates = [a.created_at.strftime('%Y-%m-%d') for a in assessments]
    assessment_scores = [a.score for a in assessments]
    
    emotion_data = {}
    for record in emotion_records:
        date = record.created_at.strftime('%Y-%m-%d')
        if date not in emotion_data:
            emotion_data[date] = {}
        
        if record.emotion not in emotion_data[date]:
            emotion_data[date][record.emotion] = 0
        
        emotion_data[date][record.emotion] += record.intensity

    return render_template(
        'dashboard.html', 
        assessments=assessments,
        avg_score=avg_score,
        assessment_dates=json.dumps(assessment_dates),
        assessment_scores=json.dumps(assessment_scores),
        emotion_data=json.dumps(emotion_data)
    )

@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    if request.method == 'POST':
        # Process assessment form
        answers = {}
        score = 0
        
        # MHQoL-7D questions are numbered 1-7
        for i in range(1, 8):
            q_key = f'q{i}'
            answer = request.form.get(q_key)
            if answer:
                answers[q_key] = int(answer)
                score += int(answer)
        
        # Normalize score (0-100)
        normalized_score = (score / 35) * 100
        
        # Save assessment
        new_assessment = Assessment(
            user_id=current_user.id,
            score=normalized_score
        )
        new_assessment.set_answers(answers)
        
        db.session.add(new_assessment)
        db.session.commit()
        
        flash('Assessment completed successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('assessment.html')

@app.route('/chat')
@login_required
def chat():
    # Get chat history
    messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at).all()
    return render_template('chat.html', messages=messages)

@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Detect emotion
    emotion = detect_emotion(user_message)
    
    # Check for crisis
    crisis_detected, crisis_level = detect_crisis(user_message)
    
    # Save user message
    user_chat = ChatMessage(
        user_id=current_user.id,
        content=user_message,
        is_user=True,
        emotion=emotion
    )
    db.session.add(user_chat)
    db.session.commit()
    
    # Record emotion
    emotion_record = EmotionRecord(
        user_id=current_user.id,
        emotion=emotion,
        intensity=0.8  # Default intensity, could be adjusted based on analysis
    )
    db.session.add(emotion_record)
    
    # Get relevant therapy resources
    relevant_resources = get_therapy_resources(user_message, emotion)
    
    # Get AI response
    ai_response = get_ai_response(
        user_message, 
        emotion, 
        relevant_resources, 
        crisis_detected,
        crisis_level
    )
    
    # Check if the response indicates an API error
    api_error = False
    if "API usage limits" in ai_response or "temporarily unavailable" in ai_response:
        api_error = True
    
    # Save AI response
    ai_chat = ChatMessage(
        user_id=current_user.id,
        content=ai_response,
        is_user=False
    )
    db.session.add(ai_chat)
    db.session.commit()
    
    response_data = {
        'message': ai_response,
        'emotion': emotion,
        'crisis_detected': crisis_detected,
        'api_error': api_error,
        'user_message_id': user_chat.id,
        'ai_message_id': ai_chat.id
    }
    
    return jsonify(response_data)

@app.route('/api/feedback', methods=['POST'])
@login_required
def provide_feedback():
    data = request.json
    message_id = data.get('message_id')
    is_positive = data.get('is_positive')
    
    if not message_id or is_positive is None:
        return jsonify({'error': 'Invalid feedback data'}), 400
    
    message = ChatMessage.query.get(message_id)
    if not message or message.user_id != current_user.id or message.is_user:
        return jsonify({'error': 'Message not found or not eligible for feedback'}), 404
    
    message.feedback = is_positive
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/assessment_history')
@login_required
def assessment_history():
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).all()
    
    history = []
    for assessment in assessments:
        history.append({
            'id': assessment.id,
            'date': assessment.created_at.strftime('%Y-%m-%d'),
            'score': assessment.score,
            'answers': assessment.get_answers()
        })
    
    return jsonify(history)

@app.route('/mood-tracker')
@login_required
def mood_tracker():
    """Render the mood tracker page"""
    # Get the user's emotion records for the last 30 days
    emotion_records = EmotionRecord.query.filter_by(user_id=current_user.id).order_by(EmotionRecord.created_at.desc()).limit(30).all()
    
    # Group emotions by date for the chart
    emotion_data = {}
    for record in emotion_records:
        date = record.created_at.strftime('%Y-%m-%d')
        if date not in emotion_data:
            emotion_data[date] = {}
        
        if record.emotion not in emotion_data[date]:
            emotion_data[date][record.emotion] = 0
        
        emotion_data[date][record.emotion] += record.intensity
    
    return render_template(
        'mood_tracker.html',
        emotion_records=emotion_records,
        emotion_data=json.dumps(emotion_data)
    )

@app.route('/api/mood', methods=['POST'])
@login_required
def record_mood():
    """API endpoint to record the user's mood"""
    data = request.json
    emotion = data.get('emotion')
    intensity = data.get('intensity', 1.0)
    notes = data.get('notes', '')
    
    if not emotion:
        return jsonify({'error': 'Emotion is required'}), 400
    
    # Validate intensity is between 0 and 1
    try:
        intensity = float(intensity)
        if intensity < 0 or intensity > 1:
            return jsonify({'error': 'Intensity must be between 0 and 1'}), 400
    except ValueError:
        return jsonify({'error': 'Intensity must be a number'}), 400
    
    # Create a new emotion record
    emotion_record = EmotionRecord(
        user_id=current_user.id,
        emotion=emotion,
        intensity=intensity
    )
    
    db.session.add(emotion_record)
    db.session.commit()
    
    return jsonify({
        'id': emotion_record.id,
        'emotion': emotion_record.emotion,
        'intensity': emotion_record.intensity,
        'created_at': emotion_record.created_at.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/mood-history')
@login_required
def mood_history():
    """API endpoint to get the user's mood history"""
    # Get query parameters
    days = request.args.get('days', 30, type=int)
    
    # Get the user's emotion records
    emotion_records = EmotionRecord.query.filter_by(user_id=current_user.id).order_by(EmotionRecord.created_at.desc()).limit(days).all()
    
    # Format the records for the response
    history = []
    for record in emotion_records:
        history.append({
            'id': record.id,
            'emotion': record.emotion,
            'intensity': record.intensity,
            'date': record.created_at.strftime('%Y-%m-%d'),
            'time': record.created_at.strftime('%H:%M:%S')
        })
    
    return jsonify(history)
