from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from . import db
from flask_login import UserMixin

# User model with auto-incrementing integer ID
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    first_name = db.Column(db.String(150))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing integer ID
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Store hashed passwords

    # Relationships
    bots = db.relationship('Bot', backref='owner', lazy=True)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"

# Bot model (adjusted for integer-based User ID)
class Bot(db.Model):
    __tablename__ = 'bots'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # bot_id
    name = db.Column(db.String(100), nullable=False)  # Bot's display name
    url = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key now references Integer ID


    # Relationships
    sessions = db.relationship('Session', backref='bot', lazy=True)

    def __repr__(self):
        return f"<Bot(name={self.name}, user_id={self.user_id})>"

# Session model
class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # session_id
    bot_id = db.Column(db.Integer, db.ForeignKey('bots.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (Optional: you can store conversation logs here as well)
    messages = db.relationship('Message', backref='session', lazy=True)

    def __repr__(self):
        return f"<Session(id={self.id}, bot_id={self.bot_id})>"

# Message model (Optional: For storing user-bot interaction logs)
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # "user" or "bot"
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message(session_id={self.session_id}, sender={self.sender})>"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database and tables created")
