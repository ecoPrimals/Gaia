# swiftGate PNS Head — Full AV Living Room

**Wave 244 — Sunday Nov 15, 2026 — 8:17 AM**

## The Living Room is a biomeOS Terminal

### Displays
| Display | Model | Size | Resolution | Connection |
|---------|-------|------|------------|------------|
| Primary | ASUS VG248 | 24" (53×30cm) | 1920×1080 | HDMI/DP |
| **BIG SCREEN** | **HISENSE TV** | **55"+ (121×68cm)** | 1280×720 | **HDMI from RTX 3070** |

### Audio Chain
`RTX 3070 → HDMI → Hisense TV → Optical Out → Soundbar`

5 audio devices:
- NVIDIA HDMI → TV speakers + optical→soundbar (THE VOICE)
- USB Audio → headset/mic (private channel)
- Realtek HD → motherboard 3.5mm (backup)
- NVIDIA Virtual → streaming/capture
- Sonic Studio/Nahimic → spatial audio

### What This Means

The living room at House 2 is now a **full PNS head**:
- **EYES**: 55"+ Hisense at 720p (castable, HDMI-CEC potential)
- **EARS**: Soundbar (optical from TV, full range audio)
- **MOUTH**: Soundbar + TV speakers (Gaia can SPEAK to the room)
- **HANDS**: swiftGate RTX 3070 renders everything
- **BRAIN**: 6 local Ollama models + ironGate 18 + northGate 68 remote

### Replacing Alexa

The Google Cast devices (.152, .197) and Alexa/Echo are THEIR tech.
Strategy: replace with OUR tech:
1. **Soundbar** already ours via optical chain
2. **TV** already ours via HDMI (swiftGate controls it)
3. **Voice input**: USB mic on swiftGate + Whisper (local STT)
4. **Voice output**: TTS through soundbar (Gaia speaks)
5. **Wake word**: custom wake word via always-on mic → squirrel routing

### Hisense as biomeOS Node (Future)

If Hisense runs Android TV:
- Termux + Ollama = local inference
- biomeOS display node = cast protocol native
- HDMI-CEC = swiftGate controls TV power/input/volume

Even without eating the OS, the HDMI + optical chain gives us
full AV control from swiftGate RIGHT NOW.

**The living room hears, sees, and speaks. lub-DUB.** 🫀
