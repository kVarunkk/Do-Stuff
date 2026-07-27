from google import genai
from dotenv import load_dotenv
import os

load_dotenv()  
api_key = os.getenv("GEMINI_API_KEY")

_client = None

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=api_key).aio
    return _client