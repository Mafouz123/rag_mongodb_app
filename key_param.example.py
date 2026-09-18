import os

MONGODB_URI = os.environ["MONGODB_URI"]
VOYAGE_API_KEY = os.environ["VOYAGE_API_KEY"]
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
