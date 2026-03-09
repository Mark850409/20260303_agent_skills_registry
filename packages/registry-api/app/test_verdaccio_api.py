import requests, base64

auth_header = {'Authorization': 'Basic ' + base64.b64encode(b'admin:admin').decode()}

try:
    r = requests.get('http://localhost:4874/-/verdaccio/search', headers=auth_header)
    print("verdaccio search:", r.status_code, r.text[:200])
    
    r = requests.get('http://localhost:4874/-/verdaccio/packages', headers=auth_header)
    print("verdaccio packages:", r.status_code, r.text[:200])

    r = requests.get('http://localhost:4874/-/v1/search?text=', headers=auth_header)
    print("v1 search:", r.status_code, r.text[:200])
except Exception as e:
    print("ERROR", str(e))
