import eventlet
eventlet.monkey_patch()

import os
import json
import random
import datetime

# --- IMPORTANT: Everything imported below must be imported AFTER monkey_patch() ---
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from openai import OpenAI
app = Flask(__name__)
app.secret_key = 'hican_secret_key'

# --- Restore API client and DB config ---
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key) if api_key else None

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hican.db'
db = SQLAlchemy(app)
# -----------------------------------------------------

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*") 
# ---------------------------------------------------------------------------------
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
plan_path = os.path.join(BASE_DIR, 'daily_plan.json')
with open(plan_path, 'r') as f:
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
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
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
            app.logger.error(f"Registration Error: {str(e)}")
            return "Registration failed. Please check your inputs.", 500
    return render_template('register.html')

def get_daily_quote():
    quotes = [
        "Believe you can and you're halfway there.",
        "The only way to do great work is to love what you do.",
        "Your potential is endless.",
        "Embrace vulnerability as your greatest strength.",
        "Leadership is about service to others."
    ]
    return quotes[datetime.datetime.now().timetuple().tm_yday % len(quotes)]

@app.route('/dashboard')
@login_required
def dashboard():
    quote = get_daily_quote()
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date.desc()).all()
    badges = current_user.check_badges()
    return render_template('dashboard.html', user=current_user, daily_plan=daily_plan, quote=quote, entries=entries, badges=badges)

@app.route('/check-in', methods=['POST'])
@login_required
def check_in():
    if not client: return jsonify({'score': 0}), 500
    day = request.form.get('day')
    answer = request.form.get('answer')
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Grade this answer on a scale of 0-100 based on the reading."},
                  {"role": "user", "content": f"Reading pages: {daily_plan[day]['pages']}. Question: {daily_plan[day]['question']}. Answer: {answer}"}]
    )
    score = int(response.choices[0].message.content.split()[0])
    return jsonify({'score': score})

@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    if request.method == 'POST':
        entry = JournalEntry(content=request.form.get('content'), user_id=current_user.id)
        db.session.add(entry)
        db.session.commit()
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date.desc()).all()
    return render_template('dashboard.html', user=current_user, entries=entries)

@app.route('/submit-report', methods=['POST'])
@login_required
def submit_report():
    report = request.form.get('report')
    # Track as an activity to earn badges
    # (Implementation of badge logic)
    with open(os.path.join(BASE_DIR, 'weekly_reports.txt'), 'a') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d')} | {current_user.name} | {report}\n")
    return redirect(url_for('dashboard'))

@app.route('/upload-audio', methods=['POST'])
@login_required
def upload_audio():
    # Hardcoded check to verify API key existence immediately
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return jsonify({'error': 'Backend missing API Key'}), 500

    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['audio']
    temp_path = os.path.join('/tmp', f'temp_{current_user.id}.webm')
    file.save(temp_path)
    
    try:
        # Use a new client instance per request for stability
        temp_client = OpenAI(api_key=api_key)
        
        with open(temp_path, "rb") as audio_file:
            transcription = temp_client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        response = temp_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a supportive Hican Bridge mentor."},
                {"role": "user", "content": transcription.text}
            ]
        )
        return jsonify({'message': response.choices[0].message.content})
    except Exception as e:
        # Log precisely what happened for debugging
        app.logger.error(f"DEBUG_ERROR: {str(e)}")
        return jsonify({'error': f'Processing Error: {str(e)}'}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@socketio.on('audio_stream')
def handle_audio_stream(data):
    # This is a basic implementation of a real-time stream handler
    # We buffer incoming audio chunks and process them when a natural pause occurs
    # or a threshold is reached.
    app.logger.info(f"Received audio chunk of size: {len(data)}")
    # In a real app, you would use an ASR stream (like OpenAI real-time)
    # For now, acknowledge the data
    emit('mentor_response', {'text': 'I am listening...'})

if __name__ == '__main__':
    socketio.run(app, debug=False, port=5000)
