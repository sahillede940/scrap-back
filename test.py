from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine, MetaData, Table, select, insert, inspect, Column, Integer, String
from sqlalchemy.orm import sessionmaker
import os

SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PORT = os.getenv("SUPABASE_PORT")
SUPABASE_DBNAME = os.getenv("SUPABASE_DBNAME")
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PASS = os.getenv("SUPABASE_PASS")

DB_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASS}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DBNAME}"

sqlite_db = "sqlite:///./my_database2.db"
sqlite_engine = create_engine(sqlite_db)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)
metadata = MetaData()

# PostgreSQL (Supabase) connection string
supabase_engine = create_engine(DB_URL)

sqlite_table_name = "my_table"  # Replace with your SQLite table name
supabase_table_name = "posts_new"  # Replace with your Supabase table name

# Function to read data from SQLite
def read_from_sqlite():
    with sqlite_engine.connect() as conn:
        table = Table(sqlite_table_name, metadata, autoload_with=sqlite_engine)
        query = select(table)
        result = conn.execute(query)
        return result.mappings().all()

# Function to check and create table in Supabase (PostgreSQL)
def check_and_create_supabase_table():
    inspector = inspect(supabase_engine)
    if not inspector.has_table(supabase_table_name):
        metadata = MetaData()
        posts_table = Table(
            supabase_table_name, metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('title', String),
            Column('description', String),
        )
        metadata.create_all(supabase_engine)
    else:
        metadata = MetaData()
        posts_table = Table(supabase_table_name, metadata, autoload_with=supabase_engine)
    return posts_table

# Function to write data to Supabase (PostgreSQL)
def write_to_supabase(data, posts_table):
    i = 0
    with supabase_engine.connect() as conn:
        for row in data:
            stmt = insert(posts_table).values({"title": row["title"], "description": row["description"]})
            conn.execute(stmt)
            if i % 100 == 0:
                print(f"Inserted {i} records")

# Main function
def main():
    # Read data from SQLite
    data = read_from_sqlite()
    
    # Check and create table in Supabase
    posts_table = check_and_create_supabase_table()
    
    # Write data to Supabase (PostgreSQL)
    write_to_supabase(data, posts_table)

if __name__ == "__main__":
    main()
