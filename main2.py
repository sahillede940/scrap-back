import subprocess
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PORT = os.getenv("SUPABASE_PORT", "5432")  # Default to port 5432 if not set
SUPABASE_DBNAME = os.getenv("SUPABASE_DBNAME")
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PASS = os.getenv("SUPABASE_PASS")

# Function to migrate data from SQLite to Supabase
def migrate_data():
    # Create a connection string for the SQLite database
    sqlite_db = "sqlite:///./my_database2.db"

    # Create a connection string for the Supabase database
    DB_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASS}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DBNAME}"

    # Use SQLAlchemy to connect to the SQLite database
    sqlite_engine = create_engine(sqlite_db)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

    # Use SQLAlchemy to connect to the Supabase database
    supabase_engine = create_engine(DB_URL)
    SupabaseSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=supabase_engine)

    # Create a base class for the models
    Base = declarative_base()

    # Define the model for the posts table
    class Post(Base):
        __tablename__ = "my_table"
        id = Column(Integer, primary_key=True, index=True)
        title = Column(String)
        description = Column(String)

    # Check if table exists in Supabase, if not create it
    inspector = inspect(supabase_engine)
    if not inspector.has_table("my_table"):
        Base.metadata.create_all(bind=supabase_engine)

    # Create sessions for SQLite and Supabase databases
    sqlite_session = SessionLocal()
    supabase_session = SupabaseSessionLocal()

    try:
        # Query the posts table in the SQLite database
        posts = sqlite_session.query(Post).all()

        # Insert the posts into the Supabase database
        i = 0
        for post in posts[10:]:
            i+=1
            new_post = Post(id=post.id, title=post.title, description=post.description)
            supabase_session.add(new_post)
            if i % 100 == 0:
                supabase_session.commit()
                print(f"Inserted {i} records.")

        # Commit the changes to Supabase
        supabase_session.commit()
        print("Data migration complete.")

    except Exception as e:
        print(f"Error occurred during data migration: {e}")
        supabase_session.rollback()  # Rollback in case of error

    finally:
        # Close the sessions
        sqlite_session.close()
        supabase_session.close()

if __name__ == "__main__":
    migrate_data()
