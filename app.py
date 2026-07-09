from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import os
import openai
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random
import datetime
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'hican_secret_key'
openai.api_key = os.getenv('OPENAI_API_KEY')
socketio = SocketIO(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hican.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    bio = db.Column(db.Text)
    photo = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

with open('daily_plan.json', 'r') as f:
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
        new_user = User(
            username=request.form['username'],
            name=request.form['name'],
            age=request.form.get('age', 0),
            bio=request.form.get('bio', '')
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
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
    return render_template('dashboard.html', user=current_user, daily_plan=daily_plan, quote=quote)

@app.route('/check-in', methods=['POST'])
@login_required
def check_in():
    day = request.form.get('day')
    answer = request.form.get('answer')
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Grade this answer on a scale of 0-100 based on the reading."},
                  {"role": "user", "content": f"Reading pages: {daily_plan[day]['pages']}. Question: {daily_plan[day]['question']}. Answer: {answer}"}]
    )
    score = int(response.choices[0].message.content.split()[0])
    return jsonify({'score': score})

@app.route('/submit-report', methods=['POST'])
@login_required
def submit_report():
    report = request.form.get('report')
    with open('weekly_reports.txt', 'a') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d')} | {current_user.name} | {report}\n")
    return redirect(url_for('dashboard'))

@app.route('/admin-reports')
@login_required
def admin_reports():
    if current_user.username != 'admin':
        return "Unauthorized", 401
    reports = []
    if os.path.exists('weekly_reports.txt'):
        with open('weekly_reports.txt', 'r') as f:
            reports = f.readlines()
    return render_template('admin.html', reports=reports)

@socketio.on('audio_data')
def handle_audio(data):
    print("Received audio data chunk")
    # For MVP, simulate a response while you finalize the Whisper/TTS setup
    # In production, you would save 'data' to a temp file and send to Whisper
    # Here is the logic placeholder for the LLM response:
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a supportive Hican Bridge mentor. Keep responses short and spoken-style."},
                  {"role": "user", "content": "The student is checking in."}]
    )
    mentor_response = response.choices[0].message.content
    emit('audio_response', {'message': mentor_response})

if __name__ == '__main__':
    socketio.run(app, debug=False, port=5000)
