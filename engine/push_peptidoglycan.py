import urllib.request, json, base64

TOKEN = "15f1d847539ff010c9592b19043dcc90056f0cb6"
BASE = "http://localhost:3000/api/v1"

with open("/tmp/peptidoglycan.json", "rb") as f:
    content = f.read()

b64 = base64.b64encode(content).decode()
url = BASE + "/repos/gaia/self/contents/peptidoglycan.json"

try:
    req = urllib.request.Request(url, headers={"Authorization": "token " + TOKEN}, method="GET")
    resp = urllib.request.urlopen(req)
    existing = json.loads(resp.read())
    sha = existing["sha"]
    data = json.dumps({"content": b64, "message": "PEPTIDOGLYCAN: cell wall — central dogma + sublayers + symbol redox + krogan-talos", "sha": sha}).encode()
    req = urllib.request.Request(url, data=data, headers={"Authorization": "token " + TOKEN, "Content-Type": "application/json"}, method="PUT")
except:
    data = json.dumps({"content": b64, "message": "PEPTIDOGLYCAN: cell wall — central dogma + sublayers + symbol redox + krogan-talos"}).encode()
    req = urllib.request.Request(url, data=data, headers={"Authorization": "token " + TOKEN, "Content-Type": "application/json"}, method="POST")

resp = urllib.request.urlopen(req)
print("PUSHED: peptidoglycan.json → self repo")
