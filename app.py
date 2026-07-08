from flask import Flask, render_template, request, redirect, session
import os
import openai

app = Flask(__name__)
app.secret_key = 'hican_secret_key' # In production use a real secret key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Mock data
students = {} # Dict by student_id or simple global for now
reports = []
diaries = []

@app.route('/')
def home():
    if 'profile' in session:
        return render_template('dashboard.html', profile=session['profile'])
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'profile' in session:
        return render_template('dashboard.html', profile=session['profile'])
    return redirect('/')

@app.route('/profile', methods=['POST'])
def profile():
    session['profile'] = {
        'name': request.form.get('name'),
        'about': request.form.get('about'),
        'photo': 'default.jpg' # Logic for file upload needed
    }
    return redirect('/')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('message')
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are Hican Bridge AI assistant for high school graduates."},
                  {"role": "user", "content": user_message}]
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=False, port=5000)
