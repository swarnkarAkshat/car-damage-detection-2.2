import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

env_path = Path('backend/.env')
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

print(f"Testing with key: {api_key[:6]}...{api_key[-4:]}")

client = genai.Client(api_key=api_key)

try:
    print("Listing models...")
    models = client.models.list()
    # In the new SDK, models.list() might return a list or an iterator
    for m in models:
        print(f"- {m.name}")
except Exception as e:
    import traceback
    traceback.print_exc()
