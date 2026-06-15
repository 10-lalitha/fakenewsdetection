import os
import sqlite3
import pickle
from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =========================
# FLASK APP CONFIGURATION
# =========================

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')

# Production settings
app.config['ENV'] = os.getenv('FLASK_ENV', 'development')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# =========================
# DATABASE CONFIGURATION
# =========================

# Use persistent storage for Render
if os.getenv('FLASK_ENV') == 'production':
    DATABASE_PATH = '/var/data/database.db'
else:
    DATABASE_PATH = 'database.db'

# Create /var/data directory if it doesn't exist (for Render)
if os.getenv('FLASK_ENV') == 'production':
    os.makedirs('/var/data', exist_ok=True)

conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
cursor = conn.cursor()

# =========================
# CREATE TABLES
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    news TEXT,
    result TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(username) REFERENCES users(username)
)
""")

conn.commit()

# =========================
# CREATE INDEXES FOR PERFORMANCE
# =========================

try:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_user ON history(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_result ON history(result)")
    conn.commit()
except sqlite3.OperationalError:
    pass

# =========================
# LOAD MACHINE LEARNING MODEL
# =========================

try:
    # Try to load from root directory (for Render)
    if os.path.exists('model.pkl') and os.path.exists('vectorizer.pkl'):
        model = pickle.load(open('model.pkl', 'rb'))
        vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
    # Try to load from model directory (for local development)
    elif os.path.exists('model/model.pkl') and os.path.exists('model/vectorizer.pkl'):
        model = pickle.load(open('model/model.pkl', 'rb'))
        vectorizer = pickle.load(open('model/vectorizer.pkl', 'rb'))
    else:
        raise FileNotFoundError("Model files not found. Please ensure model.pkl and vectorizer.pkl exist.")
except Exception as e:
    print(f"Error loading model: {e}")
    raise

# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template('index.html')

# =========================
# REGISTER PAGE
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return "Username and password required", 400
        
        if len(username) < 3 or len(password) < 3:
            return "Username and password must be at least 3 characters", 400
        
        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )
            conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Username already exists", 400
    
    return render_template('register.html')

# =========================
# LOGIN PAGE
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        
        user = cursor.fetchone()
        
        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "Invalid Credentials", 401
    
    return render_template('login.html')

# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    cursor.execute(
        "SELECT news,result FROM history WHERE username=? ORDER BY timestamp DESC",
        (session['user'],)
    )
    
    history = cursor.fetchall()
    total = len(history)
    real = sum(1 for h in history if h[1] == "REAL")
    fake = sum(1 for h in history if h[1] == "FAKE")
    
    return render_template(
        'dashboard.html',
        history=history,
        total=total,
        real=real,
        fake=fake
    )

# =========================
# PREDICT NEWS
# =========================

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect('/login')
    
    news = request.form.get('news', '').strip()
    
    if not news:
        return "Please enter news text", 400
    
    try:
        vector = vectorizer.transform([news])
        prediction = model.predict(vector)[0]
        result = "REAL" if prediction == 1 else "FAKE"
        
        # Save to history
        cursor.execute(
            "INSERT INTO history(username,news,result) VALUES(?,?,?)",
            (session['user'], news, result)
        )
        conn.commit()
        
        # Fetch updated history
        cursor.execute(
            "SELECT news,result FROM history WHERE username=? ORDER BY timestamp DESC",
            (session['user'],)
        )
        history = cursor.fetchall()
        total = len(history)
        real = sum(1 for h in history if h[1] == "REAL")
        fake = sum(1 for h in history if h[1] == "FAKE")
        
        return render_template(
            'dashboard.html',
            prediction=result,
            history=history,
            total=total,
            real=real,
            fake=fake
        )
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Error making prediction", 500

# =========================
# ADMIN PANEL
# =========================

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')
    
    if session['user'] != 'admin':
        return "Access Denied", 403
    
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    cursor.execute("SELECT result FROM history")
    data = cursor.fetchall()
    
    real = sum(1 for d in data if d[0] == "REAL")
    fake = sum(1 for d in data if d[0] == "FAKE")
    
    return render_template(
        'admin.html',
        users=users,
        real=real,
        fake=fake
    )

# =========================
# ADD USER (ADMIN ONLY)
# =========================

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user' not in session:
        return redirect('/login')
    
    if session['user'] != 'admin':
        return "Access Denied", 403
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if not username or not password:
        return "Username and password required", 400
    
    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )
        conn.commit()
        return redirect('/admin')
    except sqlite3.IntegrityError:
        return "Username already exists", 400

# =========================
# DELETE USER (ADMIN ONLY)
# =========================

@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    if 'user' not in session:
        return redirect('/login')
    
    if session['user'] != 'admin':
        return "Access Denied", 403
    
    try:
        cursor.execute("DELETE FROM users WHERE id=?", (id,))
        conn.commit()
        return redirect('/admin')
    except Exception as e:
        print(f"Error deleting user: {e}")
        return "Error deleting user", 500

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# =========================
# ERROR HANDLERS
# =========================

@app.errorhandler(404)
def not_found(e):
    return "Page not found", 404

@app.errorhandler(500)
def server_error(e):
    return "Internal server error", 500

# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])