import requests, base64

auth_header = {'Authorization': 'Basic ' + base64.b64encode(b'admin:admin').decode()}

try:
    r = requests.get('http://localhost:4874/-/verdaccio/packages', headers=auth_header)
    print("STATUS", r.status_code)
    print("JSON", r.json()[:2] if r.status_code == 200 else r.text)
except Exception as e:
    print("ERROR", str(e))
