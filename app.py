import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_123'

def get_db():
    db = sqlite3.connect('library.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE NOT NULL, 
                  password TEXT NOT NULL, 
                  role TEXT DEFAULT 'student')''')
    c.execute('''CREATE TABLE IF NOT EXISTS subjects 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT UNIQUE NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS books 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT NOT NULL, 
                  author TEXT NOT NULL, 
                  subject_id INTEGER, 
                  total_copies INTEGER DEFAULT 1, 
                  issued_copies INTEGER DEFAULT 0,
                  FOREIGN KEY (subject_id) REFERENCES subjects (id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS issued_books 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER, 
                  book_id INTEGER, 
                  issue_date TEXT, 
                  return_date TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id),
                  FOREIGN KEY (book_id) REFERENCES books (id))''')

# Students Table
    c.execute('''CREATE TABLE IF NOT EXISTS students
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              student_id TEXT UNIQUE,
              name TEXT,
              department TEXT,
              year TEXT,
              mobile TEXT,
              email TEXT)''')

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('books'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                         (username, hashed_password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!', 'error')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user['role']
            session['user_id'] = user['id']
            return redirect(url_for('books'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/books')
@login_required
def books():
    conn = get_db()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    #if session.get('role') != 'admin':
    #  flash('Only admin can add books', 'error')
    #  return redirect(url_for('books'))


    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        total_copies = int(request.form.get('total_copies', 1))

        conn = get_db()
        conn.execute('INSERT INTO books (title, author, total_copies) VALUES (?, ?, ?)',
                     (title, author, total_copies))
        conn.commit()
        conn.close()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))

    return render_template('add_book.html')

@app.route('/delete_book/<int:id>')
@login_required
def delete_book(id):
    if session.get('role') != 'admin':
        flash('Only admin can delete books', 'error')
        return redirect(url_for('books'))
        
    conn = get_db()
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books'))

@app.route('/issue_book/<int:id>')
@login_required
def issue_book(id):
    if session.get('role') != 'admin':
        flash('Only admin can issue books', 'error')
        return redirect(url_for('books'))
        
    conn = get_db()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    
    if book['issued_copies'] < book['total_copies']:
        conn.execute('UPDATE books SET issued_copies = issued_copies + 1 WHERE id = ?', (id,))
        conn.commit()
        flash('Book issued successfully!', 'success')
    else:
        flash('No copies available to issue', 'error')
    
    conn.close()
    return redirect(url_for('books'))

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    if session.get('role') != 'admin':
        flash('Only admin can edit books', 'error')
        return redirect(url_for('books'))
    
    conn = get_db()
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        total_copies = request.form['total_copies']
        
        conn.execute('UPDATE books SET title = ?, author = ?, total_copies = ? WHERE id = ?', 
                     (title, author, total_copies, id))
        conn.commit()
        conn.close()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books'))
    
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_book.html', book=book)

@app.route('/request_book/<int:book_id>')
def request_book(book_id):
    if 'username' not in session:  # he 1 line add kar
        flash("Please Login to request a book.", 'danger')
        return redirect('/login')
    
    user = session['username']
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO requests(username, book_id, status) VALUES(?, ?, 'Pending')", (user, book_id))
    cursor.execute("UPDATE books SET available = available - 1 WHERE id = ? AND available > 0", (book_id,))
    
    conn.commit()
    conn.close()
    
    flash("Book Request Sent!", 'success')
    return redirect('/books')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/issued')
def issued():
    return render_template('issued.html')

@app.route('/students')
def students():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    data = c.fetchall()
    conn.close()
    return render_template('students.html', students=data)

@app.route('/issue', methods=['GET', 'POST'])
def issue():
    db = get_db()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        book_id = request.form['book_id']
        issue_date = datetime.now().strftime('%Y-%m-%d')
        return_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d') # 14 divsanchi mudat
        
        db.execute("INSERT INTO issued_books (student_id, book_id, issue_date, return_date) VALUES (?,?,?,?)",
                   (student_id, book_id, issue_date, return_date))
        
        db.execute("UPDATE books SET available = available - 1 WHERE id = ?", (book_id,))
        
        db.commit()
        return redirect('/issued')
    
    students = db.execute('SELECT * FROM students').fetchall()
    books = db.execute('SELECT * FROM books WHERE available > 0').fetchall()
    db.close()
    return render_template('issue.html', students=students, books=books)

@app.route('/reports')
def reports():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM issued_books")
    issued_books = c.fetchone()[0]
    conn.close()
    return render_template('reports.html', total=total_books, issued=issued_books)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)