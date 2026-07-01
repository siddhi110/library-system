import sqlite3

conn = sqlite3.connect('library.db')
cursor = conn.cursor()

cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'siddhi1234'")

conn.commit()
print("DONE! Rows changed:", cursor.rowcount)

conn.close()