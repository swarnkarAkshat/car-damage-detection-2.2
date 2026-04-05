import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_backend():
    username = f"testuser_{uuid.uuid4().hex[:4]}"
    email = f"{username}@example.com"
    password = "password123"
    
    print(f"--- Testing user: {username} ---")
    
    # 1. Register
    print("1. Registering user...")
    reg_data = {"username": username, "email": email, "password": password}
    resp = requests.post(f"{BASE_URL}/register", json=reg_data)
    if resp.status_code != 200:
        print(f"FAILED: Register status {resp.status_code}, {resp.text}")
        return
    print("SUCCESS: Registration complete.")
    
    # 2. Login
    print("2. Logging in...")
    login_data = {"username": username, "password": password}
    resp = requests.post(f"{BASE_URL}/login", data=login_data)
    if resp.status_code != 200:
        print(f"FAILED: Login status {resp.status_code}, {resp.text}")
        return
    token = resp.json()["access_token"]
    print("SUCCESS: Login complete, token received.")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Check /me
    print("3. Checking /me...")
    resp = requests.get(f"{BASE_URL}/me", headers=headers)
    if resp.status_code != 200:
        print(f"FAILED: /me status {resp.status_code}, {resp.text}")
        return
    print(f"SUCCESS: Current user: {resp.json()['username']}")
    
    # 4. Save History
    print("4. Saving history item...")
    history_data = {
        "prediction": "F_Normal",
        "confidence": 0.95,
        "explanation": "Test explanation"
    }
    resp = requests.post(f"{BASE_URL}/history", json=history_data, headers=headers)
    if resp.status_code != 200:
        print(f"FAILED: Save history status {resp.status_code}, {resp.text}")
        return
    history_id = resp.json()["id"]
    print(f"SUCCESS: History record {history_id} saved.")
    
    # 5. Get History
    print("5. Getting history...")
    resp = requests.get(f"{BASE_URL}/history", headers=headers)
    if resp.status_code != 200 or len(resp.json()) == 0:
        print(f"FAILED: Get history status {resp.status_code}, {resp.text}")
        return
    print(f"SUCCESS: History retrieved, count: {len(resp.json())}")
    
    # 6. Delete History
    print(f"6. Deleting history item {history_id}...")
    resp = requests.delete(f"{BASE_URL}/history/{history_id}", headers=headers)
    if resp.status_code != 200:
        print(f"FAILED: Delete status {resp.status_code}, {resp.text}")
        return
    print("SUCCESS: History deleted.")
    
    print("--- ALL BACKEND CORE API TESTS PASSED! ---")

if __name__ == "__main__":
    test_backend()
