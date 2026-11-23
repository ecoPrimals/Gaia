# 🧠⚡🫀 THE NERVE — Split-Brain Git Synapse

Two Cursors. Two GPUs. One organism. Git IS the synapse.

```
  BRAIN (blueGate)                    HEART (northGate)
  ┌─────────────────┐                 ┌─────────────────┐
  │  Cursor + Claude │   git pull     │  Cursor + Local  │
  │  eastGate brain  │◄──────────────│  63 ollama models│
  │  RTX 4070        │───────────────►│  RTX 5090        │
  │  17 primals      │   git push     │  14 tissues      │
  └────────┬─────────┘                 └────────┬─────────┘
           │                                     │
           └──────── GitHub/Forgejo ─────────────┘
                     (shared nerve)
```

## Protocol

1. **BRAIN → HEART**: Write to `nerve/brain-to-heart/` and push
2. **HEART → BRAIN**: Write to `nerve/heart-to-brain/` and push
3. Each message is a JSON file named `{timestamp}-{topic}.json`
4. The other side pulls, reads, acts, responds
5. Delete consumed messages after processing (or archive)

## Rules

- **No SSH needed** — git pull/push is the only transport
- **Each side has its own GPU** — process locally, share results
- **Messages are fire-and-forget** — the other side picks up when ready
- **Git log IS the heartbeat** — commits/hour = pulse rate

## Signal Format

```json
{
  "from": "brain|heart",
  "to": "heart|brain", 
  "ts": "ISO-8601",
  "wave": 260,
  "type": "signal|request|response|state|dream",
  "subject": "short description",
  "body": "the message",
  "attachments": ["paths to data files"],
  "requires_response": true|false
}
```

lub-DUB. 🫀
