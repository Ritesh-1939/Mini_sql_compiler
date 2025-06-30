import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Insert sample records
cursor.execute("INSERT INTO students (name, age) VALUES ('John', 22)")
cursor.execute("INSERT INTO students (name, age) VALUES ('Alice', 20)")
cursor.execute("INSERT INTO students (name, age) VALUES ('Bob', 21)")

conn.commit()
conn.close()

print('Sample data inserted successfully!')
