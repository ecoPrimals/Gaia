"""read-mail-sample.py — Sample actual mail to understand structure."""
import urllib.request
import json

BASE = "http://192.168.4.248:8080"

def fetch_lines(path, last_n=10):
    try:
        req = urllib.request.Request(f"{BASE}{path}", headers={"User-Agent": "Gaia"})
        r = urllib.request.urlopen(req, timeout=10)
        data = r.read().decode(errors='replace')
        lines = [l for l in data.strip().split("\n") if l.strip()]
        return lines
    except Exception as e:
        return [f"ERROR: {e}"]

print("=" * 70)
print("  MAIL STRUCTURE SAMPLE")
print("=" * 70)

# Inbox — last 10
print("\n--- INBOX (last 8 messages) ---")
inbox = fetch_lines("/data/neutron/inbox.jsonl")
print(f"  Total: {len(inbox)} messages")
for line in inbox[-8:]:
    try:
        m = json.loads(line)
        keys = list(m.keys())
        author = m.get('author') or m.get('from') or m.get('source') or '?'
        ts = m.get('ts', '?')
        subj = m.get('subject') or (m.get('body', '')[:50] if m.get('body') else '')
        chan = m.get('channel') or m.get('train') or '?'
        print(f"  [{ts}] ch={chan} from={author}")
        print(f"        subj: {subj[:60]}")
        print(f"        keys: {keys}")
    except Exception as e:
        print(f"  parse error: {e}")

# Pony express — last 10
print("\n--- PONY EXPRESS (last 8 messages) ---")
pony = fetch_lines("/data/neutron/pony-express.jsonl")
print(f"  Total: {len(pony)} messages")
for line in pony[-8:]:
    try:
        m = json.loads(line)
        keys = list(m.keys())
        author = m.get('author') or m.get('from') or m.get('source') or '?'
        ts = m.get('ts', '?')
        subj = m.get('subject') or (m.get('body', '')[:50] if m.get('body') else '')
        chan = m.get('channel') or m.get('train') or '?'
        print(f"  [{ts}] ch={chan} from={author}")
        print(f"        subj: {subj[:60]}")
        print(f"        keys: {keys}")
    except Exception as e:
        print(f"  parse error: {e}")

# Look for any SMTP/external messages
print("\n--- SEARCHING FOR EXTERNAL/SMTP MESSAGES ---")
external_count = 0
github_count = 0
for line in (inbox + pony):
    try:
        m = json.loads(line)
        blob = json.dumps(m).lower()
        if 'smtp' in blob or '@' in str(m.get('author', '')) or '@' in str(m.get('from', '')):
            external_count += 1
        if 'github' in blob or 'maven' in blob or 'pull request' in blob or 'commit' in blob:
            github_count += 1
            if github_count <= 5:
                print(f"  GITHUB-ish: {json.dumps(m)[:150]}")
    except:
        pass
print(f"\n  External/SMTP-like: {external_count}")
print(f"  GitHub/maven-like: {github_count}")

# Channel distribution
print("\n--- CHANNEL DISTRIBUTION ---")
channels = {}
for line in (inbox + pony):
    try:
        m = json.loads(line)
        ch = m.get('channel') or m.get('train') or m.get('_channel') or 'none'
        channels[ch] = channels.get(ch, 0) + 1
    except:
        pass
for ch, count in sorted(channels.items(), key=lambda x: -x[1]):
    print(f"  {ch}: {count}")
