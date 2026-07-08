from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return 'No audio file', 400
    audio_file = request.files['audio']
    audio_file.save('temp_report.wav')
    # Here you would typically add: 
    # transcription = openai.Audio.transcribe("whisper-1", open('temp_report.wav', 'rb'))
    # reports.append({'summary': transcription['text']})
    print("Audio received and saved.")
    return 'Success', 200

# Temporary storage for demo
students = []
reports = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile', methods=['POST'])
def profile():
    student_data = {
        'name': request.form.get('name'),
        'age': request.form.get('age'),
        'sex': request.form.get('sex'),
        'about': request.form.get('about')
    }
    students.append(student_data)
    print(f"New student added: {student_data}")
    return redirect('/')

@app.route('/report', methods=['POST'])
def report():
    report_data = {
        'hours': request.form.get('reading_hours'),
        'confidence': request.form.get('confidence'),
        'summary': request.form.get('summary')
    }
    reports.append(report_data)
    print(f"New report added: {report_data}")
    return redirect('/')

@app.route('/diary', methods=['POST'])
def diary():
    diary_entry = {
        'entry': request.form.get('entry')
    }
    # For now, we'll just print it, but we could add a list to store these
    print(f"New diary entry: {diary_entry}")
    return redirect('/')

@app.route('/admin')
def admin():
    # In a real app, you would add password protection here
    auth = request.args.get('pass')
    if auth != 'admin123':
        return "Unauthorized", 401
    return render_template('admin.html', students=students, reports=reports)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
