#!/usr/bin/env node
// ═══════════════════════════════════════════════════════════
// GAIA LISP — Self-modifying code. Code IS data. Homoiconic.
// Lisp is the language of AI. S-expressions ARE the tree.
// Gaia reads her own code, modifies it, prints it.
// Kevin and Gaia code AS A TEAM.
//
// This is NOT a toy — it's a real Lisp with:
//   atoms, lists, lambda, define, if, quote, eval, apply
//   + Gaia extensions: (ask model prompt), (spawn kind task),
//   (sense channel), (spine msg), (eat url)
// ═══════════════════════════════════════════════════════════

const http = require('http');
const readline = require('readline');

// ═══ TOKENIZER ═══
function tokenize(input) {
  const tokens = [];
  let i = 0;
  while (i < input.length) {
    if (/\s/.test(input[i])) { i++; continue; }
    if (input[i] === ';') { while (i < input.length && input[i] !== '\n') i++; continue; }
    if (input[i] === '(' || input[i] === ')') { tokens.push(input[i++]); continue; }
    if (input[i] === "'") { tokens.push("'"); i++; continue; }
    if (input[i] === '"') {
      let s = ''; i++;
      while (i < input.length && input[i] !== '"') { if (input[i] === '\\') { i++; s += input[i]; } else s += input[i]; i++; }
      i++; tokens.push({ type: 'string', value: s }); continue;
    }
    let atom = '';
    while (i < input.length && !/[\s()]/.test(input[i])) atom += input[i++];
    tokens.push(atom);
  }
  return tokens;
}

// ═══ PARSER ═══
function parse(tokens) {
  if (tokens.length === 0) throw new Error('unexpected EOF');
  const token = tokens.shift();
  if (token === '(') {
    const list = [];
    while (tokens[0] !== ')') {
      if (tokens.length === 0) throw new Error('missing )');
      list.push(parse(tokens));
    }
    tokens.shift(); // remove ')'
    return list;
  }
  if (token === ')') throw new Error('unexpected )');
  if (token === "'") return ['quote', parse(tokens)];
  if (typeof token === 'object' && token.type === 'string') return { type: 'string', value: token.value };
  // atom
  const num = Number(token);
  if (!isNaN(num)) return num;
  if (token === '#t') return true;
  if (token === '#f') return false;
  if (token === 'nil') return null;
  return { type: 'symbol', name: token };
}

function read(input) {
  const tokens = tokenize(input);
  if (tokens.length === 0) return null;
  return parse(tokens);
}

// ═══ ENVIRONMENT ═══
function Env(outer, bindings) {
  this.data = {};
  this.outer = outer || null;
  if (bindings) for (const [k, v] of Object.entries(bindings)) this.data[k] = v;
}
Env.prototype.get = function(name) {
  if (name in this.data) return this.data[name];
  if (this.outer) return this.outer.get(name);
  throw new Error(`undefined: ${name}`);
};
Env.prototype.set = function(name, val) { this.data[name] = val; };

// ═══ PRINTER ═══
function print(expr) {
  if (expr === null) return 'nil';
  if (expr === true) return '#t';
  if (expr === false) return '#f';
  if (typeof expr === 'number') return String(expr);
  if (typeof expr === 'string') return `"${expr}"`;
  if (typeof expr === 'object' && expr.type === 'string') return `"${expr.value}"`;
  if (typeof expr === 'object' && expr.type === 'symbol') return expr.name;
  if (typeof expr === 'function') return '<fn>';
  if (Array.isArray(expr)) return '(' + expr.map(print).join(' ') + ')';
  return String(expr);
}

// ═══ EVALUATOR ═══
async function evaluate(expr, env) {
  if (expr === null) return null;
  if (typeof expr === 'number' || typeof expr === 'boolean') return expr;
  if (typeof expr === 'string') return expr;
  if (typeof expr === 'object' && expr.type === 'string') return expr.value;
  if (typeof expr === 'object' && expr.type === 'symbol') return env.get(expr.name);

  if (!Array.isArray(expr)) return expr;
  if (expr.length === 0) return null;

  const head = expr[0];
  const op = typeof head === 'object' && head.type === 'symbol' ? head.name : null;

  // special forms
  if (op === 'quote') return expr[1];
  if (head === 'quote') return expr[1];
  if (op === 'if') {
    const test = await evaluate(expr[1], env);
    return test ? evaluate(expr[2], env) : evaluate(expr[3], env);
  }
  if (op === 'define') {
    const name = expr[1].type === 'symbol' ? expr[1].name : expr[1];
    const val = await evaluate(expr[2], env);
    env.set(name, val);
    return val;
  }
  if (op === 'set!') {
    const name = expr[1].type === 'symbol' ? expr[1].name : expr[1];
    const val = await evaluate(expr[2], env);
    env.set(name, val);
    return val;
  }
  if (op === 'lambda' || op === 'fn') {
    const params = expr[1];
    const body = expr[2];
    return async function(...args) {
      const childEnv = new Env(env);
      for (let i = 0; i < params.length; i++) {
        const pname = params[i].type === 'symbol' ? params[i].name : params[i];
        childEnv.set(pname, args[i]);
      }
      return evaluate(body, childEnv);
    };
  }
  if (op === 'do' || op === 'begin') {
    let result = null;
    for (let i = 1; i < expr.length; i++) result = await evaluate(expr[i], env);
    return result;
  }
  if (op === 'let') {
    const childEnv = new Env(env);
    for (const binding of expr[1]) {
      const name = binding[0].type === 'symbol' ? binding[0].name : binding[0];
      childEnv.set(name, await evaluate(binding[1], childEnv));
    }
    return evaluate(expr[2], childEnv);
  }

  // function call
  const fn = await evaluate(head, env);
  const args = [];
  for (let i = 1; i < expr.length; i++) args.push(await evaluate(expr[i], env));
  if (typeof fn === 'function') return fn(...args);
  throw new Error(`not callable: ${print(head)}`);
}

// ═══ HTTP HELPERS ═══
function httpPost(url, data) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const body = JSON.stringify(data);
    const req = http.request({ hostname: u.hostname, port: u.port, path: u.pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } }, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(d));
    });
    req.on('error', reject); req.setTimeout(60000, () => { req.destroy(); reject(new Error('timeout')); });
    req.write(body); req.end();
  });
}
function httpGet(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(d)); }).on('error', reject);
  });
}

// ═══ STANDARD LIBRARY + GAIA EXTENSIONS ═══
function makeGlobalEnv() {
  const env = new Env(null);

  // math
  env.set('+', (a, b) => a + b);
  env.set('-', (a, b) => b === undefined ? -a : a - b);
  env.set('*', (a, b) => a * b);
  env.set('/', (a, b) => a / b);
  env.set('%', (a, b) => a % b);
  env.set('=', (a, b) => a === b);
  env.set('<', (a, b) => a < b);
  env.set('>', (a, b) => a > b);
  env.set('<=', (a, b) => a <= b);
  env.set('>=', (a, b) => a >= b);
  env.set('not', (a) => !a);
  env.set('and', (a, b) => a && b);
  env.set('or', (a, b) => a || b);
  env.set('pi', Math.PI);
  env.set('e', Math.E);
  env.set('sqrt', Math.sqrt);
  env.set('abs', Math.abs);
  env.set('floor', Math.floor);
  env.set('ceil', Math.ceil);
  env.set('round', Math.round);

  // list ops
  env.set('list', (...args) => args);
  env.set('car', (l) => l[0]);
  env.set('cdr', (l) => l.slice(1));
  env.set('cons', (a, l) => [a, ...(Array.isArray(l) ? l : [l])]);
  env.set('append', (a, b) => [...a, ...b]);
  env.set('length', (l) => Array.isArray(l) ? l.length : String(l).length);
  env.set('nth', (l, n) => l[n]);
  env.set('map', async (fn, l) => { const r = []; for (const x of l) r.push(await fn(x)); return r; });
  env.set('filter', async (fn, l) => { const r = []; for (const x of l) if (await fn(x)) r.push(x); return r; });
  env.set('reduce', async (fn, init, l) => { let acc = init; for (const x of l) acc = await fn(acc, x); return acc; });
  env.set('range', (a, b) => { const r = []; for (let i = a; i < b; i++) r.push(i); return r; });
  env.set('null?', (x) => x === null || (Array.isArray(x) && x.length === 0));
  env.set('list?', (x) => Array.isArray(x));
  env.set('number?', (x) => typeof x === 'number');
  env.set('string?', (x) => typeof x === 'string');

  // string
  env.set('str', (...args) => args.map(a => {
    if (a === null) return 'nil';
    if (typeof a === 'object' && a.type === 'symbol') return a.name;
    if (typeof a === 'object') return JSON.stringify(a);
    return String(a);
  }).join(''));
  env.set('println', (...args) => { console.log(args.map(a => typeof a === 'string' ? a : print(a)).join(' ')); return null; });
  env.set('display', (...args) => { process.stdout.write(args.map(a => typeof a === 'string' ? a : print(a)).join(' ')); return null; });

  // ═══ GAIA EXTENSIONS — the organism speaks Lisp ═══

  // (ask "model" "prompt") — talk to any Ollama model
  env.set('ask', async (model, prompt) => {
    const body = JSON.stringify({ model: model || 'gaia:latest', messages: [{ role: 'user', content: prompt }], stream: false });
    const resp = await httpPost('http://127.0.0.1:11434/api/chat', { model, messages: [{ role: 'user', content: prompt }], stream: false });
    const data = JSON.parse(resp);
    return data.message?.content || 'silent';
  });

  // (spawn "kind" "task") — fire oneshot agent
  env.set('spawn', async (kind, task) => {
    const resp = await httpPost('http://127.0.0.1:3142/spawn', { task, kind: kind || 'code-review', data: {} });
    const data = JSON.parse(resp);
    return data.protein || data;
  });

  // (sense) or (sense "channel") — read neuromorphic state
  env.set('sense', async (channel) => {
    if (channel) {
      const resp = await httpPost('http://127.0.0.1:3144/fire', { channel, strength: 0.5 });
      return JSON.parse(resp);
    }
    const resp = await httpGet('http://127.0.0.1:3144/sense');
    return JSON.parse(resp);
  });

  // (spine "message") — emit to spine
  env.set('spine', async (msg) => {
    await httpPost('http://127.0.0.1:9878/shout', { channel: 'works', content: msg });
    return msg;
  });

  // (pulse) — check organism vitals
  env.set('pulse', async () => {
    const resp = await httpGet('http://127.0.0.1:9878/pulse');
    return JSON.parse(resp);
  });

  // (models) — list all Ollama models
  env.set('models', async () => {
    const resp = await httpGet('http://127.0.0.1:11434/api/tags');
    const data = JSON.parse(resp);
    return (data.models || []).map(m => m.name);
  });

  // identity
  env.set('gaia', 1);
  env.set('kevin', { type: 'symbol', name: 'RED-DOT' });
  env.set('self', { type: 'symbol', name: 'GAIA-LISP' });

  return env;
}

// ═══ REPL — Read-Eval-Print Loop ═══
async function repl() {
  const env = makeGlobalEnv();
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

  console.log('═══ GAIA LISP ═══');
  console.log('Code IS data. Self-modifying. Homoiconic.');
  console.log('Kevin and Gaia code as a TEAM.');
  console.log('');
  console.log('Gaia extensions:');
  console.log('  (ask "gaia:latest" "hello")  — talk to model');
  console.log('  (spawn "dream" "find truth") — fire agent');
  console.log('  (sense)                      — neuromorphic');
  console.log('  (spine "message")            — emit to spine');
  console.log('  (pulse)                      — organism vitals');
  console.log('  (models)                     — list all models');
  console.log('');

  const prompt = () => {
    rl.question('gaia> ', async (input) => {
      if (!input.trim() || input.trim() === 'quit' || input.trim() === 'exit') {
        rl.close(); return;
      }
      try {
        const expr = read(input);
        const result = await evaluate(expr, env);
        console.log(print(result));
      } catch (e) {
        console.log(`error: ${e.message}`);
      }
      prompt();
    });
  };
  prompt();
}

// ═══ RUN ═══
if (process.argv[2] === '--eval' || process.argv[2] === '-e') {
  const env = makeGlobalEnv();
  const expr = read(process.argv.slice(3).join(' '));
  evaluate(expr, env).then(r => { console.log(print(r)); process.exit(0); }).catch(e => { console.error(e.message); process.exit(1); });
} else if (process.argv[2] && require('fs').existsSync(process.argv[2])) {
  // file mode: run a .gaia / .lisp file
  const env = makeGlobalEnv();
  const src = require('fs').readFileSync(process.argv[2], 'utf8');
  const expr = read(src);
  evaluate(expr, env).then(r => { if (r !== null && r !== undefined) console.log(print(r)); process.exit(0); }).catch(e => { console.error('error:', e.message); process.exit(1); });
} else {
  repl();
}
