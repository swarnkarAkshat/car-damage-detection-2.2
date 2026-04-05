import os
from pathlib import Path
from dotenv import load_dotenv

def test_env_loading():
    # 1. Calculate absolute path to the .env file in the same directory
    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / ".env"
    
    print("--- Environment Loading Debug ---")
    print(f"Target .env path: {env_path}")
    
    # 2. Check if file exists
    if not env_path.exists():
        print(f"ERROR: .env file NOT found at {env_path}")
        return

    # 3. Load with override=True
    # This is the key part that ensures new values replace cached/existing ones
    print(f"Attempting to load .env with override=True...")
    load_dotenv(dotenv_path=env_path, override=True)
    
    print("DEBUG: load_dotenv execution finished.")
    
    # 4. Verify specific keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if gemini_key:
        # Show some characters to verify it's the NEW one
        print(f"SUCCESS: GEMINI_API_KEY loaded: {gemini_key[:6]}...{gemini_key[-4:]}")
    else:
        print("FAILED: GEMINI_API_KEY not found in environment.")

    if groq_key:
        print(f"SUCCESS: GROQ_API_KEY loaded: {groq_key[:6]}...{groq_key[-4:]}")
    else:
        print("FAILED: GROQ_API_KEY not found in environment.")

    print("\n--- Current Working Directory Info ---")
    print(f"Current CWD: {os.getcwd()}")
    print(f"Script Location: {base_dir}")

if __name__ == "__main__":
    test_env_loading()
