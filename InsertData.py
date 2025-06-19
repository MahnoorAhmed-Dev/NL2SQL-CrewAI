import sqlite3
import pandas as pd

# Step 1: Load the CSV
csv_file = "Annual_P_L_1_final.csv"
df = pd.read_csv(csv_file)

# Optional: Clean column names
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Step 2: Connect to SQLite and insert data
conn = sqlite3.connect("financial_data.db")
df.to_sql("companies", conn, if_exists="replace", index=False)  # creates or replaces table
conn.commit()
conn.close()
