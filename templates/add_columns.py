import sqlite3

conn = sqlite3.connect('library.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)''')
try:
    cursor.execute('ALTER TABLE books ADD COLUMN subject_id INTEGER')
    print("subject_id column added")
except: 
    print("subject_id already exists")

try:
    cursor.execute('ALTER TABLE books ADD COLUMN total_copies INTEGER DEFAULT 5')
    print("total_copies column added")
except:
    print("total_copies already exists")

try:
    cursor.execute('ALTER TABLE books ADD COLUMN issued_copies INTEGER DEFAULT 0')
    print("issued_copies column added")
except:
    print("issued_copies already exists")

subjects = [('Computer',), ('Mechanical',), ('Electrical',), ('Other',)]
cursor.executemany('INSERT OR IGNORE INTO subjects (name) VALUES (?)', subjects)

conn.commit()
conn.close()
print("\nSAFE UPDATE DONE! Tuza juna data safe ahe ✅")
print("Aata Step 2 la jau.")

import sqlite3

conn = sqlite3.connect('library.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    book_id INTEGER,
    status TEXT
)''')

try:
    cursor.execute("ALTER TABLE books ADD COLUMN available INTEGER DEFAULT 5")
except:
    pass

conn.commit()
conn.close()
print("Done")