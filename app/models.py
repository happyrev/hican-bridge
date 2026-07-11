from app import db
from flask_login import UserMixin
import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    bio = db.Column(db.Text)
    journal_entries = db.relationship('JournalEntry', backref='student', lazy=True)

    def check_badges(self):
        badges = []
        if len(self.journal_entries) >= 3:
            badges.append({"name": "Journalist", "icon": "✍️"})
        if len(self.journal_entries) >= 7:
            badges.append({"name": "Master Writer", "icon": "📖"})
        return badges

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
