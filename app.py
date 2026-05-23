from flask import Flask, render_template, request, redirect, session
import hashlib
import requests as req

app = Flask(__name__)
app.secret_key = 'campusx_secret_123'

SUPABASE_URL = 'https://xbgutfybiepojuqrtsfk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhiZ3V0ZnliaWVwb2p1cXJ0c2ZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk1NTA1NDcsImV4cCI6MjA5NTEyNjU0N30.ag6OtUlCPG5ssXjJFscqHYbPme23vqCnwyPdTaoqVL8'

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def db_get(table, params=None):
    r = req.get(f'{SUPABASE_URL}/rest/v1/{table}', headers=HEADERS, params=params)
    return r.json()

def db_post(table, data):
    r = req.post(f'{SUPABASE_URL}/rest/v1/{table}', headers=HEADERS, json=data)
    return r.json()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    department = request.form['department']
    password = hashlib.sha256(request.form['password'].encode()).hexdigest()
    
    result = db_post('users', {
        'name': name,
        'email': email,
        'department': department,
        'password': password
    })
    
    if isinstance(result, list) and result:
        user = result[0]
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return redirect('/dashboard')
    else:
        return redirect('/auth?error=Email already exists')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = hashlib.sha256(request.form['password'].encode()).hexdigest()
    
    result = db_get('users', {'email': f'eq.{email}'})
    
    if isinstance(result, list) and result and result[0]['password'] == password:
        user = result[0]
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return redirect('/dashboard')
    else:
        return redirect('/auth?error=Invalid credentials')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/auth')
    return render_template('dashboard.html', name=session['user_name'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/skills')
def skills():
    if 'user_id' not in session:
        return redirect('/auth')
    result = db_get('skills', {'select': '*,users(name,department,email)', 'order': 'id.desc'})
    if not isinstance(result, list):
        result = []
    return render_template('skills.html', skills=result)

@app.route('/skills/post', methods=['POST'])
def post_skill():
    if 'user_id' not in session:
        return redirect('/auth')
    db_post('skills', {
        'user_id': session['user_id'],
        'offer': request.form['offer'],
        'want': request.form['want'],
        'description': request.form['description']
    })
    return redirect('/skills')

@app.route('/marketplace')
def marketplace():
    if 'user_id' not in session:
        return redirect('/auth')
    result = db_get('items', {'select': '*,users(name,department,email)', 'order': 'id.desc'})
    if not isinstance(result, list):
        result = []
    return render_template('marketplace.html', items=result)

@app.route('/marketplace/post', methods=['POST'])
def post_item():
    if 'user_id' not in session:
        return redirect('/auth')
    db_post('items', {
        'user_id': session['user_id'],
        'title': request.form['title'],
        'price': request.form['price'],
        'category': request.form['category'],
        'description': request.form['description']
    })
    return redirect('/marketplace')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)