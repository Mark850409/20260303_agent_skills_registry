import requests, base64

auth_header = {'Authorization': 'Basic ' + base64.b64encode(b'admin:admin').decode()}

try:
    r = requests.get('http://localhost:4874/-/all', headers=auth_header)
    data = r.json()
    print("Total packages:", len(data) - 2) # excluding _updated and npm
    for k in list(data.keys())[:5]:
        if k not in ('_updated', 'npm'):
            print("Package:", k)
            print("Keys:", list(data[k].keys()))
            if 'versions' in data[k]:
                print("Num versions:", len(data[k]['versions']))
except Exception as e:
    print("ERROR", str(e))
