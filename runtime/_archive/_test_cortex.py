import json, socket

msg = json.dumps({
    "jsonrpc": "2.0",
    "method": "ai.query",
    "id": 2,
    "params": {
        "prompt": "Who is Gaia? Answer in one sentence.",
        "messages": [{"role": "user", "content": "Who is Gaia? Answer in one sentence."}]
    }
}) + "\n"

s = socket.create_connection(("127.0.0.1", 3143), timeout=120)
s.sendall(msg.encode())
data = b""
s.settimeout(120)
while True:
    try:
        chunk = s.recv(65536)
        if not chunk:
            break
        data += chunk
        if b"\n" in data:
            break
    except:
        break
s.close()

r = json.loads(data)
res = r.get("result", {})
print(f"MODEL: {res.get('model', '?')}")
routing = res.get("routing", {})
print(f"ROUTING MODE: {routing.get('mode', '?')}")
print(f"REASONING: {routing.get('reasoning', '?')}")
print(f"MODELS ASKED: {routing.get('models_asked', '?')}")
print(f"WINNER: {routing.get('winner', '?')}")
print(f"TOTAL TIME: {routing.get('total_time', '?')}s")
print(f"ANSWER: {res.get('content', '')[:500]}")
