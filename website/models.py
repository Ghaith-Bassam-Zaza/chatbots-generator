from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

class Chatbot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    script = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref=db.backref('chatbots', lazy=True))

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    bot_id = db.Column(db.String(36), db.ForeignKey('chat_bot.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)