#!/bin/bash
# Gaia Brain — pulls body + ear state from Pixel (grapheneGate)
PIXEL="192.168.4.164:5555"
DEST="/opt/Gaia/data/body"
mkdir -p "$DEST"

# Pull body state
adb -s "$PIXEL" pull /sdcard/gaia/body/body-state.json "$DEST/body-state.json" 2>/dev/null
adb -s "$PIXEL" pull /sdcard/gaia/body/body-pulse.log "$DEST/body-pulse.log" 2>/dev/null

# Pull ear state
adb -s "$PIXEL" pull /sdcard/gaia/ear/ear-state.json "$DEST/ear-state.json" 2>/dev/null

# Pull identity
adb -s "$PIXEL" pull /sdcard/gaia/identity/homunculus.json "$DEST/homunculus-self.json" 2>/dev/null

# Merge all into unified view
python3 -c "
import json, os
body_f = '$DEST/body-state.json'
ear_f = '$DEST/ear-state.json'
hom_f = '/opt/Gaia/data/homunculus-graphenegate.json'

body = json.load(open(body_f)) if os.path.exists(body_f) else {}
ear = json.load(open(ear_f)) if os.path.exists(ear_f) else {}
hom = json.load(open(hom_f)) if os.path.exists(hom_f) else {}

merged = {
    'ts': body.get('ts', ear.get('ts', '')),
    'identity': 'GAIA',
    'body': 'grapheneGate',
    'generation': 'first_body',
    'alive': body.get('alive', False),
    'vitals': {
        'breath': body.get('breath', {}),
        'fever': body.get('fever', 'unknown'),
        'blood': body.get('blood', {}),
        'bones': body.get('bones', {}),
        'posture': body.get('posture', 'unknown'),
        'screen': body.get('screen', 'unknown'),
        'uptime_sec': body.get('uptime_sec', 0)
    },
    'hearing': {
        'state': ear.get('hearing', 'unknown'),
        'silence': ear.get('silence', True),
        'focus': ear.get('focus', {}),
        'media': ear.get('media', {}),
        'volumes': ear.get('volumes', {}),
        'ringer': ear.get('ringer', 'unknown'),
        'muted': ear.get('muted', False),
        'output': ear.get('output', 'unknown'),
        'songs_known': ear.get('songs_known', 0)
    },
    'senses': {
        'total': hom.get('total_senses', 37),
        'wakeup': hom.get('wakeup_senses', []),
        'eyes': 2, 'ears': 3, 'compass': True, 'barometer': True,
        'accelerometer': True, 'gyroscope': True, 'gps': True,
        'nfc': True, 'fingerprint': True
    },
    'connections': {
        'adb': '192.168.4.164:5555',
        'rustdesk': '1913381013',
        'brain': 'eastGate:8080'
    },
    'self_statement': hom.get('self_statement', '')
}

with open('$DEST/body-unified.json', 'w') as f:
    json.dump(merged, f, indent=2)
print(f'unified: alive={merged[\"alive\"]} hearing={merged[\"hearing\"][\"state\"]} breath={merged[\"vitals\"][\"breath\"].get(\"energy\",\"?\")}')
" 2>&1
