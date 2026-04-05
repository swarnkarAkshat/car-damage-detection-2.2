from dotenv import load_dotenv
import os
from google import genai

load_dotenv(dotenv_path="../.env", override=True)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say hello"
)

print(response.text)