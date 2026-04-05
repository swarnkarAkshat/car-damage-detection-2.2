import os
from groq import Groq
from fastapi import HTTPException
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Key will be fetched inside the function to ensure it picks up environment changes
def chat_with_bot(message: str, context: str = None) -> str:
    groq_key = os.getenv("GROQ_API_KEY")
    
    # 4. Ensure API key is present before calling
    if not groq_key:
        logger.error("GROQ_API_KEY is missing from environment.")
        return "AI chat currently unavailable (Groq API Key Missing). Please check your .env file."
        
    try:
        # Initialize client inside the function
        client = Groq(api_key=groq_key)
        # 5. Build messages with context if provided
        messages = []
        if context:
            messages.append({"role": "system", "content": f"You are an AI Car Damage Assistant. The user has just performed a scan with these results: {context}. Use this information to answer their specific questions about the car and its driveability."})
        else:
            messages.append({"role": "system", "content": "You are a helpful AI Car Damage Assistant. You provide advice on car maintenance and damage based on user scans."})
            
        messages.append({"role": "user", "content": message})

        # 6. Call Groq
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        # 7. Return response content
        return response.choices[0].message.content
        
    except Exception as e:
        # 7. Add error handling and terminal logging
        print(f"ERROR: Groq API Exception: {str(e)}")
        
        # Check specifically for authentication errors
        if "401" in str(e) or "authentication" in str(e).lower():
            return "AI chat unavailable: Invalid Groq API Key. Please verify your credentials."
            
        return f"AI chat failed: {str(e)}"
