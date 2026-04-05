import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_explanation(prediction: str, confidence: float) -> str:
    """
    Generates a technical explanation for car damage using Groq API (Llama-3.1).
    Replaces the previously failing Gemini implementation.
    """
    # 1. Force reload of environment variables
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

    # 2. Key Access
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        logger.error("GROQ_API_KEY is missing from environment.")
        return f"AI explanation unavailable (Missing API Key). Detected: {prediction}."

    try:
        # 3. Initialize Groq Client
        client = Groq(api_key=api_key)
        
        prompt = (
            f"Technical report for car damage: '{prediction}' with {confidence*100:.1f}% confidence. "
            "Explain what this damage implies for the vehicle's structural integrity and next steps. "
            "Keep it under 60 words."
        )
        
        # 4. Use Groq Model
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional automotive structural engineer."},
                {"role": "user", "content": prompt}
            ]
        )
        
        if response and response.choices[0].message.content:
            return response.choices[0].message.content
        return f"Detected {prediction} ({confidence*100:.1f}% confidence). Manual inspection recommended."

    except Exception as e:
        err = str(e)
        logger.error(f"Groq API Error: {err}")
        
        if "429" in err or "rate_limit" in err.lower():
            return "AI service at capacity (Rate Limit). Please try again in 60 seconds."
            
        return f"Technician Note: {prediction} detected. AI summary currently unavailable."
