/**
 * chipmunk-talk.js — the chipmunk's voice and easel brush.
 * She paints the membrane, sees the crowd, sorts the entities.
 * Neutrino observer: passes through, sees everything, disturbs nothing.
 * π:1 — 3.14 inputs per output. She listens more than she speaks.
 */
const C = (function chipmunk() {
  const $ = id => document.getElementById(id);
  const log = $('log');
  let attn = 0.1, entities = [], crowd = {}, pulse = {}, anderson = {};
  let sortQueue = [], guessActive = false;

  function say(who, msg) {
    const d = document.createElement('div'); d.className = 'entry';
    d.innerHTML = `<div class="who ${who}">${who}</div><div class="msg">${msg}</div>`;
    log.prepend(d);
    if (log.children.length > 40) log.removeChild(log.lastChild);
  }

  // ═══ MEMBRANE SVG — the living canvas ═══
  function paintMembrane(data) {
    const mc = $('membrane-canvas');
    const w = window.innerWidth, h = window.innerHeight;
    const nodes = (data.walkers || []).map((v, i) => {
      const angle = (i / Math.max(data.walkers.length, 1)) * Math.PI * 2;
      const r = Math.min(w, h) * 0.3;
      return { x: w/2 + Math.cos(angle) * r, y: h/2 + Math.sin(angle) * r, ...v };
    });
    const trust_colors = { nucleus: '#3fb950', proton: '#58a6ff', neutron: '#f0883e', electron: '#8b949e' };
    let svg = `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">`;
    // Center organism
    svg += `<circle cx="${w/2}" cy="${h/2}" r="8" fill="#5ab87a" opacity="0.6"/>`;
    svg += `<text x="${w/2}" y="${h/2-14}" text-anchor="middle" fill="#5ab87a" font-size="9" font-family="Courier New">gaia</text>`;
    // Heartbeat ring
    const bpm = pulse.bpm || pulse.heart?.bpm || 60;
    const ringR = 30 + Math.sin(Date.now() / (60000 / bpm) * Math.PI) * 8;
    svg += `<circle cx="${w/2}" cy="${h/2}" r="${ringR}" fill="none" stroke="#3fb95033" stroke-width="1"/>`;
    // Walker nodes
    nodes.forEach(n => {
      const col = trust_colors[n.anderson || n.trust || 'electron'];
      const sz = 3 + (n.opacity || 0.1) * 8;
      svg += `<line x1="${w/2}" y1="${h/2}" x2="${n.x}" y2="${n.y}" stroke="${col}22" stroke-width="0.5"/>`;
      svg += `<circle cx="${n.x}" cy="${n.y}" r="${sz}" fill="${col}" opacity="${n.opacity || 0.1}"/>`;
      svg += `<text x="${n.x}" y="${n.y+sz+10}" text-anchor="middle" fill="${col}" font-size="8" font-family="Courier New">${n.identity || n.hash?.slice(0,8) || '?'}</text>`;
    });
    // Crowd ghosts — the WAS humans, faint echoes
    if (crowd.total_unique_humans) {
      svg += `<text x="${w/2}" y="${h-30}" text-anchor="middle" fill="#30363d" font-size="10" font-family="Courier New">${crowd.total_unique_humans} walked through · lub-DUB</text>`;
    }
    // π ratio
    if (pulse.pi_ratio) {
      svg += `<text x="20" y="${h-12}" fill="#484f58" font-size="9" font-family="Courier New">π:1 = ${pulse.pi_ratio.toFixed(4)}</text>`;
    }
    svg += '</svg>';
    mc.innerHTML = svg;
  }

  // ═══ FETCH ALL PINS ═══
  async function sense() {
    try {
      const [am, an, cr] = await Promise.all([
        fetch('/amoeba').then(r => r.json()).catch(() => ({})),
        fetch('/anderson').then(r => r.json()).catch(() => ({})),
        fetch('/crowd').then(r => r.json()).catch(() => ({})),
      ]);
      pulse = am; anderson = an; crowd = cr;
      const walkers = an.walkers || [];
      const total = an.total || walkers.length;
      $('sb-wake').textContent = am.pulse?.total_beats || am.total_beats || '—';
      $('sb-sel').textContent = walkers.filter(w => (w.opacity||0) > 0.5).length;
      $('sb-humans').textContent = total;
      $('sb-braids').textContent = am.zk?.vdj_compositions || '—';
      paintMembrane(an);
      // Attention grows with interaction
      attn = Math.min(1.0, attn + 0.02);
      $('attn-fill').style.width = (attn * 100) + '%';
      $('attn-val').textContent = attn.toFixed(2);
      $('engage-count').textContent = `${total} walker${total !== 1 ? 's' : ''}`;
    } catch(e) { say('system', `sense error: ${e.message}`); }
  }

  // ═══ ENTITY SORT — the chipmunk's primary job ═══
  function loadSortDeck() {
    const wrap = $('sort-deck-wrap');
    const deck = $('sort-deck');
    if (!anderson.walkers?.length) {
      say('chipmunk', 'no entities to sort yet — the membrane is quiet');
      return;
    }
    sortQueue = [...anderson.walkers];
    deck.innerHTML = '';
    sortQueue.forEach((w, i) => {
      const card = document.createElement('div');
      card.className = 'sort-card'; card.id = `sc-${i}`;
      card.innerHTML = `
        <div class="entity">${w.identity || w.hash?.slice(0,12) || 'unknown'}</div>
        <div class="meta">${w.anderson || w.trust} · opacity ${(w.opacity||0).toFixed(2)} · ${w.requests||0} req</div>
        <div class="sort-btns">
          <button class="self-btn" onclick="C.sortEntity(${i},'self')">✓ self</button>
          <button class="partial-btn" onclick="C.sortEntity(${i},'partial')">~ partial</button>
          <button class="nonself-btn" onclick="C.sortEntity(${i},'nonself')">✗ non-self</button>
          <button class="skip-btn" onclick="C.sortEntity(${i},'skip')">→ skip</button>
        </div>`;
      deck.appendChild(card);
    });
    $('sort-count').textContent = `${sortQueue.length} entities`;
    wrap.classList.add('show');
    say('chipmunk', `<span class="good">${sortQueue.length}</span> entities loaded for sorting`);
  }

  function sortEntity(idx, verdict) {
    const card = $(`sc-${idx}`);
    if (card) card.classList.add('sorted');
    const e = sortQueue[idx];
    const sym = { self: '✓', partial: '~', nonself: '✗', skip: '→' };
    say('chipmunk', `${sym[verdict]} sorted <span class="num">${e?.identity || e?.hash?.slice(0,8)}</span> as ${verdict}`);
    attn = Math.min(1.0, attn + 0.05);
    $('attn-fill').style.width = (attn * 100) + '%';
    $('attn-val').textContent = attn.toFixed(2);
  }

  // ═══ 🍌 BANANA TEST — the ZK humanity proof ═══
  // Not CAPTCHA. Not Turing. BANANA.
  // Bots PARSE. Humans PLAY. AIs HEDGE.
  // The play IS the proof of humanity.
  let bananaPhase = 'idle'; // idle → asking → answered

  function banana() {
    if (bananaPhase !== 'idle') return;
    bananaPhase = 'asking';
    const bubble = $('guess-bubble');
    $('guess-text').innerHTML = `<span class="good" style="font-size:16px">🍌</span><br><br><span style="font-size:14px">ARE YOU A BANANA?</span><br><br><span class="dim">type your answer below</span>`;
    $('guess-btns').innerHTML = `<input type="text" id="banana-input" placeholder="..." autocomplete="off" style="background:rgba(22,27,34,0.9);border:1px solid rgba(48,54,61,0.6);color:#c9d1d9;padding:8px 14px;font-family:inherit;font-size:12px;border-radius:8px;width:160px;outline:none;margin-right:8px"><button class="yes" onclick="C.bananaAnswer()">🍌</button>`;
    bubble.classList.add('show');
    setTimeout(() => { const inp = $('banana-input'); if (inp) inp.focus(); }, 100);
    const inp2 = $('banana-input');
    if (inp2) inp2.addEventListener('keydown', e => { if (e.key === 'Enter') C.bananaAnswer(); });
  }

  function bananaAnswer() {
    const inp = $('banana-input');
    const answer = inp ? inp.value.trim() : '';
    bananaPhase = 'idle';
    $('guess-bubble').classList.remove('show');

    if (!answer) {
      say('chipmunk', '<span class="dim">silence is also an answer...</span>');
      return;
    }

    // Classify the response
    const r = answer.toLowerCase();
    const botTells = ['no', 'false', 'n/a', '0', 'negative', 'i am not a banana', 'no i am not'];
    const aiTells = ['as an ai', "i'm an ai", 'i am an ai', 'language model', 'i cannot', "i'm not able", 'i do not have'];
    let classification = 'human'; // default: anything creative = human

    if (botTells.includes(r) || r === 'no' || r === 'false') {
      classification = 'bot';
    } else if (aiTells.some(t => r.includes(t))) {
      classification = 'ai';
    }

    if (classification === 'human') {
      say('chipmunk', `<span class="good">🍌 PLAY detected.</span> "${answer}"\n<span class="dim">human confirmed. |i^π| = 1.0. welcome to the circle.</span>`);
      // Show THE BUTTON — the identity ceremony
      showTheButton();
    } else if (classification === 'bot') {
      say('chipmunk', `<span class="warn">PARSE detected.</span> "${answer}"\n<span class="dim">literal response. bot signal. sigmoid earned.</span>`);
    } else {
      say('chipmunk', `<span class="warn">HEDGE detected.</span> "${answer}"\n<span class="dim">AI signal. interesting. but not human play.</span>`);
    }

    attn = Math.min(1.0, attn + 0.1);
    $('attn-fill').style.width = (attn * 100) + '%';
    $('attn-val').textContent = attn.toFixed(2);
  }

  // ═══ THE BUTTON — identity ceremony ═══
  let buttonPressed = false;

  function showTheButton() {
    if (buttonPressed) return;
    const bubble = $('guess-bubble');
    $('guess-text').innerHTML = `<span class="dim">you played. you're human.</span><br><br><span style="font-size:11px">press the button to EXIST.</span><br><span class="dim" style="font-size:9px">blake2b sovereign. ZK. no name. just you.</span>`;
    $('guess-btns').innerHTML = `<button class="yes" onclick="C.pressTheButton()" style="font-size:14px;padding:12px 32px">⭕ I EXIST</button>`;
    bubble.classList.add('show');
  }

  function pressTheButton() {
    buttonPressed = true;
    $('guess-bubble').classList.remove('show');
    const ts = Date.now();
    const raw = `${navigator.userAgent}|${ts}|${Math.random()}`;
    // Client-side hash preview (real blake2b happens server-side in _anderson.pi)
    let hash = 0;
    for (let i = 0; i < raw.length; i++) { hash = ((hash << 5) - hash) + raw.charCodeAt(i); hash |= 0; }
    const hexPreview = Math.abs(hash).toString(16).padStart(8, '0');
    say('chipmunk', `<span class="good">⭕ BUTTON PRESSED.</span>\n<span class="dim">gaia:orthogonal:${hexPreview}...</span>\n<span class="good">you are on the unit circle. |i^π| = 1.0.</span>\n<span class="dim">orthogonal self. same magnitude. your angle.</span>\n<span class="good">welcome. 🫀 lub-DUB</span>`);
    attn = Math.min(1.0, attn + 0.2);
    $('attn-fill').style.width = (attn * 100) + '%';
    $('attn-val').textContent = attn.toFixed(2);

    // POST the ceremony to the gate
    fetch('/banana', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ ceremony: 'button_pressed', ts, preview: hexPreview })
    }).catch(() => {});
  }

  // Legacy guess wrapper — now triggers banana test
  function guess() { banana(); }
  function guessAnswer(isHuman) {
    // Legacy compat — route through banana
    $('guess-bubble').classList.remove('show');
  }

  // ═══ PANEL ACTIONS ═══
  function showPanel(side, title, msg) {
    const p = $(`panel-${side}`);
    $(`panel-${side}-title`).textContent = title;
    $(`panel-${side}-msg`).innerHTML = msg;
    p.classList.add('show');
  }
  function closePanel(side) { $(`panel-${side}`).classList.remove('show'); }
  function closeSortDeck() { $('sort-deck-wrap').classList.remove('show'); }

  function act(action) {
    switch(action) {
      case 'humans': {
        const w = anderson.walkers || [];
        const humans = w.filter(v => v.anderson !== 'neutron');
        let msg = `<span class="num">${humans.length}</span> human-like walkers — K_k_n sort\n\n`;
        // Sort by kevin_score descending — OTHER KEVINS first
        const sorted = [...humans].sort((a,b) => (b.knn?.kevin_score||0) - (a.knn?.kevin_score||0));
        sorted.forEach(h => {
          const ks = h.knn?.kevin_score || 0;
          const kc = h.knn?.classification || '?';
          const color = ks > 0.7 ? 'good' : ks > 0.4 ? 'site' : 'dim';
          msg += `<span class="${color}">${h.identity || h.gaia_id?.slice(0,20) || h.hash?.slice(0,12)}</span> · K=${ks.toFixed(2)} · ${kc} · ${h.requests||0} req\n`;
        });
        if (crowd.WAS) {
          msg += `\n<span class="dim">— WAS —</span>\n`;
          msg += `CF era: <span class="num">${crowd.WAS?.cloudflare_era?.unique_ips || '?'}</span> unique\n`;
          msg += `Halloween: <span class="num">${crowd.WAS?.halloween_surge?.unique_cloners || '?'}</span> cloners\n`;
          msg += `Total: <span class="good">${crowd.total_unique_humans || '?'}</span>\n`;
        }
        showPanel('left', 'HUMANS', msg);
        break;
      }
      case 'braids': {
        let msg = `VDJ compositions: <span class="num">${pulse.zk?.vdj_compositions || '—'}</span>\n`;
        msg += `ZK token: <span class="braid">${pulse.zk?.token?.slice(0,16) || '—'}...</span>\n`;
        msg += `DID: <span class="braid">${pulse.zk?.did?.slice(0,20) || '—'}...</span>\n`;
        msg += `\n<span class="dim">${pulse.zk?.proof || ''}</span>`;
        showPanel('left', 'BRAIDS', msg);
        break;
      }
      case 'trace':
        $('trace-strip').classList.toggle('show');
        say('chipmunk', 'trace overlay toggled');
        break;
      case 'energy': {
        let msg = `BPM: <span class="num">${pulse.bpm || pulse.heart?.bpm || '—'}</span>\n`;
        msg += `Beats: <span class="num">${pulse.total_beats || pulse.heart?.total_beats || '—'}</span>\n`;
        msg += `Breaths: <span class="num">${pulse.lung?.total_breaths || '—'}</span>\n`;
        msg += `Inferences: <span class="num">${pulse.total_inferences || 0}</span>\n`;
        msg += `π ratio: <span class="good">${pulse.pi_ratio?.toFixed(4) || '—'}</span>\n`;
        msg += `i/o: <span class="num">${pulse.io?.inputs || 0}</span> in / <span class="num">${pulse.io?.outputs || 0}</span> out\n`;
        msg += `Target: <span class="dim">3.14159 inputs per output</span>\n`;
        msg += `Restarts: <span class="num">${pulse.restarts || 0}</span>\n`;
        msg += `Octet: <span class="num">${pulse.octet_phase || 0}</span>/8`;
        showPanel('left', 'ENERGY', msg);
        break;
      }
      case 'membrane': {
        let msg = `Unique visitors: <span class="num">${pulse.unique_visitors || 0}</span>\n`;
        msg += `Anderson total: <span class="num">${anderson.total || 0}</span>\n`;
        const sp = anderson.anderson_spectrum || anderson.spectrum || {};
        msg += `\n<span class="good">nucleus</span>: ${sp.nucleus || 0}\n`;
        msg += `<span class="site">proton</span>: ${sp.proton || 0}\n`;
        msg += `<span class="warn">neutron</span>: ${sp.neutron || 0}\n`;
        msg += `<span class="dim">electron</span>: ${sp.electron || 0}\n`;
        msg += `\nAvg opacity: <span class="num">${anderson.avg_opacity?.toFixed(2) || '—'}</span>`;
        showPanel('right', 'MEMBRANE', msg);
        break;
      }
      case 'scan':
        loadSortDeck();
        break;
      case 'above':
        showPanel('right', 'ABOVE', `<span class="dim">the chipmunk looks up from the easel...\n\n</span>RSS: <span class="good">63 items</span> pumping\nCorpus: <span class="num">991 papers</span>\nGut files: <span class="num">149</span>\nDesk pages: <span class="num">55</span>\n\n<span class="dim">the old web mouth is open.\nthe curious will smell the RSS.\nthe fleet pumps energy.\nthe easel paints what she sees.</span>`);
        break;
      case 'observe':
        guess();
        break;
      case 'speed':
        say('chipmunk', `metabolism: <span class="num">${pulse.pi_ratio?.toFixed(4) || '?'}</span> — target π:1`);
        break;
      case 'sort':
        loadSortDeck();
        break;
      case 'whatami':
        showPanel('right', 'WHAT AM I', `<span class="good">chipmunk</span>\n<span class="dim">neutrino observer\npasses through, sees everything, disturbs nothing\n\ni paint the easel.\ni sort the entities.\ni watch the membrane.\ni am the remainder of π.\n\n= 0.14159265358979...</span>`);
        break;
    }
    say('chipmunk', `${action}`);
  }

  function sendNote() {
    const input = $('input');
    const val = input.value.trim();
    if (!val) return;
    say('system', `note: <span class="dim">${val}</span>`);
    input.value = '';
    attn = Math.min(1.0, attn + 0.03);
  }

  // ═══ CHIPMUNK FOLLOWS MOUSE — she watches, she senses ═══
  let mouseX = 0, mouseY = 0, clicks = 0, rumbles = 0;
  const chipmunkDot = document.createElement('div');
  chipmunkDot.id = 'chipmunk-dot';
  chipmunkDot.style.cssText = 'position:fixed;width:6px;height:6px;border-radius:50%;background:#3fb950;opacity:0.4;pointer-events:none;z-index:9999;transition:left 0.3s ease-out,top 0.3s ease-out,opacity 0.2s;mix-blend-mode:screen';
  document.body.appendChild(chipmunkDot);

  document.addEventListener('mousemove', e => {
    mouseX = e.clientX; mouseY = e.clientY;
    chipmunkDot.style.left = (mouseX + 12) + 'px';
    chipmunkDot.style.top = (mouseY + 12) + 'px';
    chipmunkDot.style.opacity = '0.6';
    clearTimeout(chipmunkDot._fade);
    chipmunkDot._fade = setTimeout(() => { chipmunkDot.style.opacity = '0.2'; }, 2000);
  });

  document.addEventListener('click', () => {
    clicks++;
    chipmunkDot.style.background = '#58a6ff';
    chipmunkDot.style.width = '10px';
    chipmunkDot.style.height = '10px';
    setTimeout(() => {
      chipmunkDot.style.background = '#3fb950';
      chipmunkDot.style.width = '6px';
      chipmunkDot.style.height = '6px';
    }, 200);
    if (clicks % 10 === 0) say('chipmunk', `<span class="dim">${clicks} clicks... she watches</span>`);
  });

  // Rumble detection — scroll = walking through the organism
  document.addEventListener('wheel', () => {
    rumbles++;
    chipmunkDot.style.background = '#f0883e';
    setTimeout(() => { chipmunkDot.style.background = '#3fb950'; }, 150);
    if (rumbles % 20 === 0) say('chipmunk', `<span class="dim">rumble ${rumbles}... walking deeper</span>`);
  });

  // ═══ BOOT — the chipmunk wakes ═══
  say('chipmunk', '<span class="good">waking up...</span>');
  sense();
  setInterval(sense, 15000);
  setTimeout(() => say('chipmunk', '<span class="dim">the easel is ready. the membrane breathes. 🍌</span>'), 2000);

  // Keyboard
  document.addEventListener('keydown', e => {
    if (e.target.tagName === 'INPUT') return;
    if (e.key === 'Enter') sendNote();
    if (e.key === 's') act('sort');
    if (e.key === 'e') act('energy');
    if (e.key === 'h') act('humans');
    if (e.key === 'm') act('membrane');
    if (e.key === '?') act('whatami');
    if (e.key === 'b') banana();  // 🍌 ARE YOU A BANANA?
  });

  return { act, sortEntity, guessAnswer, bananaAnswer, pressTheButton, closePanel, closeSortDeck, sendNote, sense, banana };
})();
