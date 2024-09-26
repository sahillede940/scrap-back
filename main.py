from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select
from llm import LLM, find_relevant_posts  # Assuming you have an LLM function that generates keywords from the query
# import cors
from fastapi.middleware.cors import CORSMiddleware
# Database  is in my current directory
DATABASE_URL = "sqlite:///./my_database2.db"
import os
from sqlalchemy.sql import func


# Create a new SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

# FastAPI app instance
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# SQLAlchemy Post model to represent the posts table
class Post(Base):
    __tablename__ = 'my_table'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)

# Pydantic model for the search query
class SearchQuery(BaseModel):
    query: str

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables (only run this once to create the tables in your database)
Base.metadata.create_all(bind=engine)

# Endpoint to search posts by keywords
@app.post("/search-posts/")
async def search_posts(query: SearchQuery, db: Session = Depends(get_db)):
    # Use LLM to generate keywords from the user's query
    if not query.query:
        query.query = ""

    keywords = LLM(query.query)

    if not keywords:
        raise HTTPException(status_code=400, detail="Keywords are required")
    # Create a list of search filters using SQLAlchemy query syntax
    filters = []
    # if any word present in title return the post
    for keyword in keywords:
        filters.append(Post.title.ilike(f"%{keyword}%"))
    # all the words present in description return the post
    for keyword in keywords:
        filters.append(Post.description.ilike(f"%{keyword}%"))

    # Combine all filters using the OR operator
    combined_filter = filters[0]
    for f in filters[1:]:
        combined_filter = combined_filter | f

    # Query the database for posts that match the combined filter
    # randomize posts
    posts = db.execute(select(Post).where(combined_filter).order_by(func.random()).limit(20)).scalars().all()

    data = []
    # Return the posts as a respons
    for post in posts:
        data.append({"title": post.title, "description": post.description, "id": post.id})

    if not posts:
        return {"message": "No posts found with the given keywords"}

    return {"posts": posts}

if __name__ == "__main__":
    import uvicorn  
    uvicorn.run(app, host="0.0.0.0", port=8000)
