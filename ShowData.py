import sqlite3

# Connect to your SQLite DB
conn = sqlite3.connect("financial_data.db")
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# See the first 5 rows from 'companies' table (or your actual table name)
cursor.execute("SELECT * FROM companies LIMIT 5;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()