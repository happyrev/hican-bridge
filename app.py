import os
import json
import random
import datetime

# --- IMPORTANT: No Eventlet monkey_patch here to fix RLock issues ---
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from openai import OpenAI

app = Flask(__name__)
app.secret_key = 'hican_secret_key'

# --- API and DB ---
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key) if api_key else None
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hican.db'
db = SQLAlchemy(app)

# Use standard thread-based mode for SocketIO
socketio = SocketIO(app, cors_allowed_origins="*") 
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'daily_plan.json'), 'r') as f:
    daily_plan = json.load(f)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            new_user = User(
                username=request.form['username'],
                name=request.form['name'],
                age=int(request.form.get('age', 0)),
                bio=request.form.get('bio', '')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
        except Exception as e:
            return f"Registration failed: {str(e)}", 500
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    quote = ["Believe you can.", "Your potential is endless.", "Embrace vulnerability."][datetime.datetime.now().timetuple().tm_yday % 3]
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date.desc()).all()
    return render_template('dashboard.html', user=current_user, daily_plan=daily_plan, quote=quote, entries=entries, badges=current_user.check_badges())

@app.route('/upload-audio', methods=['POST'])
@login_required
def upload_audio():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or 'audio' not in request.files:
        return jsonify({'error': 'Missing API key or audio'}), 400
    
    file = request.files['audio']
    temp_path = os.path.join('/tmp', f'audio_{current_user.id}.webm')
    file.save(temp_path)
    
    try:
        temp_client = OpenAI(api_key=api_key)
        with open(temp_path, "rb") as f:
            transcript = temp_client.audio.transcriptions.create(model="whisper-1", file=f).text
        response = temp_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a supportive mentor."}, {"role": "user", "content": transcript}]
        )
        return jsonify({'message': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

if __name__ == '__main__':
    socketio.run(app, debug=False, port=5000)
