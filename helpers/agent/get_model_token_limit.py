from lib.genai_client import get_client
import os
from dotenv import load_dotenv

load_dotenv()  
model = os.getenv("MODEL") or ""

async def get_model_token_limit():
    client = get_client()
    model_info = await client.models.get(model=model)
    token_limit = model_info.input_token_limit or 10000
    return token_limit
