from langchain_openai import ChatOpenAI
import re 
import json
from dotenv import load_dotenv
import os
load_dotenv()   

def sanitize_json_string(json_string: str) -> str:
    json_string = re.sub(r"[\x00-\x1f\x7f]", "", json_string)
    return json_string



prompt = """
Given the following query:

{query}

Your task is to generate a broad set of one-word general keywords that represent the main ideas, themes, or concepts from the query. These keywords will be used to search through a collection of posts and help retrieve the most relevant results. Consider variations and synonyms to ensure a diverse and comprehensive list.

The output should be a list of one-word keywords related to the query. Generate at least 20-30 different keywords to maximize the search coverage.

Example output json format:

{'keywords':[
    "keyword1",
    "keyword2",
    "keyword3",
    ...
]}
Please ensure the keywords are general and represent the core ideas of the query, avoiding very specific or niche terms unless highly relevant."
Return only JSON response
"""



def LLM(query):
    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("api_key"))
    try:
        messages = [
            {"role": "system", "content": prompt.format(query=query)}
        ]
        response = llm.invoke(messages)
        response = sanitize_json_string(response.content)
        response = json.loads(response)
        return response
    
    except Exception as e:
        print(e)
        return {"keywords": []}
    
LLM("how people send parcels")

prompt2= """
"You are provided with a list of posts in the following JSON format:

json
Copy code
[
    {
        "id": "1",
        "title": "Post Title 1",
        "content": "Detailed description of post 1",
        "tags": ["tag1", "tag2"]
    },
]
Your task is to analyze these posts and identify the top 30 most similar ones based on the following criteria:

Similarity in content, topics, and themes.
Alignment of tags and keywords.
Relevance and cohesion in the ideas presented in the content.
If a certain post has multiple versions, you can select the most recent or well-developed one.
Provide the list of the 30 most similar posts (in terms of content) with their id, title, and similarity score between 0 and 1, where 1 indicates the highest similarity. The final output should be returned in this JSON format:
now from the retrived post just seperate title description and comments. make random user names for comments
json
Copy code
[
    {
        "id": "Post ID",
        "title": "Post Title",
        "description": "Post Description",
        "comments": [{content: 'comment', user: 'user'}]
    },
]
Analyze carefully and provide the top 30 posts based on the criteria mentioned above.
"""

def find_relevant_posts(posts):
    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("api_key"))
    # posts is json

    try:
        messages = [
            {"role": "system", "content": prompt2},
            {"role": "system", "content": json.dumps(posts)},
        ]
        
        response = llm.invoke(messages)
        response = sanitize_json_string(response.content)
        response = json.loads(response)
        return response
    
    except Exception as e:
        print(e)
        return {"posts": []}

