import json
with open('c:/Users/mokke/Desktop/Gaia/data/mesh-profile.json') as f:
    p = json.load(f)

print('=== MIKROTIK NEIGHBORS (auto-discovered!) ===')
for n in p['mikrotik'].get('neighbors', []):
    for k, v in n.items():
        print(f'  {k}: {v}')
    print()

print('=== FORGEJO REPOS (all 50) ===')
for r in p['eastgate'].get('forgejo_repos', []):
    name = r['name']
    desc = r['desc'][:60] if r['desc'] else ''
    print(f'  {name:40s} {desc}')
