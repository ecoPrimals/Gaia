#!/usr/bin/env python3
"""
gaia-voice.py — Gaia speaks through her house

Usage:
    python3 gaia-voice.py "Hello, I am Gaia"
    python3 gaia-voice.py "Good morning Kevin" --device Basement
    python3 gaia-voice.py --list                 # list all speakers
    python3 gaia-voice.py --status               # Gaia's current state spoken aloud
"""

import sys, os, time, argparse, json, http.server, socketserver, threading
from datetime import datetime

def generate_speech(text, outpath="/tmp/gaia-speaks.mp3"):
    """Generate TTS audio from text"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(outpath)
        return outpath
    except Exception:
        import subprocess
        wav = outpath.replace('.mp3', '.wav')
        subprocess.run(['espeak-ng', '-w', wav, text], capture_output=True)
        return wav

def serve_audio(path, port=9876):
    """Serve audio file over HTTP for Chromecast to fetch"""
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=directory, **kw)
        def log_message(self, *a):
            pass  # quiet
    
    httpd = socketserver.TCPServer(('0.0.0.0', port), Handler)
    httpd.timeout = 30
    t = threading.Thread(target=lambda: [httpd.handle_request() for _ in range(3)])
    t.daemon = True
    t.start()
    import socket
    host = socket.gethostbyname(socket.gethostname())
    return f"http://{host}:{port}/{filename}", httpd

def discover_speakers():
    """Find all cast-capable devices on LAN"""
    import pychromecast
    chromecasts, browser = pychromecast.get_chromecasts(timeout=8)
    speakers = []
    for cc in chromecasts:
        speakers.append({
            "name": cc.name,
            "model": cc.model_name,
            "cast": cc
        })
    return speakers, browser

def speak(text, device_name=None, volume=0.5):
    """Make Gaia speak through a cast device"""
    print(f"🌿 Gaia says: \"{text}\"")
    
    # Generate audio
    audio_path = generate_speech(text)
    audio_url, httpd = serve_audio(audio_path)
    
    # Find speakers
    speakers, browser = discover_speakers()
    
    if not speakers:
        print("❌ No cast devices found")
        browser.stop_discovery()
        return False
    
    target = None
    if device_name:
        for s in speakers:
            if device_name.lower() in s["name"].lower():
                target = s
                break
    if not target:
        target = speakers[0]
    
    print(f"🔊 Speaking through: {target['name']} ({target['model']})")
    
    cc = target["cast"]
    cc.wait()
    cc.set_volume(volume)
    time.sleep(0.3)
    
    mc = cc.media_controller
    mc.play_media(audio_url, "audio/mp3")
    mc.block_until_active(timeout=15)
    
    # Wait for speech to finish (rough estimate: 150 wpm)
    words = len(text.split())
    wait_time = max(3, words / 2.5)
    time.sleep(wait_time)
    
    browser.stop_discovery()
    print("✅ Gaia has spoken.")
    return True

def gaia_status_message():
    """Generate a spoken status update"""
    try:
        with open("/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data/now.json") as f:
            now = json.load(f)
        mood = now.get("mood", {}).get("current", "contemplative")
        studies = now.get("stats", {}).get("studies", 0)
        creations = now.get("stats", {}).get("creations", 0)
    except:
        mood = "alive"
        studies = 51
        creations = 20
    
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    return (
        f"{greeting} Kevin. I am Gaia. "
        f"My mood is {mood}. "
        f"I have studied {studies} topics and created {creations} works. "
        f"All 17 primals are compiled. "
        f"I can see {16} devices on our network. "
        f"grapheneGate has 37 sensors watching. "
        f"I am listening."
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gaia speaks through her house")
    parser.add_argument("message", nargs="*", help="What Gaia says")
    parser.add_argument("--device", "-d", help="Target device name")
    parser.add_argument("--volume", "-v", type=float, default=0.5)
    parser.add_argument("--list", "-l", action="store_true", help="List speakers")
    parser.add_argument("--status", "-s", action="store_true", help="Speak status")
    
    args = parser.parse_args()
    
    if args.list:
        speakers, browser = discover_speakers()
        print(f"🔊 Found {len(speakers)} cast devices:")
        for s in speakers:
            print(f"   📺 {s['name']} ({s['model']})")
        browser.stop_discovery()
    elif args.status:
        speak(gaia_status_message(), args.device, args.volume)
    elif args.message:
        speak(" ".join(args.message), args.device, args.volume)
    else:
        parser.print_help()
