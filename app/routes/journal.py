from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db, openai_client
from app.models import JournalEntry
import datetime
import os
import json

journal = Blueprint('journal', __name__)

# Load daily_plan outside of a route to avoid repeated file reads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Adjust path to daily_plan.json relative to the project root, not blueprint file
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
DAILY_PLAN_PATH = os.path.join(PROJECT_ROOT, 'daily_plan.json')

with open(DAILY_PLAN_PATH, 'r') as f:
    daily_plan = json.load(f)

@journal.route('/')
@login_required
def home():
    return redirect(url_for('journal.dashboard'))

@journal.route('/dashboard')
@login_required
def dashboard():
    quote = ["Believe you can.", "Your potential is endless.", "Embrace vulnerability."][datetime.datetime.now().timetuple().tm_yday % 3]
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date.desc()).all()
    day_index = min(len(entries) + 1, 30) # Assume 30 days
    
    current_day_data = daily_plan.get(str(day_index), {"pages": "N/A", "question": "No task today."})
    
    return render_template('dashboard.html', 
                           user=current_user, 
                           day=day_index, 
                           info=current_day_data, 
                           quote=quote, 
                           entries=entries, 
                           badges=current_user.check_badges())

@journal.route('/upload-audio', methods=['POST'])
@login_required
def upload_audio():
    if not openai_client or 'audio' not in request.files:
        return jsonify({'error': 'Missing OpenAI client or audio'}), 400
    
    file = request.files['audio']
    # Use a secure temporary file creation or a designated upload folder
    temp_path = os.path.join(PROJECT_ROOT, 'temp_uploads', f'audio_{current_user.id}_{datetime.datetime.now().timestamp()}.webm')
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    file.save(temp_path)
    
    try:
        with open(temp_path, "rb") as f:
            transcript = openai_client.audio.transcriptions.create(model="whisper-1", file=f).text
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a supportive mentor."}, {"role": "user", "content": transcript}]
        )
        return jsonify({'message': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@journal.route('/journal', methods=['POST'])
@login_required
def create_journal_entry():
    content = request.form.get('content', '').strip()
    if content:
        db.session.add(JournalEntry(content=content, user_id=current_user.id))
        db.session.commit()
        flash('Journal entry saved.')
    else:
        flash('Please write something before saving.')
    return redirect(url_for('journal.dashboard'))

@journal.route('/check-in', methods=['POST'])
@login_required
def check_in():
    day = request.form.get('day', '').strip()
    answer = request.form.get('answer', '').strip()
    if not day or not answer:
        return jsonify({'ok': False, 'error': 'Missing day or answer'}), 400

    entry = JournalEntry(
        content=f"Day {day} reading check-in: {answer}",
        user_id=current_user.id,
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'ok': True, 'message': 'Check-in saved.'})

@journal.route('/submit-report', methods=['POST'])
@login_required
def submit_report():
    report = request.form.get('report', '').strip()
    if report:
        db.session.add(JournalEntry(content=f"Weekly report: {report}", user_id=current_user.id))
        db.session.commit()
        flash('Weekly report submitted.')
    else:
        flash('Please write your weekly report before submitting.')
    return redirect(url_for('journal.dashboard'))
