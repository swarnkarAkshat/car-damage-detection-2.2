import sys, json, urllib.request, urllib.error, urllib.parse
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

BASE = "http://127.0.0.1:8000"
USERNAME = "akshat2"
EMAIL    = "akshat2@test.com"
PASSWORD = "demo1234"

results = []

# 1. Register
try:
    data = json.dumps({"username": USERNAME, "email": EMAIL, "password": PASSWORD}).encode()
    req = urllib.request.Request(f"{BASE}/register", data=data,
          headers={"Content-Type": "application/json"}, method="POST")
    r = urllib.request.urlopen(req)
    results.append(f"REGISTER: OK {r.status} {r.read().decode()}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    results.append(f"REGISTER: HTTP {e.code} {body}")
except Exception as e:
    results.append(f"REGISTER: ERROR {e}")

# 2. Login
token = None
try:
    form = urllib.parse.urlencode({"username": USERNAME, "password": PASSWORD}).encode()
    req = urllib.request.Request(f"{BASE}/login", data=form,
          headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    r = urllib.request.urlopen(req)
    d = json.loads(r.read().decode())
    token = d.get("access_token")
    results.append(f"LOGIN: OK token={token[:20] if token else 'NONE'}...")
except urllib.error.HTTPError as e:
    results.append(f"LOGIN: HTTP {e.code} {e.read().decode()}")
except Exception as e:
    results.append(f"LOGIN: ERROR {e}")

# 3. /me
if token:
    try:
        req = urllib.request.Request(f"{BASE}/me",
              headers={"Authorization": f"Bearer {token}"}, method="GET")
        r = urllib.request.urlopen(req)
        results.append(f"ME: OK {r.read().decode()}")
    except urllib.error.HTTPError as e:
        results.append(f"ME: HTTP {e.code} {e.read().decode()}")

# Write results to file
with open("_auth_results.txt", "w", encoding="utf-8") as f:
    for line in results:
        f.write(line + "\n")

for line in results:
    print(line)
