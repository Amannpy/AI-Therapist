from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assessments = db.relationship('Assessment', backref='user', lazy='dynamic')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy='dynamic')
    emotion_records = db.relationship('EmotionRecord', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON string of answers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_answers(self, answers_dict):
        self.answers = json.dumps(answers_dict)

    def get_answers(self):
        return json.loads(self.answers)

    def __repr__(self):
        return f'<Assessment {self.id} by User {self.user_id}>'

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_user = db.Column(db.Boolean, default=True)  # True if from user, False if from AI
    emotion = db.Column(db.String(50), nullable=True)  # Detected emotion if from user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Boolean, nullable=True)  # True for 👍, False for 👎, None for no feedback

    def __repr__(self):
        return f'<ChatMessage {self.id} by User {self.user_id}>'

class EmotionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    emotion = db.Column(db.String(50), nullable=False)
    intensity = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EmotionRecord {self.id} by User {self.user_id}>'
