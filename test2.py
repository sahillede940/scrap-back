# list all tables in the database

import sqlite3
import os

# Create a connection to the SQLite database

sqlite_db = "./my_database2.db"
conn = sqlite3.connect(sqlite_db)

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Get a list of all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Fetch all the rows from the cursor object
tables = cursor.fetchall()

# Print the list of tables
print("Tables in the database:")
for table in tables:
    print(table[0])

# Close the connection
conn.close()

