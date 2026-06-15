from flask import Flask, render_template, request, redirect, session
import sqlite3
import pickle

# =========================
# FLASK APP
# =========================

app = Flask(__name__)
app.secret_key = "secret123"

# =========================
# DATABASE CONNECTION
# =========================

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# =========================
# CREATE USERS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# =========================
# CREATE HISTORY TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    news TEXT,
    result TEXT
)
""")

conn.commit()

# =========================
# LOAD MACHINE LEARNING MODEL
# =========================

model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

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

        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()

        return redirect('/login')

    return render_template('register.html')

# =========================
# LOGIN PAGE
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        if user:

            session['user'] = username

            return redirect('/dashboard')

        else:
            return "Invalid Credentials"

    return render_template('login.html')

# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    cursor.execute(
        "SELECT news,result FROM history WHERE username=?",
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

    news = request.form['news']

    vector = vectorizer.transform([news])

    prediction = model.predict(vector)[0]

    result = "REAL" if prediction == 1 else "FAKE"

    # SAVE HISTORY

    cursor.execute(
        "INSERT INTO history(username,news,result) VALUES(?,?,?)",
        (session['user'], news, result)
    )

    conn.commit()

    # FETCH HISTORY

    cursor.execute(
        "SELECT news,result FROM history WHERE username=?",
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

# =========================
# ADMIN PANEL
# =========================

@app.route('/admin')
def admin():

    if 'user' not in session:
        return redirect('/login')

    if session['user'] != 'admin':
        return "Access Denied"

    # FETCH USERS

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # FETCH PREDICTIONS

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
# ADD USER
# =========================

@app.route('/add_user', methods=['POST'])
def add_user():

    if 'user' not in session:
        return redirect('/login')

    if session['user'] != 'admin':
        return "Access Denied"

    username = request.form['username']
    password = request.form['password']

    cursor.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (username, password)
    )

    conn.commit()

    return redirect('/admin')

# =========================
# DELETE USER
# =========================

@app.route('/delete_user/<int:id>')
def delete_user(id):

    if 'user' not in session:
        return redirect('/login')

    if session['user'] != 'admin':
        return "Access Denied"

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (id,)
    )

    conn.commit()

    return redirect('/admin')

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')

# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)
