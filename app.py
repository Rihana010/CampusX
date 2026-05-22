from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'campusx_secret_123'
app.config['SESSION_TYPE'] = 'filesystem'

def get_db():
    conn = sqlite3.connect('campusx.db')
    conn.row_factory = sqlite3.Row
    return conn

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
    
    db = get_db()
    try:
        db.execute('INSERT INTO users (name, email, department, password) VALUES (?, ?, ?, ?)',
                   (name, email, department, password))
        db.commit()
        return redirect('/dashboard')
    except:
        return redirect('/auth?error=Email already exists')
    finally:
        db.close()

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = hashlib.sha256(request.form['password'].encode()).hexdigest()
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email=? AND password=?', 
                      (email, password)).fetchone()
    db.close()
    
    if user:
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
    db = get_db()
    skills = db.execute('''
        SELECT skills.*, users.name, users.department, users.email 
        FROM skills JOIN users ON skills.user_id = users.id
        ORDER BY skills.id DESC
    ''').fetchall()
    db.close()
    return render_template('skills.html', skills=skills)

@app.route('/skills/post', methods=['POST'])
def post_skill():
    if 'user_id' not in session:
        return redirect('/auth')
    offer = request.form['offer']
    want = request.form['want']
    description = request.form['description']
    db = get_db()
    db.execute('INSERT INTO skills (user_id, offer, want, description) VALUES (?, ?, ?, ?)',
               (session['user_id'], offer, want, description))
    db.commit()
    db.close()
    return redirect('/skills')
@app.route('/marketplace')
def marketplace():
    if 'user_id' not in session:
        return redirect('/auth')
    db = get_db()
    items = db.execute('''
        SELECT items.*, users.name, users.department, users.email 
        FROM items JOIN users ON items.user_id = users.id
        ORDER BY items.id DESC
    ''').fetchall()
    db.close()
    return render_template('marketplace.html', items=items)

@app.route('/marketplace/post', methods=['POST'])
def post_item():
    if 'user_id' not in session:
        return redirect('/auth')
    title = request.form['title']
    price = request.form['price']
    category = request.form['category']
    description = request.form['description']
    db = get_db()
    db.execute('INSERT INTO items (user_id, title, price, category, description) VALUES (?, ?, ?, ?, ?)',
               (session['user_id'], title, price, category, description))
    db.commit()
    db.close()
    return redirect('/marketplace')

if __name__ == '__main__':
    app.run(debug=True)