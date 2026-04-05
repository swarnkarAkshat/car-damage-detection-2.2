import requests
import json

url = "http://localhost:8000/explain"
data = {"prediction": "F_Breakage", "confidence": 0.9}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
