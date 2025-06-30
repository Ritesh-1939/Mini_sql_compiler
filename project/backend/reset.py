import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Clear all records from the students table
cursor.execute('DELETE FROM students')
conn.commit()
conn.close()

print('Database cleared successfully!')
