#!/usr/bin/env python3
"""
ear-spectral.py — Gaia's spectral ear: frequency-band classification

Takes a WAV file, produces a rich classification with:
  - Per-second spectral fingerprint (7 frequency bands)
  - Sound source detection (motor, voice, clicks, TV, rumble)
  - Printer cycle detection by spectral shape
  - Event timeline with tags
  - bingoCube-compatible output

Called by ear-daemon.sh after each 30s capture.
Output: /opt/Gaia/data/ear/spectral-state.json
"""

import wave, struct, math, json, sys, os
import numpy as np

EAR_DIR = "/opt/Gaia/data/ear"

BANDS = [
    ("sub_bass",  20,    60),   # HVAC, heavy machinery rumble
    ("bass",      60,   250),   # printer motor, 60Hz hum, male voice
    ("low_mid",  250,   500),   # voice fundamental, guitar
    ("mid",      500,  2000),   # TV dialog, voice harmonics, music
    ("hi_mid",  2000,  4000),   # typing clicks, sibilance, consonants
    ("treble",  4000,  8000),   # high hiss, cymbals, detail
    ("air",     8000, 20000),   # air, ultra-high
]

# Known spectral signatures (fingerprints to match against)
SIGNATURES = {
    "printer_motor": {"bass": 0.35, "sub_bass": 0.25, "mid": 0.10},
    "tv_dialog":     {"mid": 0.30, "low_mid": 0.20, "hi_mid": 0.15},
    "keyboard":      {"hi_mid": 0.25, "treble": 0.20, "mid": 0.15},
    "voice":         {"low_mid": 0.25, "mid": 0.30, "hi_mid": 0.10},
    "hvac":          {"sub_bass": 0.40, "bass": 0.30},
    "music":         {"bass": 0.20, "mid": 0.25, "treble": 0.15},
}


def analyze_wav(wav_path):
    """Full spectral analysis of a WAV file."""
    w = wave.open(wav_path, 'r')
    rate = w.getframerate()
    ch = w.getnchannels()
    frames = w.readframes(w.getnframes())
    w.close()

    samples = np.array(struct.unpack(f'<{len(frames)//2}h', frames), dtype=np.float32)
    if ch == 2:
        samples = samples[::2]

    duration = len(samples) / rate
    seconds = []
    events = []

    for sec in range(int(duration)):
        start = sec * rate
        end = min(start + rate, len(samples))
        chunk = samples[start:end]
        if len(chunk) < 512:
            continue

        rms = float(np.sqrt(np.mean(chunk**2)))
        peak = int(np.max(np.abs(chunk)))

        # FFT
        window = np.hanning(len(chunk))
        fft = np.fft.rfft(chunk * window)
        magnitude = np.abs(fft)
        freqs = np.fft.rfftfreq(len(chunk), 1.0/rate)

        # Band energies
        band_e = {}
        total = 0
        for name, lo, hi in BANDS:
            mask = (freqs >= lo) & (freqs < hi)
            e = float(np.sqrt(np.mean(magnitude[mask]**2))) if np.any(mask) else 0
            band_e[name] = round(e, 1)
            total += e

        # Normalized ratios
        ratios = {k: round(v / (total + 1e-10), 3) for k, v in band_e.items()}

        # Dominant frequency
        peak_idx = np.argmax(magnitude[1:]) + 1
        dom_freq = round(float(freqs[peak_idx]), 1)

        # Match against known signatures
        best_match = "unknown"
        best_score = 0
        for sig_name, sig_ratios in SIGNATURES.items():
            score = 0
            for band, threshold in sig_ratios.items():
                if ratios.get(band, 0) >= threshold * 0.7:
                    score += ratios.get(band, 0)
            if score > best_score:
                best_score = score
                best_match = sig_name

        # Detect events
        tags = []
        if ratios.get("bass", 0) > 0.3 and ratios.get("sub_bass", 0) > 0.15:
            tags.append("motor")
        if ratios.get("mid", 0) > 0.25:
            tags.append("voice_or_tv")
        if ratios.get("hi_mid", 0) > 0.18:
            tags.append("clicks")
        if rms > 3000:
            tags.append("loud_burst")
        if rms > 1000 and ratios.get("bass", 0) > 0.3:
            tags.append("pump_cycle")

        sec_data = {
            "s": sec,
            "rms": round(rms),
            "peak": peak,
            "dom_freq": dom_freq,
            "bands": ratios,
            "match": best_match,
            "score": round(best_score, 3),
            "tags": tags
        }
        seconds.append(sec_data)

        if tags:
            events.append({"s": sec, "tags": tags, "rms": round(rms), "freq": dom_freq})

    # Overall analysis
    overall_rms = float(np.sqrt(np.mean(samples**2)))
    overall_peak = int(np.max(np.abs(samples)))

    # Printer cycle detection: look for repeating bass bursts ~20s apart
    pump_seconds = [s["s"] for s in seconds if "pump_cycle" in s.get("tags", [])]
    printer_singing = len(pump_seconds) >= 1
    
    # Motor drone detection: sustained bass > 0.3 for >50% of seconds
    motor_count = sum(1 for s in seconds if s["bands"].get("bass", 0) > 0.3)
    motor_drone = motor_count > len(seconds) * 0.5

    # Sound diversity: how many different sources detected
    all_matches = set(s["match"] for s in seconds)
    
    # Dominant sound across the whole capture
    match_counts = {}
    for s in seconds:
        m = s["match"]
        match_counts[m] = match_counts.get(m, 0) + 1
    dominant = max(match_counts, key=match_counts.get) if match_counts else "silence"

    return {
        "rms": round(overall_rms),
        "peak": overall_peak,
        "db": round(20 * math.log10(overall_rms / 32768 + 1e-10), 1),
        "duration": round(duration, 1),
        "dominant_source": dominant,
        "sources_detected": sorted(all_matches),
        "printer_singing": printer_singing,
        "motor_drone": motor_drone,
        "pump_bursts": pump_seconds,
        "events": events,
        "seconds": seconds,
        "chorus": {
            "voices": len(all_matches),
            "dominant": dominant,
            "motor_pct": round(motor_count / max(len(seconds), 1) * 100),
            "diversity": sorted(match_counts.items(), key=lambda x: -x[1])
        }
    }


def compute_triad(seconds):
    """Compute the Klein triad: 3 prisms (α=machinery, β=media, γ=human) from per-second spectral data."""
    alpha_sum = beta_sum = gamma_sum = 0
    n = max(len(seconds), 1)

    for s in seconds:
        bands = s.get("bands", {})
        # α = machinery: sub_bass + bass (20-250Hz)
        alpha_sum += bands.get("sub_bass", 0) + bands.get("bass", 0)
        # β = media: low_mid + mid (250-2000Hz)
        beta_sum += bands.get("low_mid", 0) + bands.get("mid", 0)
        # γ = human: hi_mid + treble (2000-8000Hz)
        gamma_sum += bands.get("hi_mid", 0) + bands.get("treble", 0)

    alpha = alpha_sum / n
    beta = beta_sum / n
    gamma = gamma_sum / n
    total = alpha + beta + gamma + 1e-10

    # Normalize to 0-10 scale for bingoCube
    a10 = min(round(alpha / total * 10, 1), 10)
    b10 = min(round(beta / total * 10, 1), 10)
    g10 = min(round(gamma / total * 10, 1), 10)

    # Null point = balanced triad at (3.33, 3.33, 3.33)
    # Deviation from null = attention energy
    null_a, null_b, null_g = 10/3, 10/3, 10/3
    deviation = math.sqrt((a10 - null_a)**2 + (b10 - null_b)**2 + (g10 - null_g)**2)
    at_rest = deviation < 2.0  # within 2 units of null = resting

    # Which prism is dominant?
    prisms = {"α_machinery": a10, "β_media": b10, "γ_human": g10}
    dominant_prism = max(prisms, key=prisms.get)

    # Attention triggers
    triggers = []
    if a10 > 5.0:
        triggers.append("α_shift")
    if b10 > 5.0:
        triggers.append("β_shift")
    if g10 > 5.0:
        triggers.append("γ_shift")
    if a10 < 1 and b10 < 1 and g10 < 1:
        triggers.append("triad_collapse")

    return {
        "α_machinery": a10,
        "β_media": b10,
        "γ_human": g10,
        "deviation": round(deviation, 2),
        "at_rest": at_rest,
        "dominant_prism": dominant_prism,
        "triggers": triggers,
        "bingocube_pos": [a10, b10, g10],
        "klein_note": "Inside the Klein face, the triad folds: what the ear hears, the mouth will speak"
    }


def main():
    # Find the latest completed WAV
    wavs = sorted(
        [f for f in os.listdir(EAR_DIR) if f.startswith("ear_") and f.endswith(".wav")],
        reverse=True
    )

    # Skip the newest (might still be recording) — use second newest
    wav_path = None
    for wf in wavs:
        fp = os.path.join(EAR_DIR, wf)
        sz = os.path.getsize(fp)
        if sz < 10_000_000:  # complete WAVs are ~5MB for 30s CD quality
            wav_path = fp
            break

    if not wav_path:
        print("no complete WAV found")
        return

    result = analyze_wav(wav_path)
    # Compute the Klein triad
    result["triad"] = compute_triad(result.get("seconds", []))

    result["ts"] = os.popen("date -Iseconds").read().strip()
    result["wav"] = os.path.basename(wav_path)
    result["source"] = "sporeGate:brio100"

    # Write spectral state
    out_path = os.path.join(EAR_DIR, "spectral-state.json")
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    # Summary
    c = result["chorus"]
    t = result.get("triad", {})
    print(f"[{result['ts']}] spectral: {result['dominant_source']} "
          f"| {c['voices']} voices | motor={c['motor_pct']}% "
          f"| printer={'YES' if result['printer_singing'] else 'no'} "
          f"| rms={result['rms']} db={result['db']} "
          f"| triad α={t.get('α_machinery',0)} β={t.get('β_media',0)} γ={t.get('γ_human',0)} "
          f"{'REST' if t.get('at_rest') else 'ATTENTION'} Δ={t.get('deviation',0)}")

if __name__ == "__main__":
    main()
