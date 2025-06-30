import sqlite3

# Connect to a new database file (this will create database.db)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create a table named 'students'
cursor.execute('CREATE TABLE IF NOT EXISTS students (name TEXT, age INTEGER)')

# Insert some sample data
cursor.execute('INSERT INTO students (name, age) VALUES ("John", 20)')
cursor.execute('INSERT INTO students (name, age) VALUES ("Alice", 22)')
cursor.execute('INSERT INTO students (name, age) VALUES ("Bob", 19)')

# Save changes and close the connection
conn.commit()
conn.close()

print("Database created successfully.")
