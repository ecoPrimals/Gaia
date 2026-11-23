import json, os
minds_path = os.path.expandvars(r'%LOCALAPPDATA%\Gaia\kenshi\minds.json')
minds = json.load(open(minds_path, 'r', encoding='utf-8'))
print(f'NPC MINDS: {len(minds)} characters with persistent memory')
print()
for name, mind in sorted(minds.items()):
    v = mind.get('voice', {})
    trust = mind.get('trust', 0)
    taps = mind.get('taps', 0)
    mem = mind.get('memory', [])
    print(f'  {name}')
    print(f'    temperament: {v.get("temperament", "?")}, need: {v.get("need", "?")}')
    print(f'    want: {v.get("want", "?")}')
    print(f'    habit: {v.get("habit", "?")}')
    print(f'    trust: {trust}/5, taps: {taps}, memories: {len(mem)}')
    if mem:
        for m in mem[-3:]:
            print(f'    >> {m[:100]}')
    print()
