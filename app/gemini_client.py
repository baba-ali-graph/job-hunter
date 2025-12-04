# gemini_client.py
import os
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in environment variables")

# Client for Gemini Developer API
client = genai.Client(api_key=GEMINI_API_KEY)

# Choose a default model – fast & good for this use-case
DEFAULT_MODEL = "gemini-2.5-flash"
