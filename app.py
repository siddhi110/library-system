import sqlite3
from flask import Flask, render_template, request, redirect, url_for,session

app = Flask(__name__)
app.secret_key="library123"
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  author TEXT NOT NULL,
                  status TEXT DEFAULT 'Available')''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password TEXT NOT NULL,
             role TEXT DEFAULT 'student')''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
@login_required
def home():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/add', methods=['POST'])
@login_required
def add_book():
    title = request.form['title']
    author = request.form['author']
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author) VALUES (?,?)", (title, author))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/delete/<int:id>')
@login_required
def delete_book(id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/issue/<int:id>')
@login_required
def issue_book(id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("UPDATE books SET status='Issued' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except:
            return "Username already ahe! Dusra try kara"
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['role'] = user[3] 
            return redirect(url_for('home'))
        else:
            return "Chukicha username/password!"
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

with app.app_context():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    # jar admin user ahe tar tyala admin banav
    c.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)