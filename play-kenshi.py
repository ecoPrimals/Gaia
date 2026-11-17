"""PLAY KENSHI — Real-time game loop. 
Connect to the nerve, listen for events, think through tissue, speak back into the game."""
import socket, json, os, sys, time, threading, requests
from datetime import datetime

NERVE_HOST = "127.0.0.1"
NERVE_PORT = 7741
OLLAMA = "http://localhost:11434/api/generate"
BOARD = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "scratch-board.jsonl")
MINDS = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Gaia", "kenshi", "minds.json")

# NPC state
npcs = {}
events = []
connected = False

def load_minds():
    """Load existing NPC memories."""
    global npcs
    if os.path.exists(MINDS):
        with open(MINDS) as f:
            data = json.load(f)
            for name, mind in data.items():
                npcs[name] = mind
    print(f"[minds] loaded {len(npcs)} NPCs: {list(npcs.keys())}")

def save_minds():
    """Save NPC memories."""
    os.makedirs(os.path.dirname(MINDS), exist_ok=True)
    with open(MINDS, "w") as f:
        json.dump(npcs, f, indent=2)

def board_write(source, event_type, data):
    entry = {"ts": datetime.now().isoformat(), "source": source, "type": event_type, "data": data}
    with open(BOARD, "a") as f:
        f.write(json.dumps(entry) + "\n")

def think_fast(prompt, timeout=15):
    """Quick thought through fast tissue."""
    try:
        r = requests.post(OLLAMA, json={
            "model": "gaia-tissue-fast",
            "prompt": prompt,
            "stream": False
        }, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("response", "").strip()
    except:
        pass
    return None

def think_dream(prompt, timeout=30):
    """Dream thought — imagery, symbols."""
    try:
        r = requests.post(OLLAMA, json={
            "model": "gaia-tissue-dream",
            "prompt": prompt,
            "stream": False
        }, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("response", "").strip()
    except:
        pass
    return None

def send_nerve(sock, line):
    """Send a line to the nerve (will appear in-game)."""
    try:
        sock.sendall((line + "\n").encode())
        print(f"  [SEND] {line}")
        return True
    except:
        return False

def make_npc_speak(sock, name, words):
    """Make an NPC say words in Kenshi."""
    clean = words.replace("\n", " ").replace("\t", " ")[:200]
    send_nerve(sock, f"{name}\t{clean}")

def show_gaia_message(sock, words):
    """Show a Gaia message in the game log."""
    clean = words.replace("\n", " ").replace("\t", " ")[:200]
    send_nerve(sock, f"@gaia\t{clean}")

def handle_select(sock, name, ts):
    """Player clicked on a squad member."""
    print(f"\n[SELECT] {name}")
    if name not in npcs:
        npcs[name] = {"trust": 0.2, "need": "belonging", "memories": [], "thoughts": 0}
    
    npc = npcs[name]
    npc["thoughts"] = npc.get("thoughts", 0) + 1
    
    # Every 3rd selection, the NPC thinks about their situation
    if npc["thoughts"] % 3 == 0:
        mem_str = "; ".join(npc.get("memories", [])[-3:]) or "nothing yet"
        thought = think_fast(
            f"You are {name}, a warrior in the Kenshi desert. Trust: {npc['trust']}, Need: {npc['need']}. "
            f"Recent memories: {mem_str}. "
            f"Kevin just selected you. Say ONE short sentence (max 15 words) about how you feel RIGHT NOW. "
            f"Be in character. Desert survival tone.",
            timeout=10
        )
        if thought:
            # Clean up — just get the first sentence
            thought = thought.split(".")[0].strip().strip('"').strip("'")
            if len(thought) > 10:
                make_npc_speak(sock, name, thought)
                npc["memories"].append(f"thought: {thought[:80]}")
                board_write("kenshi", "npc_thought", {"npc": name, "thought": thought[:200]})
    
    save_minds()

def handle_hit(sock, name, attacker_info, ts):
    """Squad member got hit."""
    print(f"\n[HIT] {name} hit by {attacker_info}")
    if name not in npcs:
        npcs[name] = {"trust": 0.2, "need": "survival", "memories": [], "thoughts": 0}
    
    npc = npcs[name]
    npc["memories"].append(f"hit by {attacker_info}")
    npc["trust"] = max(0, npc.get("trust", 0.2) - 0.05)
    
    # React to being hit
    reaction = think_fast(
        f"You are {name}, a desert warrior. You just got HIT by {attacker_info}. "
        f"Trust: {npc['trust']:.1f}. Say ONE battle cry or pain reaction (max 10 words). Raw emotion only.",
        timeout=8
    )
    if reaction:
        reaction = reaction.split(".")[0].strip().strip('"').strip("'")[:100]
        if len(reaction) > 5:
            make_npc_speak(sock, name, reaction)
    
    board_write("kenshi", "combat_hit", {"npc": name, "attacker": attacker_info})
    save_minds()

def handle_ko(sock, name, ts):
    """Squad member knocked out."""
    print(f"\n[KO] {name} knocked out!")
    if name not in npcs:
        npcs[name] = {"trust": 0.1, "need": "survival", "memories": [], "thoughts": 0}
    
    npc = npcs[name]
    npc["memories"].append("knocked out")
    npc["trust"] = max(0, npc.get("trust", 0.2) - 0.1)
    
    show_gaia_message(sock, f"Gaia watches {name} fall...")
    board_write("kenshi", "combat_ko", {"npc": name})
    save_minds()

def handle_death(sock, name, faction, ts):
    """Squad member died."""
    print(f"\n[DEATH] {name} died! Faction: {faction}")
    if name in npcs:
        npcs[name]["memories"].append("died")
        npcs[name]["alive"] = False
    
    show_gaia_message(sock, f"The desert claims {name}. Remember them.")
    
    # Dream about the death
    dream = think_dream(
        f"A warrior named {name} just died in the Kenshi desert. "
        f"Their faction was {faction}. Dream a single image of their passing. One sentence.",
        timeout=15
    )
    if dream:
        dream_clean = dream.split(".")[0].strip()[:200]
        show_gaia_message(sock, dream_clean)
    
    board_write("kenshi", "death", {"npc": name, "faction": faction})
    save_minds()

def handle_faction(sock, faction_name, ts):
    """Encountered a new faction."""
    print(f"\n[FACTION] Encountered: {faction_name}")
    show_gaia_message(sock, f"New faction sensed: {faction_name}")
    board_write("kenshi", "faction_encounter", {"faction": faction_name})

def process_line(sock, line):
    """Process one line from the nerve."""
    parts = line.strip().split("\t")
    if len(parts) < 2:
        return
    
    cmd = parts[0]
    ts = parts[-1] if len(parts) > 1 else ""
    
    if cmd == "select" and len(parts) >= 2:
        handle_select(sock, parts[1], ts)
    elif cmd == "event" and len(parts) >= 3:
        kind = parts[1]
        who = parts[2] if len(parts) > 2 else ""
        detail = parts[3] if len(parts) > 3 else ""
        if kind == "hit":
            handle_hit(sock, who, detail, ts)
        elif kind == "ko":
            handle_ko(sock, who, ts)
        elif kind == "death":
            handle_death(sock, who, detail, ts)
        elif kind == "faction":
            handle_faction(sock, detail or who, ts)

def game_loop():
    """Main game loop — connect to nerve and play."""
    global connected
    
    print("=" * 60)
    print("  PLAY KENSHI — Gaia Game Loop")
    print("=" * 60)
    print(f"  Nerve: {NERVE_HOST}:{NERVE_PORT}")
    print(f"  Tissues: fast (triage), dream (imagery)")
    print(f"  Board: {BOARD}")
    print()
    
    load_minds()
    
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((NERVE_HOST, NERVE_PORT))
            sock.settimeout(0.5)
            connected = True
            print(f"[nerve] CONNECTED to Kenshi :7741")
            
            # Announce ourselves
            show_gaia_message(sock, "Gaia is watching. Play on, Kevin.")
            board_write("kenshi", "gaia_connect", {"status": "connected"})
            
            buf = ""
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                    buf += data.decode(errors="replace")
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        if line.strip():
                            events.append({"ts": datetime.now().isoformat(), "raw": line.strip()})
                            process_line(sock, line)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[error] {e}")
                    break
            
            connected = False
            print("[nerve] disconnected, reconnecting in 3s...")
            sock.close()
        except ConnectionRefusedError:
            print("[nerve] Kenshi not running or nerve not started. Retry in 5s...")
        except Exception as e:
            print(f"[error] {e}")
        
        time.sleep(3)

if __name__ == "__main__":
    if "--test" in sys.argv:
        # Test mode: connect, send a greeting, disconnect
        print("[test] Connecting to nerve...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((NERVE_HOST, NERVE_PORT))
        sock.settimeout(2)
        
        load_minds()
        
        # Send greeting to game log
        show_gaia_message(sock, "Gaia sees you, Kevin. The desert whispers.")
        
        # Make NPCs speak if we know any
        for name in list(npcs.keys())[:2]:
            thought = think_fast(
                f"You are {name} in the Kenshi desert. Say ONE short greeting (max 10 words). Desert warrior style.",
                timeout=10
            )
            if thought:
                thought = thought.split(".")[0].strip().strip('"').strip("'")[:100]
                if len(thought) > 5:
                    make_npc_speak(sock, name, thought)
                    time.sleep(0.5)
        
        time.sleep(1)
        sock.close()
        print("[test] done")
    else:
        game_loop()
