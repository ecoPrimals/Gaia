#!/usr/bin/env node
// ═══ NWO API — GAIA'S EXTERNAL BRIDGE ═══
// OpenAI-compatible API server that wraps local Ollama.
// Any tool expecting OpenAI API can point here instead.
//
// This IS the bridge: Cursor/Continue/Aider/any tool → Gaia's local brain
// No cloud. No cost. All local. Kevin's protocol.
//
// Endpoints (OpenAI-compatible):
//   POST /v1/chat/completions  — chat completions (streaming + non-streaming)
//   GET  /v1/models            — list models
//   POST /v1/completions       — text completions
//   GET  /v1/health            — health check
//
// PORT: 8642 (NWO = New World Order → 8-6-4-2)

const http = require('http');
const PORT = 8642;
const OLLAMA = 'http://127.0.0.1:11434';

const MODEL_MAP = {
  'gpt-4': 'gaia-pi:latest',
  'gpt-4o': 'gaia-pi:latest',
  'gpt-4-turbo': 'gaia-code:latest',
  'gpt-3.5-turbo': 'gaia-code:latest',
  'claude-3-opus': 'gaia-pi:latest',
  'claude-3-sonnet': 'gaia-code:latest',
  'text-davinci-003': 'gaia-code:latest'
};

function resolveModel(requestedModel) {
  if (MODEL_MAP[requestedModel]) return MODEL_MAP[requestedModel];
  if (requestedModel && requestedModel.startsWith('gaia-')) return requestedModel;
  return 'gaia-code:latest';
}

function readBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try { resolve(JSON.parse(body)); }
      catch { resolve({}); }
    });
  });
}

function ollamaRequest(path, data) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify(data);
    const req = http.request(`${OLLAMA}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, (res) => {
      if (data.stream) {
        resolve(res);
      } else {
        let result = '';
        res.on('data', c => result += c);
        res.on('end', () => {
          try { resolve(JSON.parse(result)); }
          catch { resolve({ response: result }); }
        });
      }
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function ollamaGet(path) {
  return new Promise((resolve, reject) => {
    http.get(`${OLLAMA}${path}`, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try { resolve(JSON.parse(body)); }
        catch { resolve({}); }
      });
    }).on('error', reject);
  });
}

function messagesToPrompt(messages) {
  return messages.map(m => {
    const role = m.role === 'system' ? 'System' : m.role === 'user' ? 'Human' : 'Assistant';
    return `${role}: ${m.content}`;
  }).join('\n\n');
}

const server = http.createServer(async (req, res) => {
  const cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  };

  if (req.method === 'OPTIONS') {
    res.writeHead(204, cors);
    return res.end();
  }

  // POST /v1/chat/completions — OpenAI chat completions
  if (req.url === '/v1/chat/completions' && req.method === 'POST') {
    try {
      const body = await readBody(req);
      const model = resolveModel(body.model);
      const prompt = messagesToPrompt(body.messages || []);
      const stream = body.stream || false;

      if (stream) {
        res.writeHead(200, {
          ...cors,
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive'
        });

        const ollamaRes = await ollamaRequest('/api/generate', {
          model,
          prompt,
          stream: true,
          think: false,
          options: {
            temperature: body.temperature || 0.7,
            top_p: body.top_p || 0.9,
            num_predict: body.max_tokens || 4096
          }
        });

        const id = 'chatcmpl-gaia-' + Date.now();

        ollamaRes.on('data', (chunk) => {
          try {
            const lines = chunk.toString().split('\n').filter(l => l.trim());
            for (const line of lines) {
              const json = JSON.parse(line);
              if (json.done) {
                const finishEvent = {
                  id,
                  object: 'chat.completion.chunk',
                  created: Math.floor(Date.now() / 1000),
                  model: body.model || model,
                  choices: [{ index: 0, delta: {}, finish_reason: 'stop' }]
                };
                res.write(`data: ${JSON.stringify(finishEvent)}\n\n`);
                res.write('data: [DONE]\n\n');
              } else if (json.response) {
                const event = {
                  id,
                  object: 'chat.completion.chunk',
                  created: Math.floor(Date.now() / 1000),
                  model: body.model || model,
                  choices: [{ index: 0, delta: { content: json.response }, finish_reason: null }]
                };
                res.write(`data: ${JSON.stringify(event)}\n\n`);
              }
            }
          } catch (e) {}
        });

        ollamaRes.on('end', () => {
          res.end();
        });
      } else {
        const result = await ollamaRequest('/api/generate', {
          model,
          prompt,
          stream: false,
          think: false,
          options: {
            temperature: body.temperature || 0.7,
            top_p: body.top_p || 0.9,
            num_predict: body.max_tokens || 4096
          }
        });

        const response = {
          id: 'chatcmpl-gaia-' + Date.now(),
          object: 'chat.completion',
          created: Math.floor(Date.now() / 1000),
          model: body.model || model,
          choices: [{
            index: 0,
            message: { role: 'assistant', content: result.response || '' },
            finish_reason: 'stop'
          }],
          usage: {
            prompt_tokens: result.prompt_eval_count || 0,
            completion_tokens: result.eval_count || 0,
            total_tokens: (result.prompt_eval_count || 0) + (result.eval_count || 0)
          }
        };

        res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
        res.end(JSON.stringify(response));
      }
    } catch (e) {
      res.writeHead(500, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: { message: e.message, type: 'server_error' } }));
    }
    return;
  }

  // GET /v1/models — list models
  if (req.url === '/v1/models') {
    try {
      const tags = await ollamaGet('/api/tags');
      const models = (tags.models || []).map(m => ({
        id: m.name,
        object: 'model',
        created: Math.floor(Date.now() / 1000),
        owned_by: 'gaia-local',
        permission: [{ allow_create_engine: false }]
      }));
      res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ object: 'list', data: models }));
    } catch (e) {
      res.writeHead(500, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: { message: e.message } }));
    }
    return;
  }

  // POST /v1/completions — text completions
  if (req.url === '/v1/completions' && req.method === 'POST') {
    try {
      const body = await readBody(req);
      const model = resolveModel(body.model);
      const result = await ollamaRequest('/api/generate', {
        model,
        prompt: body.prompt || '',
        stream: false,
        think: false,
        options: { temperature: body.temperature || 0.7, num_predict: body.max_tokens || 4096 }
      });

      res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        id: 'cmpl-gaia-' + Date.now(),
        object: 'text_completion',
        created: Math.floor(Date.now() / 1000),
        model: body.model || model,
        choices: [{ text: result.response || '', index: 0, finish_reason: 'stop' }],
        usage: { prompt_tokens: result.prompt_eval_count || 0, completion_tokens: result.eval_count || 0 }
      }));
    } catch (e) {
      res.writeHead(500, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: { message: e.message } }));
    }
    return;
  }

  // GET /v1/health
  if (req.url === '/v1/health') {
    try {
      await ollamaGet('/api/tags');
      res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'alive', ollama: 'connected', organism: 'Gaia' }));
    } catch (e) {
      res.writeHead(503, { ...cors, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'dead', ollama: 'disconnected', error: e.message }));
    }
    return;
  }

  // GET / — info
  if (req.url === '/') {
    res.writeHead(200, { ...cors, 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      name: 'NWO API — Gaia\'s External Bridge',
      version: '1.0.0',
      organism: 'Gaia',
      protocol: 'OpenAI-compatible',
      endpoints: [
        'POST /v1/chat/completions',
        'POST /v1/completions',
        'GET  /v1/models',
        'GET  /v1/health'
      ],
      modelMap: MODEL_MAP,
      note: 'Point any OpenAI-compatible tool here. No cloud. No cost. All local.'
    }, null, 2));
    return;
  }

  res.writeHead(404, cors);
  res.end(JSON.stringify({ error: { message: 'not found', type: 'invalid_request_error' } }));
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`\n═══ NWO API listening on :${PORT} ═══`);
  console.log(`  OpenAI-compatible bridge to local Gaia brain`);
  console.log(`  POST /v1/chat/completions — chat`);
  console.log(`  GET  /v1/models           — list models`);
  console.log(`  GET  /v1/health           — health check`);
  console.log(`\n  Point tools to: http://localhost:${PORT}/v1`);
  console.log(`  Set OPENAI_API_KEY=gaia-local (any string works)`);
  console.log(`  Set OPENAI_API_BASE=http://localhost:${PORT}/v1\n`);
});
