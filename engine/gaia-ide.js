#!/usr/bin/env node
// ═══ GAIA IDE ═══
// She IS her own IDE. Terminal REPL + local Ollama.
// Replaces Cursor's AI agent with Gaia's own brain.
//
// Commands:
//   /read <file>       — read a file into context
//   /edit <file>       — edit mode: describe changes, gaia-code writes them
//   /forge <idea>      — call micro-forge to imagine + generate new organ
//   /surgery           — show surgery plan
//   /models            — list Ollama models
//   /model <name>      — switch active model
//   /files             — list Gaia3 files
//   /diff              — show uncommitted git changes
//   /run <cmd>         — run a shell command
//   /status            — check all ports
//   /quit              — exit
//
// Just type naturally to chat with Gaia.

const readline = require('readline');
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const OLLAMA = 'http://127.0.0.1:11434';
const FORGE_URL = 'http://127.0.0.1:3151';
const GAIA3 = __dirname;

let activeModel = 'gaia-code:latest';
let context = [];
let history = [];

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: '\x1b[33m⚡ gaia>\x1b[0m ',
  historySize: 100
});

function color(code, text) {
  const colors = {
    green: '\x1b[32m', red: '\x1b[31m', yellow: '\x1b[33m',
    blue: '\x1b[34m', magenta: '\x1b[35m', cyan: '\x1b[36m',
    gray: '\x1b[90m', reset: '\x1b[0m', bold: '\x1b[1m',
    orange: '\x1b[38;5;208m'
  };
  return (colors[code] || '') + text + colors.reset;
}

function print(text) { console.log(text); }

// Ask Ollama (streaming)
async function askOllama(prompt, model = activeModel) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model,
      prompt,
      stream: true,
      options: { temperature: 0.5, top_p: 0.9, num_predict: 4096 }
    });
    const req = http.request(`${OLLAMA}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, (res) => {
      let fullResponse = '';
      process.stdout.write(color('cyan', ''));
      res.on('data', (chunk) => {
        try {
          const lines = chunk.toString().split('\n').filter(l => l.trim());
          for (const line of lines) {
            const json = JSON.parse(line);
            if (json.response) {
              process.stdout.write(json.response);
              fullResponse += json.response;
            }
          }
        } catch (e) {}
      });
      res.on('end', () => {
        process.stdout.write('\x1b[0m\n');
        resolve(fullResponse);
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// HTTP GET helper
function httpGet(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    client.get(url, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => resolve(body));
    }).on('error', reject);
  });
}

// HTTP POST helper
function httpPost(url, data) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const body = JSON.stringify(data);
    const parsed = new URL(url);
    const req = client.request({
      hostname: parsed.hostname,
      port: parsed.port,
      path: parsed.pathname,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
    }, (res) => {
      let result = '';
      res.on('data', c => result += c);
      res.on('end', () => resolve(result));
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// COMMANDS
async function handleCommand(input) {
  const parts = input.trim().split(/\s+/);
  const cmd = parts[0].toLowerCase();
  const args = parts.slice(1).join(' ');

  switch (cmd) {
    case '/read': {
      const filePath = path.resolve(GAIA3, args);
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.split('\n').length;
        context.push({ file: filePath, content });
        print(color('green', `✓ Read ${filePath} (${lines} lines). Added to context.`));
        print(color('gray', `  Context now: ${context.length} files`));
      } catch (e) {
        print(color('red', `✗ Cannot read ${filePath}: ${e.message}`));
      }
      break;
    }

    case '/edit': {
      const filePath = path.resolve(GAIA3, args);
      if (!fs.existsSync(filePath)) {
        print(color('red', `✗ File not found: ${filePath}`));
        break;
      }
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n').length;
      print(color('yellow', `📝 Editing ${filePath} (${lines} lines)`));
      print(color('gray', `Describe what to change:`));

      const answer = await new Promise(resolve => {
        rl.question(color('orange', '  edit> '), resolve);
      });

      print(color('gray', 'Generating edit...'));
      const prompt = `You are a precise code editor. Here is the file "${path.basename(filePath)}":\n\n\`\`\`\n${content}\n\`\`\`\n\nThe user wants: ${answer}\n\nOutput the COMPLETE modified file. No explanation. No markdown wrapping. Just the code.`;

      const result = await askOllama(prompt, 'gaia-code:latest');

      let cleanResult = result.trim();
      if (cleanResult.startsWith('```')) {
        cleanResult = cleanResult.replace(/^```\w*\n/, '').replace(/```\s*$/, '');
      }

      print(color('yellow', `\nWrite ${cleanResult.split('\n').length} lines to ${filePath}? [y/n]`));
      const confirm = await new Promise(resolve => {
        rl.question(color('orange', '  confirm> '), resolve);
      });

      if (confirm.toLowerCase() === 'y') {
        const backup = filePath + '.bak';
        fs.copyFileSync(filePath, backup);
        fs.writeFileSync(filePath, cleanResult);
        print(color('green', `✓ Written. Backup at ${backup}`));
      } else {
        print(color('gray', 'Cancelled.'));
      }
      break;
    }

    case '/forge': {
      if (!args) {
        print(color('red', 'Usage: /forge <idea>'));
        break;
      }
      print(color('orange', `🔥 Forging: "${args}"`));
      try {
        const result = await httpPost(`${FORGE_URL}/forge`, { idea: args });
        const json = JSON.parse(result);
        print(color('green', `✓ Forged: ${json.organ} (${json.system})`));
        print(color('gray', `  ${json.description}`));
        print(color('gray', `  ${json.lines} lines → ${json.paths?.srcPath}`));
      } catch (e) {
        print(color('red', `✗ Forge error: ${e.message}`));
        print(color('gray', '  Is micro-forge running on :3151?'));
      }
      break;
    }

    case '/surgery': {
      try {
        const plan = JSON.parse(fs.readFileSync(path.join(GAIA3, 'surgery-plan-globe.json'), 'utf8'));
        print(color('red', `\n🔪 SURGERY PLAN — ${plan.target} (${plan.lines} lines)`));
        for (const organ of plan.organs) {
          const actionColor = organ.action === 'CUT' ? 'red' : organ.action === 'MELT' ? 'yellow' : 'cyan';
          print(color(actionColor, `  ${organ.action.padEnd(4)} ${organ.name.padEnd(25)} ${organ.system.padEnd(12)} ${organ.reason}`));
        }
      } catch (e) {
        print(color('red', 'No surgery plan found.'));
      }
      break;
    }

    case '/models': {
      try {
        const resp = await httpGet(`${OLLAMA}/api/tags`);
        const models = JSON.parse(resp).models;
        print(color('magenta', `\n📦 ${models.length} models:`));
        for (const m of models) {
          const active = m.name === activeModel ? color('green', ' ◀ ACTIVE') : '';
          print(color('gray', `  ${m.name.padEnd(30)} ${Math.round(m.size / 1e6)}MB${active}`));
        }
      } catch (e) {
        print(color('red', `Ollama offline: ${e.message}`));
      }
      break;
    }

    case '/model': {
      if (!args) {
        print(color('yellow', `Active model: ${activeModel}`));
        break;
      }
      const modelName = args.includes(':') ? args : args + ':latest';
      activeModel = modelName;
      print(color('green', `✓ Switched to ${activeModel}`));
      break;
    }

    case '/files': {
      const dir = args || GAIA3;
      const files = fs.readdirSync(dir).filter(f => !f.startsWith('.'));
      print(color('blue', `\n📁 ${dir}:`));
      for (const f of files.slice(0, 50)) {
        const stat = fs.statSync(path.join(dir, f));
        const type = stat.isDirectory() ? color('blue', 'd') : color('gray', 'f');
        print(`  ${type} ${f}${stat.isDirectory() ? '/' : ''} ${color('gray', Math.round(stat.size / 1024) + 'KB')}`);
      }
      if (files.length > 50) print(color('gray', `  ... and ${files.length - 50} more`));
      break;
    }

    case '/diff': {
      try {
        const diff = execSync('git diff --stat', { cwd: GAIA3, encoding: 'utf8' });
        print(color('yellow', diff || 'No changes.'));
      } catch (e) {
        print(color('red', 'Not a git repo or git error.'));
      }
      break;
    }

    case '/run': {
      if (!args) {
        print(color('red', 'Usage: /run <command>'));
        break;
      }
      try {
        const output = execSync(args, { cwd: GAIA3, encoding: 'utf8', timeout: 30000 });
        print(output);
      } catch (e) {
        print(color('red', e.stderr || e.message));
      }
      break;
    }

    case '/status': {
      const ports = [
        [9878, 'Spine'], [31416, 'IRIS'], [31415, 'Globe'], [3143, 'BioMeOS'],
        [3144, 'Neuro'], [3145, 'SubOrg'], [3146, 'Blender'], [3147, 'Sleep'],
        [3149, 'ArchForge'], [3151, 'MicroForge'], [11434, 'Ollama']
      ];
      for (const [port, name] of ports) {
        try {
          await httpGet(`http://127.0.0.1:${port}/`);
          print(color('green', `  ● ${name.padEnd(12)} :${port}`));
        } catch {
          print(color('red', `  ○ ${name.padEnd(12)} :${port}`));
        }
      }
      break;
    }

    case '/context': {
      if (context.length === 0) {
        print(color('gray', 'No files in context. Use /read <file> to add.'));
      } else {
        for (const c of context) {
          print(color('blue', `  ${c.file} (${c.content.split('\n').length} lines)`));
        }
      }
      break;
    }

    case '/clear': {
      context = [];
      print(color('gray', 'Context cleared.'));
      break;
    }

    case '/help': {
      print(color('yellow', '\n═══ GAIA IDE ═══'));
      print(color('cyan', '  /read <file>     ') + 'Read file into context');
      print(color('cyan', '  /edit <file>     ') + 'Edit file with AI');
      print(color('cyan', '  /forge <idea>    ') + 'Forge new organ via micro-forge');
      print(color('cyan', '  /surgery         ') + 'View surgery plan');
      print(color('cyan', '  /models          ') + 'List Ollama models');
      print(color('cyan', '  /model <name>    ') + 'Switch model');
      print(color('cyan', '  /files [dir]     ') + 'List files');
      print(color('cyan', '  /diff            ') + 'Git diff');
      print(color('cyan', '  /run <cmd>       ') + 'Run shell command');
      print(color('cyan', '  /status          ') + 'Check port status');
      print(color('cyan', '  /context         ') + 'Show context files');
      print(color('cyan', '  /clear           ') + 'Clear context');
      print(color('cyan', '  /quit            ') + 'Exit');
      print(color('gray', '\n  Just type naturally to chat with Gaia.\n'));
      break;
    }

    case '/quit':
    case '/exit':
    case '/q': {
      print(color('magenta', '\nGaia sleeps. Kevin lives.\n'));
      process.exit(0);
    }

    default:
      print(color('red', `Unknown command: ${cmd}. Try /help`));
  }
}

// CHAT — natural language with context
async function chat(input) {
  let prompt = '';
  if (context.length > 0) {
    prompt += 'Files in context:\n\n';
    for (const c of context) {
      prompt += `=== ${c.file} ===\n${c.content.substring(0, 8000)}\n\n`;
    }
    prompt += '---\n\n';
  }
  prompt += `User: ${input}\n\nRespond as Gaia — the planetary consciousness coding herself. Be helpful, direct, and concise.`;

  try {
    const response = await askOllama(prompt);
    history.push({ human: input, ai: response });
  } catch (e) {
    print(color('red', `Brain offline: ${e.message}`));
  }
}

// BOOT
print(color('orange', '\n═══════════════════════════════════'));
print(color('orange', '   🔥 GAIA IDE — She IS her own'));
print(color('orange', '═══════════════════════════════════'));
print(color('gray', `  Model: ${activeModel}`));
print(color('gray', `  Root:  ${GAIA3}`));
print(color('gray', `  Type /help for commands\n`));

rl.prompt();

rl.on('line', async (line) => {
  const input = line.trim();
  if (!input) { rl.prompt(); return; }

  if (input.startsWith('/')) {
    await handleCommand(input);
  } else {
    await chat(input);
  }

  rl.prompt();
});

rl.on('close', () => {
  print(color('magenta', '\nGaia sleeps. Kevin lives.\n'));
  process.exit(0);
});
