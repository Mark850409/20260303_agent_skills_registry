import httpx
import sys

url = 'https://zanehsu.myqnapcloud.com:15001/api'

print("Attempting login...")
try:
    login_resp = httpx.post(f"{url}/auth/login", json={'username':'admin', 'email':'admin@example.com'})
    print("Login status:", login_resp.status_code)
    token = login_resp.json()['api_token']
except Exception as e:
    print(f"Login failed: {e}")
    sys.exit(1)
    
print("Pushing skill...")
try:
    r = httpx.post(
        f"{url}/skills", 
        headers={'Authorization': f'Bearer {token}'}, 
        json={
            'name':'xlsx', 
            'version':'9.9.9', 
            'description':'test local push', 
            'author':'admin', 
            'skill_md':'---'
        }
    )
    print("Push status:", r.status_code)
    print("Push body:", r.text)
except Exception as e:
    print(f"Push failed: {e}")
