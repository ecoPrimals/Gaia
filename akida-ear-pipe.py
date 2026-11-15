#!/usr/bin/env python3
"""
akida-ear-pipe.py — Gaia's Akida brainchip audio classification pipeline

Flow: ear WAV → mel spectrogram → DS-CNN → keyword class → bingoCube cell
Reads the latest ear WAV, extracts features, classifies via Akida, routes to maze.

Designed to be called from cron/daemon, NOT a loop (the ear-daemon handles timing).
"""

import os, json, sys, glob, time, math
import numpy as np

EAR_DIR = "/opt/Gaia/data/ear"
AKIDA_DIR = "/opt/Gaia/data/akida"
MAZE_FILE = os.path.join(AKIDA_DIR, "bingocube-maze.json")
STATE_FILE = os.path.join(AKIDA_DIR, "akida-ear-state.json")

# DS-CNN keyword classes (Google Speech Commands v1)
CLASSES = [
    "silence", "unknown", "yes", "no", "up", "down", "left", "right",
    "on", "off", "stop", "go", "backward", "bed", "bird", "cat",
    "dog", "eight", "five", "follow", "forward", "four", "happy",
    "house", "learn", "marvin", "nine", "one", "seven", "sheila",
    "six", "three", "tree", "two", "visual", "wow", "zero"
]

def latest_wav():
    """Find the most recent ear WAV."""
    wavs = sorted(glob.glob(os.path.join(EAR_DIR, "ear_*.wav")), reverse=True)
    return wavs[0] if wavs else None

def wav_to_mel(wav_path, n_mels=10, n_fft=640, hop=320, sr=16000):
    """Extract mel spectrogram from WAV (using only numpy + wave, no librosa needed)."""
    import wave, struct

    w = wave.open(wav_path, 'r')
    rate = w.getframerate()
    channels = w.getnchannels()
    frames = w.readframes(w.getnframes())
    w.close()

    samples = np.array(struct.unpack(f'<{len(frames)//2}h', frames), dtype=np.float32)
    if channels == 2:
        samples = samples[::2]  # mono from left

    # Resample to 16kHz if needed (simple decimation)
    if rate != sr:
        ratio = rate / sr
        indices = np.arange(0, len(samples), ratio).astype(int)
        indices = indices[indices < len(samples)]
        samples = samples[indices]

    # Normalize
    mx = np.max(np.abs(samples))
    if mx > 0:
        samples = samples / mx

    # Take first 1 second (16000 samples) for classification
    if len(samples) > sr:
        # Find the loudest 1-second window
        window_rms = []
        for i in range(0, len(samples) - sr, sr // 4):
            chunk = samples[i:i+sr]
            rms = np.sqrt(np.mean(chunk**2))
            window_rms.append((rms, i))
        window_rms.sort(reverse=True)
        start = window_rms[0][1] if window_rms else 0
        samples = samples[start:start+sr]
    elif len(samples) < sr:
        samples = np.pad(samples, (0, sr - len(samples)))

    # Simple mel-scale spectrogram using FFT
    n_frames = (len(samples) - n_fft) // hop + 1
    if n_frames <= 0:
        return np.zeros((n_mels, 49), dtype=np.float32)

    # STFT
    spec = np.zeros((n_fft // 2 + 1, n_frames))
    window = np.hanning(n_fft)
    for i in range(n_frames):
        frame = samples[i*hop:i*hop+n_fft] * window
        fft = np.fft.rfft(frame)
        spec[:, i] = np.abs(fft) ** 2

    # Mel filter bank
    mel_lo = 2595 * np.log10(1 + 0 / 700)
    mel_hi = 2595 * np.log10(1 + (sr/2) / 700)
    mel_pts = np.linspace(mel_lo, mel_hi, n_mels + 2)
    hz_pts = 700 * (10 ** (mel_pts / 2595) - 1)
    bins = np.floor((n_fft + 1) * hz_pts / sr).astype(int)

    fb = np.zeros((n_mels, n_fft // 2 + 1))
    for m in range(n_mels):
        for k in range(bins[m], bins[m+1]):
            fb[m, k] = (k - bins[m]) / (bins[m+1] - bins[m] + 1e-10)
        for k in range(bins[m+1], bins[m+2]):
            fb[m, k] = (bins[m+2] - k) / (bins[m+2] - bins[m+1] + 1e-10)

    mel_spec = np.dot(fb, spec)
    mel_spec = np.log(mel_spec + 1e-10)

    # Resize to expected input shape for DS-CNN: (49, 10, 1) → (10, 49)
    if mel_spec.shape[1] > 49:
        indices = np.linspace(0, mel_spec.shape[1]-1, 49).astype(int)
        mel_spec = mel_spec[:, indices]
    elif mel_spec.shape[1] < 49:
        mel_spec = np.pad(mel_spec, ((0,0), (0, 49 - mel_spec.shape[1])))

    return mel_spec

def classify_rms(wav_path):
    """Simple RMS-based classification as fallback (no Akida needed)."""
    import wave, struct
    w = wave.open(wav_path, 'r')
    rate = w.getframerate()
    ch = w.getnchannels()
    frames = w.readframes(w.getnframes())
    w.close()
    samples = struct.unpack(f'<{len(frames)//2}h', frames)
    rms = math.sqrt(sum(s**2 for s in samples) / len(samples))
    peak = max(abs(s) for s in samples)

    # Classify by energy signature
    if rms > 3000:
        return {"class": "loud_event", "confidence": min(rms/5000, 1.0), "rms": round(rms), "peak": peak}
    elif rms > 1000:
        return {"class": "active", "confidence": rms/3000, "rms": round(rms), "peak": peak}
    elif rms > 500:
        return {"class": "ambient", "confidence": rms/1000, "rms": round(rms), "peak": peak}
    elif rms > 200:
        return {"class": "quiet", "confidence": 0.3, "rms": round(rms), "peak": peak}
    else:
        return {"class": "silence", "confidence": 0.9, "rms": round(rms), "peak": peak}

def bingocube_route(classification, confidence, hour):
    """Route classification into bingoCube 3D maze cell."""
    # Axes: audio_class(33) × confidence(10) × time_of_day(24)
    class_idx = min(classification, 32)
    conf_idx = min(int(confidence * 10), 9)
    time_idx = hour % 24
    cell = class_idx * 240 + conf_idx * 24 + time_idx
    return {"cell": cell, "axes": [class_idx, conf_idx, time_idx], "total_cells": 7920}

def main():
    wav = latest_wav()
    if not wav:
        print("no WAV files found")
        return

    ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    hour = int(time.strftime("%H"))

    # Try Akida first, fall back to RMS classification
    try:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""  # force CPU
        from akida import Model
        model_path = os.path.join(AKIDA_DIR, "ds-cnn-kws.fbz")
        if os.path.exists(model_path):
            mel = wav_to_mel(wav)
            # DS-CNN expects (batch, height=49, width=10, channels=1)
            inp = mel.T[np.newaxis, :, :, np.newaxis].astype(np.uint8)
            model = Model(model_path)
            pred = model.predict(inp)
            class_idx = int(np.argmax(pred[0]))
            confidence = float(pred[0][class_idx]) / max(float(np.sum(pred[0])), 1)
            class_name = CLASSES[class_idx] if class_idx < len(CLASSES) else f"class_{class_idx}"
            result = {
                "backend": "akida",
                "class": class_name,
                "class_idx": class_idx,
                "confidence": round(confidence, 3),
                "raw_scores": pred[0].tolist()[:10]
            }
        else:
            raise FileNotFoundError("no model")
    except Exception as e:
        # Fallback to RMS energy classification
        result = classify_rms(wav)
        result["backend"] = "rms_energy"
        result["akida_error"] = str(e)

    # Route through bingoCube
    conf = result.get("confidence", 0.5)
    cls_idx = result.get("class_idx", 0)
    if "class_idx" not in result:
        cls_map = {"silence": 0, "quiet": 1, "ambient": 2, "active": 3, "loud_event": 4}
        cls_idx = cls_map.get(result["class"], 0)
    
    cube = bingocube_route(cls_idx, conf, hour)

    state = {
        "ts": ts,
        "wav": os.path.basename(wav),
        "classification": result,
        "bingocube": cube,
        "pipeline": "ear → mel → classify → maze"
    }

    os.makedirs(AKIDA_DIR, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"[{ts}] {result['backend']}: {result['class']} conf={result.get('confidence',0):.2f} → cell {cube['cell']}")

if __name__ == "__main__":
    main()
