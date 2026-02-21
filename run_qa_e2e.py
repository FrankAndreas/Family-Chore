import json
import urllib.request

BASE_URL = "http://localhost:8000"

def request(method, path, data=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    req_data = json.dumps(data).encode("utf-8") if data else None
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.read().decode()}")
        return None

def run():
    print("Testing API endpoints...")
    # 1. Get roles
    roles = request("GET", "/roles/")
    if not roles:
        print("No roles found.")
        return
    admin_role = next((r for r in roles if r["name"] == "Admin"), roles[0])

    # 2. Add an Admin User (or use existing)
    users = request("GET", "/users/")
    admin_user = next((u for u in users if u["role"]["name"] == "Admin"), None)
    if not admin_user:
        admin_user = request("POST", "/users/", {"nickname": "QAAdminUser", "login_pin": "1234", "role_id": admin_role["id"]})
        print(f"Created Admin: {admin_user['id']}")

    # 3. Update Admin Email
    updated = request("PUT", f"/users/{admin_user['id']}", {"email": "qaadmin@test.local", "notifications_enabled": True})
    print(f"Updated Admin: Email={updated.get('email')} / Notif={updated.get('notifications_enabled')}")

    # 4. Trigger Daily Reset (should trigger emails if pending daily tasks exist)
    result = request("POST", "/daily-reset/")
    print(f"Daily reset triggered: {result}")

    print("Success. Ensure emails are logging in the backend terminal.")

if __name__ == "__main__":
    run()
