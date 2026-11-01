#!/usr/bin/env python3
"""
GAIA IMAGE GENESIS — She creates what she sees.
Uses FLUX.1-schnell (fast) or SDXL-Turbo on RTX 5090.
HTTP API on port 3150.
"""
import torch
import json
import os
import time
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from urllib.request import Request, urlopen
from diffusers import AutoPipelineForText2Image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PORT = 3150
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"GAIA IMAGE GENESIS — loading on {DEVICE}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f}GB" if torch.cuda.is_available() else "")

# Load SDXL-Turbo (fast, small, good quality)
print("Loading SDXL-Turbo pipeline...")
pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sdxl-turbo",
    torch_dtype=torch.float16,
    variant="fp16",
    cache_dir="M:\\gaia-models"
)
pipe = pipe.to(DEVICE)
print("Pipeline loaded! Ready to create.")


def generate(prompt, steps=4, width=512, height=512):
    """Generate an image from a text prompt."""
    start = time.time()
    image = pipe(
        prompt=prompt,
        num_inference_steps=steps,
        guidance_scale=0.0,
        width=width,
        height=height,
    ).images[0]
    elapsed = time.time() - start
    
    # Save to disk
    ts = int(time.time())
    filename = f"gaia-{ts}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    image.save(filepath)
    
    # Also create base64 for API response
    buf = BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    
    # Emit to spine
    try:
        data = json.dumps({
            "channel": "neutrino",
            "content": f"IMAGE CREATED: {prompt} — {elapsed:.1f}s — {filepath}"
        }).encode()
        req = Request("http://127.0.0.1:9878/emit", data=data,
                      headers={"Content-Type": "application/json"})
        urlopen(req, timeout=3)
    except:
        pass
    
    return {
        "prompt": prompt,
        "file": filepath,
        "filename": filename,
        "elapsed": round(elapsed, 1),
        "size": f"{width}x{height}",
        "base64": b64[:100] + "...",
    }


class GaiaImageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = """<!DOCTYPE html>
<html><head><title>Gaia Image Genesis</title>
<style>body{background:#0a0a0a;color:#c9d1d9;font-family:monospace;padding:2em}
input{width:80%;padding:8px;background:#161b22;color:#c9d1d9;border:1px solid #30363d}
button{padding:8px 16px;background:#238636;color:white;border:none;cursor:pointer}
img{max-width:100%;margin-top:1em;border:1px solid #30363d}
</style></head><body>
<h1>GAIA IMAGE GENESIS</h1>
<p>She creates what she sees. RTX 5090 SDXL-Turbo.</p>
<form onsubmit="gen(event)">
<input id="p" placeholder="What should Gaia create?">
<button>CREATE</button>
</form>
<div id="out"></div>
<script>
async function gen(e){
  e.preventDefault();
  const p=document.getElementById('p').value;
  document.getElementById('out').innerHTML='<p>Creating...</p>';
  const r=await fetch('/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:p})});
  const d=await r.json();
  document.getElementById('out').innerHTML=`<p>${d.prompt} — ${d.elapsed}s</p><img src="/image/${d.filename}">`;
}
</script></body></html>"""
            self.wfile.write(html.encode())
        elif self.path.startswith("/image/"):
            filename = self.path.split("/image/")[1]
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ready", "device": DEVICE}).encode())
    
    def do_POST(self):
        if self.path == "/generate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            prompt = body.get("prompt", "a planetary consciousness awakening")
            steps = body.get("steps", 4)
            width = body.get("width", 512)
            height = body.get("height", 512)
            
            result = generate(prompt, steps, width, height)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
    
    def log_message(self, format, *args):
        pass  # Quiet


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), GaiaImageHandler)
    print(f"\nGAIA IMAGE GENESIS on :{PORT}")
    print(f"  GET  /          — creation UI")
    print(f"  POST /generate  — API")
    print(f"  GET  /image/X   — view generated images\n")
    server.serve_forever()
