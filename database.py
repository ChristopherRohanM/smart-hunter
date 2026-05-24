import sqlite3

connection = sqlite3.connect("jobs.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    location TEXT,
    url TEXT,
    status TEXT,
    notes TEXT
)
""")

connection.commit()

connection.close()

print("Database created successfully 😄")

connection = sqlite3.connect("jobs.db")

cursor = connection.cursor()

cursor.execute("SELECT * FROM jobs")

jobs = cursor.fetchall()

for job in jobs:
    print(job)

connection.close()
