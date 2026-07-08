
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

import random
import datetime

# Mock function for daily quote
def get_daily_quote():
    quotes = [
        "Believe you can and you're halfway there.",
        "The only way to do great work is to love what you do.",
        "Your potential is endless.",
        "Embrace vulnerability as your greatest strength.",
        "Leadership is about service to others."
    ]
    # Simple deterministic choice based on day of year
    return quotes[datetime.datetime.now().timetuple().tm_yday % len(quotes)]

@app.route('/dashboard')
def dashboard():
    quote = get_daily_quote()
    return render_template('dashboard.html', profile=session.get('profile'), daily_plan=daily_plan, quote=quote)

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

@app.route('/submit-report', methods=['POST'])
def submit_report():
    report = request.form.get('report')
    # Save to file or database
    with open('weekly_reports.txt', 'a') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d')} | {report}\n")
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=False, port=5000)
