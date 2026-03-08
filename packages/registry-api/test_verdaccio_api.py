import requests
import base64
import json

auth_header = {'Authorization': 'Basic ' + base64.b64encode(b"admin:admin").decode()}

urls = [
    "http://verdaccio:4873/-/verdaccio/packages",
    "http://verdaccio:4873/npm/-/verdaccio/packages",
    "http://verdaccio:4873/-/verdaccio/search",
    "http://verdaccio:4873/npm/-/verdaccio/search",
    "http://verdaccio:4873/-/all",
    "http://verdaccio:4873/npm/-/all",
]

for url in urls:
    print(f"Testing {url}")
    try:
        resp = requests.get(url, headers=auth_header, timeout=5)
        print(f"Status: {resp.status_code}")
        print(f"Content: {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)
