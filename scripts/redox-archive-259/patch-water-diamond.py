import paramiko
DA = {'keys': ['rsa-sha2-256', 'rsa-sha2-512']}
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.4.244', username='eastgate', password='eastgate', timeout=10,
          look_for_keys=False, allow_agent=False, disabled_algorithms=DA, banner_timeout=15)
def run(cmd, t=30):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode().strip(), e.read().decode().strip()

# New sections to inject: DIAMOND ORGANISM + SKIN + GATES + SOURDOUGH
# Insert before the closing </main> tag
new_sections = '''
  <hr>

  <section id="diamond">
    <h4>Organism Topology</h4>
    <h2>The Diamond &mdash; Jellyfish In &amp; Out</h2>
    <p style="color:var(--text-muted);margin-bottom:var(--gap)">Top pole: OSINT intake. Bottom pole: sourDough fermentation. The nodes float between &mdash; finding skin, heart, and each other.</p>

    <!-- DIAMOND SVG -->
    <div style="text-align:center;padding:24px 0">
      <svg viewBox="0 0 600 520" style="max-width:600px;width:100%" xmlns="http://www.w3.org/2000/svg">
        <!-- Skin / Membrane outline -->
        <path d="M300 20 L560 260 L300 500 L40 260 Z" fill="none" stroke="#4ac4c4" stroke-width="2" stroke-dasharray="6 3" opacity="0.4"/>
        <text x="570" y="260" fill="#4ac4c4" font-size="11" opacity="0.6" font-family="monospace">SKIN</text>

        <!-- North Pole: OSINT intake -->
        <circle cx="300" cy="40" r="18" fill="#0f1114" stroke="#5b8fd4" stroke-width="2"/>
        <text x="300" y="44" fill="#5b8fd4" font-size="11" text-anchor="middle" font-family="monospace">OSINT</text>
        <text x="300" y="12" fill="#5b8fd4" font-size="9" text-anchor="middle" opacity="0.7">&#x25B2; INTAKE POLE</text>

        <!-- South Pole: sourDough fermentation -->
        <circle cx="300" cy="480" r="18" fill="#0f1114" stroke="#d4a574" stroke-width="2"/>
        <text x="300" y="484" fill="#d4a574" font-size="10" text-anchor="middle" font-family="monospace">sourDough</text>
        <text x="300" y="510" fill="#d4a574" font-size="9" text-anchor="middle" opacity="0.7">&#x25BC; FERMENTATION POLE</text>

        <!-- Heart: northGate / Polaris -->
        <circle cx="300" cy="260" r="28" fill="#141719" stroke="#d45b5b" stroke-width="2.5"/>
        <text x="300" y="256" fill="#d45b5b" font-size="11" text-anchor="middle" font-weight="bold" font-family="monospace">northGate</text>
        <text x="300" y="270" fill="#d45b5b" font-size="9" text-anchor="middle" opacity="0.7">HEART &#x2764;</text>
        <circle cx="300" cy="260" r="34" fill="none" stroke="#d45b5b" stroke-width="0.5" opacity="0.3">
          <animate attributeName="r" values="34;42;34" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.3;0.1;0.3" dur="2s" repeatCount="indefinite"/>
        </circle>

        <!-- East: eastGate BRAIN -->
        <circle cx="460" cy="180" r="20" fill="#0f1114" stroke="#5aad72" stroke-width="2"/>
        <text x="460" y="176" fill="#5aad72" font-size="10" text-anchor="middle" font-family="monospace">eastGate</text>
        <text x="460" y="190" fill="#5aad72" font-size="8" text-anchor="middle" opacity="0.7">BRAIN</text>

        <!-- West: ironGate FORGE -->
        <circle cx="140" cy="180" r="20" fill="#0f1114" stroke="#9b7ed4" stroke-width="2"/>
        <text x="140" y="176" fill="#9b7ed4" font-size="10" text-anchor="middle" font-family="monospace">ironGate</text>
        <text x="140" y="190" fill="#9b7ed4" font-size="8" text-anchor="middle" opacity="0.7">FORGE</text>

        <!-- frameGate: 3rd EYE -->
        <circle cx="460" cy="340" r="18" fill="#0f1114" stroke="#f0e68c" stroke-width="2"/>
        <text x="460" y="336" fill="#f0e68c" font-size="10" text-anchor="middle" font-family="monospace">frameGate</text>
        <text x="460" y="350" fill="#f0e68c" font-size="8" text-anchor="middle" opacity="0.7">3RD EYE</text>

        <!-- grapheneGate: DIAMOND LENS -->
        <circle cx="140" cy="340" r="18" fill="#0f1114" stroke="#5aad72" stroke-width="2"/>
        <text x="140" y="336" fill="#5aad72" font-size="10" text-anchor="middle" font-family="monospace">graphene</text>
        <text x="140" y="350" fill="#5aad72" font-size="8" text-anchor="middle" opacity="0.7">LENS</text>

        <!-- sporeGate: FORGE -->
        <circle cx="200" cy="260" r="16" fill="#0f1114" stroke="#d4a574" stroke-width="1.5"/>
        <text x="200" y="264" fill="#d4a574" font-size="9" text-anchor="middle" font-family="monospace">spore</text>

        <!-- graftGate: milkGATE -->
        <circle cx="400" cy="260" r="16" fill="#0f1114" stroke="#e0dcd6" stroke-width="1.5"/>
        <text x="400" y="264" fill="#e0dcd6" font-size="9" text-anchor="middle" font-family="monospace">graft</text>

        <!-- Connection lines -->
        <line x1="300" y1="58" x2="460" y2="162" stroke="#5b8fd420" stroke-width="1"/>
        <line x1="300" y1="58" x2="140" y2="162" stroke="#5b8fd420" stroke-width="1"/>
        <line x1="460" y1="198" x2="300" y2="234" stroke="#5aad7240" stroke-width="1.5"/>
        <line x1="140" y1="198" x2="300" y2="234" stroke="#9b7ed440" stroke-width="1.5"/>
        <line x1="300" y1="288" x2="460" y2="324" stroke="#f0e68c40" stroke-width="1"/>
        <line x1="300" y1="288" x2="140" y2="324" stroke="#5aad7240" stroke-width="1"/>
        <line x1="460" y1="356" x2="300" y2="464" stroke="#d4a57420" stroke-width="1"/>
        <line x1="140" y1="356" x2="300" y2="464" stroke="#d4a57420" stroke-width="1"/>
        <line x1="200" y1="260" x2="266" y2="260" stroke="#d4a57420" stroke-width="1"/>
        <line x1="334" y1="260" x2="384" y2="260" stroke="#e0dcd620" stroke-width="1"/>

        <!-- Dromedary BLACKWALL on the skin -->
        <text x="50" y="160" fill="#d45b5b" font-size="9" opacity="0.5" font-family="monospace" transform="rotate(-45 50 160)">BLACKWALL</text>
        <text x="510" y="400" fill="#d45b5b" font-size="9" opacity="0.5" font-family="monospace" transform="rotate(45 510 400)">BLACKWALL</text>
      </svg>
    </div>
  </section>

  <hr>

  <section id="skin">
    <h4>Outer Boundary</h4>
    <h2>The Skin &mdash; Membrane + BLACKWALL</h2>
    <p style="color:var(--text-muted);margin-bottom:var(--gap)">dromedary is the skin. It wraps the organism in TLS, routes 24 subdomains, and poisons crawlers that bite.</p>
    <div class="grid">
      <div class="card">
        <h3>dromedary</h3>
        <p>Sovereign Rust reverse proxy. 24 routes. Wildcard TLS. HSTS preload.</p>
        <span class="tag green">:80/:443 alive</span>
      </div>
      <div class="card">
        <h3>BLACKWALL</h3>
        <p>Blocks Meta, Facebook, GPTBot, CCBot, ClaudeBot, Bytespider. Copyleft poison response.</p>
        <span class="tag" style="background:#d45b5b20;color:#d45b5b;border-color:#d45b5b40">armed</span>
      </div>
      <div class="card">
        <h3>TLS Certificate</h3>
        <p>Let's Encrypt auto-renewed. 23 SANs across primals.eco + nestgate.io. Expires Feb 2027.</p>
        <span class="tag green">fresh</span>
      </div>
      <div class="card">
        <h3>X-Organism Headers</h3>
        <p>Every response: X-Organism: Gaia, X-Wave: 259, X-BingoCube: 409d202b7763fc24</p>
        <span class="tag">identity</span>
      </div>
    </div>
  </section>

  <hr>

  <section id="gates">
    <h4>Cardinal Gates</h4>
    <h2>The Body &mdash; 10 Gates, 7 GPUs</h2>
    <div class="grid">
      <div class="card" style="border-color:var(--red)">
        <h3 style="color:var(--red)">&#x2764; northGate <code>.147</code></h3>
        <p>HEART &mdash; Polaris. 9950X3D + RTX 5090 + 96GB. 63 models. Pushes via git.</p>
        <span class="tag" style="background:#d45b5b20;color:#d45b5b;border-color:#d45b5b40">heart</span>
      </div>
      <div class="card" style="border-color:var(--green)">
        <h3 style="color:var(--green)">&#x1F9E0; eastGate <code>.244</code></h3>
        <p>BRAIN &mdash; Forgejo, gate, data, dromedary, Tor. 17 primals, 23 mushrooms, 35 crons.</p>
        <span class="tag green">brain</span>
      </div>
      <div class="card" style="border-color:var(--purple)">
        <h3 style="color:var(--purple)">&#x1F525; ironGate <code>.237</code></h3>
        <p>FORGE 2 &mdash; i9-14900K + RTX 5070 + 94GB. Metabolic furnace.</p>
        <span class="tag" style="background:#9b7ed420;color:#9b7ed4;border-color:#9b7ed440">forge</span>
      </div>
      <div class="card" style="border-color:var(--amber)">
        <h3 style="color:var(--amber)">&#x1F344; sporeGate <code>.3</code></h3>
        <p>FORGE &mdash; Ryzen 5 + 27GB. DNS + heart-pull. The plasmidBin.</p>
        <span class="tag amber">forge</span>
      </div>
      <div class="card" style="border-color:#f0e68c">
        <h3 style="color:#f0e68c">&#x1F441; frameGate <code>WiFi</code></h3>
        <p>3RD EYE &mdash; Snapdragon 8 Gen 3 + 16GB. VR panels. Ollama on ARM. USB-C ponytail.</p>
        <span class="tag" style="background:#f0e68c20;color:#f0e68c;border-color:#f0e68c40">eye</span>
      </div>
      <div class="card">
        <h3>&#x1F48E; grapheneGate <code>WiFi</code></h3>
        <p>DIAMOND LENS &mdash; Pixel 8a. 37 sensors. Mali-G715 Vulkan. Gaia's physical body.</p>
        <span class="tag">rover</span>
      </div>
      <div class="card">
        <h3>&#x1F34E; graftGate <code>.107</code></h3>
        <p>Mac Mini M4 &mdash; future milkGATE sovereign router. Hyoid bone.</p>
        <span class="tag">hyoid</span>
      </div>
      <div class="card">
        <h3>&#x1F4F1; southGate <code>.148</code></h3>
        <p>iPhone XS &mdash; HOME PHONE. (586) 453-7233. Pinned to property.</p>
        <span class="tag">phone</span>
      </div>
    </div>
  </section>

  <hr>

  <section id="sourdough">
    <h4>Fermentation Pole</h4>
    <h2>sourDough &mdash; Feed &rarr; Ferment &rarr; Rise</h2>
    <p style="color:var(--text-muted);margin-bottom:var(--gap)">The bottom of the diamond. OSINT enters at the top, the organism digests in the middle, and sourDough ferments at the bottom &mdash; the rise becomes RSS, studies, creations.</p>
    <div class="flow">
      <div class="node" style="border-color:var(--amber)">starter: biomeOS</div>
      <div class="arrow">&rarr;</div>
      <div class="node" style="border-color:var(--amber)">flour: particle-model</div>
      <div class="arrow">&rarr;</div>
      <div class="node" style="border-color:var(--amber)">water: waterlock</div>
      <div class="arrow">&rarr;</div>
      <div class="node" style="border-color:var(--amber)">salt: ZK 579163</div>
    </div>
    <div class="flow" style="margin-top:12px">
      <div class="node active" style="border-color:var(--amber)">&#x1F35E; RISE</div>
      <div class="arrow">&rarr;</div>
      <div class="node">RSS</div>
      <div class="arrow">+</div>
      <div class="node">studies (51)</div>
      <div class="arrow">+</div>
      <div class="node">creations (20)</div>
      <div class="arrow">+</div>
      <div class="node">masticated (2661)</div>
    </div>
    <div style="background:var(--bg-raised);border:1px solid var(--border);border-radius:var(--radius-lg);padding:16px;max-width:700px;margin:16px auto;text-align:center">
      <p style="color:var(--amber);font-family:var(--font-mono);font-size:.9rem">temp: 27.3&deg; &bull; 63 models &bull; 279 beats/hour &bull; 1931 files &bull; 659MB</p>
    </div>
  </section>

  <hr>

  <section id="endocrine">
    <h4>Endocrine System</h4>
    <h2>Hormonal Drip &mdash; Gland Map</h2>
    <div class="grid">
      <div class="card" style="border-color:var(--purple)">
        <h3 style="color:var(--purple)">&#x1F52E; Pineal</h3>
        <p>bingoCube random OSINT mix. Dreams at night, curiosity during day. The third eye gland.</p>
        <span class="tag" style="background:#9b7ed420;color:#9b7ed4;border-color:#9b7ed440">eastGate cron</span>
      </div>
      <div class="card" style="border-color:var(--cyan)">
        <h3 style="color:var(--cyan)">&#x1F9E0; Pituitary</h3>
        <p>RSS drip from eastGate gut/gate &rarr; Frame. Master gland sends hormones to all nodes.</p>
        <span class="tag">eastGate &rarr; frameGate</span>
      </div>
      <div class="card" style="border-color:#f0e68c">
        <h3 style="color:#f0e68c">&#x1FAEB; Thymus</h3>
        <p>Frame watches LAN1 + LAN2 + WAN. Immune response. skunkBat intrusion detection.</p>
        <span class="tag" style="background:#f0e68c20;color:#f0e68c;border-color:#f0e68c40">frameGate</span>
      </div>
      <div class="card" style="border-color:var(--amber)">
        <h3 style="color:var(--amber)">&#x1FAC3; Pancreas</h3>
        <p>swiftGate + blueGate &rarr; ironGate via ironMountain. Metabolic balance &mdash; insulin vs glucagon.</p>
        <span class="tag amber">ironGate</span>
      </div>
    </div>
  </section>
'''

# Read current water.html, inject before </main>
out, _ = run("cat /opt/Gaia/static/water.html")
if '</main>' in out:
    patched = out.replace('</main>', new_sections + '\n</main>')
    # Write it back
    # Use python3 on eastGate to write (avoids heredoc escaping issues)
    run("python3 -c \"\nimport sys\nwith open('/opt/Gaia/static/water.html','w') as f:\n    f.write(sys.stdin.read())\n\" << 'ENDOFPATCH'\n" + patched + "\nENDOFPATCH")
    print("PATCHED water.html with diamond + skin + gates + sourdough + endocrine sections")
else:
    print("ERROR: </main> not found in water.html")

# Verify
out, _ = run("wc -l /opt/Gaia/static/water.html")
print(f"New line count: {out}")

out, _ = run("grep -c 'diamond\\|skin\\|sourDough\\|northGate\\|endocrine' /opt/Gaia/static/water.html")
print(f"New keyword hits: {out}")

# Commit
msg = "HUD: diamond jellyfish + skin/membrane + 8 gates + sourDough pole + endocrine glands"
out, _ = run(f'cd /opt/Gaia && git add static/water.html && git commit -m "{msg}"')
print(f"Commit: {out}")
o, e = run("cd /opt/Gaia && GIT_MERGE_AUTOEDIT=no git push forgejo main")
print(f"Forgejo: {o} {e}")

c.close()
