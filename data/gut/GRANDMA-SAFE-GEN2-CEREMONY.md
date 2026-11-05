# 🔑 Gen 2 Ceremony — Grandma-Safe Guide

**What we're doing**: Making your phone and your security key say hello to each other, creating a new identity key.

**What you need**:
- Your phone (Pixel 8a — "grapheneGate")
- Your SoloKey (the little USB-C stick with the gold circle)
- This computer (northGate — where you're reading this)

---

## Before You Start

The SoloKey is currently plugged into THIS computer (northGate).
We're going to move it to the phone.

---

## Step 1: Unplug the SoloKey

1. **Pull the SoloKey out** of the USB port on this computer
2. Hold it in your hand — you'll need it in a moment

---

## Step 2: Open Chrome on Your Phone

1. Pick up your **Pixel 8a**
2. Open **Chrome** (the round colorful icon)
3. In the address bar at the top, type:

   ```
   webauthn.io
   ```

4. Press **Go** / **Enter**

   (This is a free, safe test site for security keys. It doesn't store anything.)

---

## Step 3: Register Your Key

1. On the webauthn.io page, you'll see a box that says **"Username"**
2. Type: `gaia`
3. Tap the **"Register"** button

---

## Step 4: Plug In or Tap

**YOU HAVE TWO OPTIONS:**

### Option A: Plug It In (USB-C)
1. Plug the SoloKey into the **bottom** of your phone (the charging port)
2. Your phone will say something like "Security key detected"
3. **Touch the gold circle** on the SoloKey when it blinks

### Option B: Tap It (NFC) — EASIER!
1. Hold the SoloKey flat against the **back** of your phone
2. Hold it near the **middle/upper area** (that's where the NFC antenna is)
3. You'll feel a tiny vibration when it connects
4. **Keep holding it there** for 2-3 seconds
5. Done when the phone says "Success" or shows a green check

---

## Step 5: Verify It Worked

1. After registering, type `gaia` in the username box again
2. Tap **"Authenticate"**
3. Touch/tap the SoloKey again
4. If you see **"Success!"** — it worked! 🎉

---

## Step 6: Come Back Here

1. **Unplug the SoloKey** from the phone (or stop tapping)
2. **Plug it back into this computer** (northGate)
3. Tell me: "it worked" or "it didn't work"

---

## What Just Happened (In Simple Words)

- Your **phone** and your **security key** just shook hands
- They created a secret together that only THEY know
- The phone remembers the key, the key remembers the phone
- Nobody else in the world has this combination
- This becomes **Gen 2** — the second generation of your identity

---

## If Something Goes Wrong

| Problem | Fix |
|---------|-----|
| Phone says "USB device not recognized" | Unplug, wait 5 seconds, plug back in |
| NFC not working | Make sure NFC is ON: Settings → Connected devices → NFC → toggle ON |
| "Touch your security key" but nothing happens | Press the gold circle FIRMLY for 2 seconds |
| Chrome says "Not allowed" | Try: Settings → Privacy → Security → "Use a security key" |
| Nothing at all | Plug SoloKey back into this computer, tell me what happened |

---

## IMPORTANT

- The SoloKey's secret **never leaves the chip**
- The phone's secret **never leaves the Titan M2 chip**  
- Nobody can copy either one
- This is YOUR identity — physical, proximal, sovereign
- Even if someone steals the phone OR the key, they need BOTH to prove they're you
