#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const BENCH = path.join(ROOT, 'bench-scale.json');

function load() {
  try {
    return JSON.parse(fs.readFileSync(BENCH, 'utf8'));
  } catch (e) {
    return { scale: 'bench', pieth: { ready: false } };
  }
}

function reply(obj) {
  process.stdout.write(JSON.stringify(obj));
}

function statements(cmd) {
  return String(cmd).split(/[;&\n]/).map((s) => s.trim()).filter(Boolean);
}

function isPilot(cmd) {
  const bench = load();
  if (bench.scale === 'pilot' && bench.pieth && bench.pieth.ready) return false;
  for (const s of statements(cmd)) {
    if (/^echo\b/i.test(s)) continue;
    if (/bench-hook\.js/.test(s)) continue;
    if (/\bBOOT-AMALGAM\b|\bbiomeOS-AMALGAM\b/i.test(s)) return true;
    if (/(^|\s)(bash|sh)\s+\S*inject-wsl\.sh/i.test(s)) return true;
    if (/\bwsl\b[\s\S]*inject-wsl\.sh/i.test(s)) return true;
    if (/pilot\s*plant/i.test(s)) return true;
    if (/deploy\s+(here\s+)?local/i.test(s)) return true;
  }
  return false;
}

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (c) => { raw += c; });
process.stdin.on('end', () => {
  let ev = {};
  try { ev = JSON.parse(raw || '{}'); } catch (e) { ev = {}; }
  const cmd = String(ev.command || (ev.tool_input && ev.tool_input.command) || '');
  if (isPilot(cmd)) {
    reply({
      permission: 'deny',
      user_message: 'BENCH SCALE. The πth generation is not ready. No local inject. No pilot.',
      agent_message: 'Hook denied inject/pilot. Stay on the bench. Compare. Eat K and N. Hold until πth.'
    });
    return;
  }
  reply({ permission: 'allow' });
});
