
from flask import Flask, render_template, request, redirect, session, jsonify
import os
import openai
import json

app = Flask(__name__)
app.secret_key = 'hican_secret_key'
openai.api_key = os.getenv('OPENAI_API_KEY')

with open('daily_plan.json', 'r') as f:
    daily_plan = json.load(f)

@app.route('/')
def home():
    if 'profile' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', profile=session.get('profile'), daily_plan=daily_plan)

@app.route('/check-in', methods=['POST'])
def check_in():
    day = request.form.get('day')
    answer = request.form.get('answer')
    
    # AI Grade
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Grade this answer on a scale of 0-100 based on the reading."},
                  {"role": "user", "content": f"Reading pages: {daily_plan[day]['pages']}. Question: {daily_plan[day]['question']}. Answer: {answer}"}]
    )
    score = int(response.choices[0].message.content.split()[0])
    return jsonify({'score': score})

if __name__ == '__main__':
    app.run(debug=False, port=5000)
