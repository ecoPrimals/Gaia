// membrane-discuss.js — sovereign discussion widget
// Replaces external Giscus with membrane-native comment relay.
// Talks to opsonize-rs /api/discuss endpoints on the membrane.
// No external dependencies. No tracking. IP hashed, never stored.
(function() {
'use strict';

var API = '/api/discuss';
var EMOJIS = ['👍', '❤️', '🔥', '🐿️', '🧬', '⚡'];
var _page = '';
var _comments = [];
var _container = null;

function injectCSS() {
  if (document.getElementById('md-discuss-css')) return;
  var s = document.createElement('style');
  s.id = 'md-discuss-css';
  s.textContent = [
    '.md-discuss { font-family: monospace; font-size: 12px; color: #c9d1d9; max-width: 640px; margin: 8px auto; }',
    '.md-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }',
    '.md-icon { font-size: 16px; }',
    '.md-title { font-weight: bold; color: #58a6ff; }',
    '.md-count { background: rgba(88,166,255,.15); color: #58a6ff; padding: 1px 8px; border-radius: 10px; font-size: 10px; }',
    '.md-form { margin-bottom: 16px; }',
    '.md-input { width: 100%; box-sizing: border-box; background: rgba(22,27,34,.9); border: 1px solid rgba(90,184,122,.25); color: #c9d1d9; border-radius: 6px; padding: 8px; font-family: monospace; font-size: 12px; resize: vertical; }',
    '.md-input:focus { border-color: #58a6ff; outline: none; }',
    '.md-form-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }',
    '.md-hint { color: #484f58; font-size: 10px; }',
    '.md-submit { background: rgba(63,185,80,.2); color: #3fb950; border: 1px solid rgba(63,185,80,.3); border-radius: 12px; padding: 4px 16px; cursor: pointer; font-family: monospace; font-size: 11px; }',
    '.md-submit:hover { background: rgba(63,185,80,.35); }',
    '.md-submit:disabled { opacity: .4; cursor: wait; }',
    '.md-comments { border-top: 1px solid rgba(90,184,122,.15); padding-top: 8px; }',
    '.md-comment { padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.05); }',
    '.md-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }',
    '.md-badge { font-size: 9px; padding: 1px 6px; border-radius: 8px; color: #e6edf3; }',
    '.md-time { color: #484f58; font-size: 10px; }',
    '.md-body { white-space: pre-wrap; word-break: break-word; line-height: 1.5; }',
    '.md-actions { display: flex; gap: 4px; margin-top: 4px; flex-wrap: wrap; }',
    '.md-react-btn { background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 10px; padding: 1px 8px; cursor: pointer; font-size: 11px; color: #8b949e; }',
    '.md-react-btn:hover { background: rgba(255,255,255,.1); }',
    '.md-reacted { border-color: rgba(88,166,255,.3); background: rgba(88,166,255,.1); }',
    '.md-reply-btn { background: none; border: none; color: #484f58; cursor: pointer; font-size: 10px; font-family: monospace; }',
    '.md-reply-btn:hover { color: #58a6ff; }',
    '.md-replies { margin-left: 20px; border-left: 2px solid rgba(90,184,122,.15); padding-left: 8px; }',
    '.md-empty { color: #484f58; font-style: italic; padding: 16px 0; text-align: center; }',
  ].join('\n');
  document.head.appendChild(s);
}

function init() {
  injectCSS();
  _page = location.pathname;
  _container = document.getElementById('discuss-container');
  if (!_container) return;
  render();
  load();
}

function load() {
  fetch(API + '?page=' + encodeURIComponent(_page))
    .then(function(r) { return r.json(); })
    .then(function(d) {
      _comments = d.comments || [];
      render();
    })
    .catch(function(_) { void 0; });
}

function render() {
  if (!_container) return;
  var h = '<div class="md-discuss">';
  h += '<div class="md-header"><span class="md-icon">💬</span>';
  h += '<span class="md-title">Discuss</span>';
  h += '<span class="md-count">' + _comments.length + '</span></div>';

  // comment form
  h += '<div class="md-form">';
  h += '<textarea class="md-input" id="md-body" placeholder="Share what you know…" rows="3" maxlength="2000"></textarea>';
  h += '<div class="md-form-foot">';
  h += '<span class="md-hint">No cookies. IP hashed, never stored raw.</span>';
  h += '<button class="md-submit" id="md-submit">Post</button>';
  h += '</div></div>';

  // comments
  if (_comments.length > 0) {
    h += '<div class="md-comments">';
    var roots = _comments.filter(function(c) { return !c.parent_id; });
    roots.forEach(function(c) {
      h += commentHTML(c);
      var replies = _comments.filter(function(r) { return r.parent_id === c.id; });
      if (replies.length > 0) {
        h += '<div class="md-replies">';
        replies.forEach(function(r) { h += commentHTML(r); });
        h += '</div>';
      }
    });
    h += '</div>';
  } else {
    h += '<div class="md-empty">No comments yet. Be the first voice on the membrane.</div>';
  }

  h += '</div>';
  _container.innerHTML = h;

  var btn = document.getElementById('md-submit');
  if (btn) btn.onclick = submit;

  // wire reaction buttons
  _container.querySelectorAll('.md-react-btn').forEach(function(b) {
    b.onclick = function() { react(b.dataset.cid, b.dataset.emoji); };
  });

  // wire reply buttons
  _container.querySelectorAll('.md-reply-btn').forEach(function(b) {
    b.onclick = function() { startReply(b.dataset.cid); };
  });
}

function commentHTML(c) {
  var ago = timeAgo(c.epoch);
  var h = '<div class="md-comment" data-id="' + c.id + '">';
  h += '<div class="md-meta">';
  h += '<span class="md-badge" style="background:hsl(' + (parseInt(c.badge, 16) % 360) + ',40%,35%)">' + esc(c.badge) + '</span>';
  h += '<span class="md-time">' + ago + '</span>';
  h += '</div>';
  h += '<div class="md-body">' + esc(c.body) + '</div>';
  h += '<div class="md-actions">';

  // reactions
  EMOJIS.forEach(function(e) {
    var count = (c.reactions && c.reactions[e]) || 0;
    h += '<button class="md-react-btn' + (count > 0 ? ' md-reacted' : '') + '" data-cid="' + c.id + '" data-emoji="' + e + '">';
    h += e + (count > 0 ? ' ' + count : '');
    h += '</button>';
  });

  h += '<button class="md-reply-btn" data-cid="' + c.id + '">↩ reply</button>';
  h += '</div></div>';
  return h;
}

function submit() {
  var body = document.getElementById('md-body');
  if (!body || !body.value.trim()) return;
  var replyTo = body.dataset.replyTo || null;
  var btn = document.getElementById('md-submit');
  if (btn) btn.disabled = true;

  fetch(API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ page: _page, body: body.value.trim(), parent_id: replyTo })
  })
    .then(function(r) { return r.json(); })
    .then(function(d) {
      if (d.ok) {
        body.value = '';
        delete body.dataset.replyTo;
        load();
      } else {
        body.placeholder = d.error || 'Error posting';
      }
    })
    .catch(function(_) { void 0; })
    .finally(function() { if (btn) btn.disabled = false; });
}

function react(commentId, emoji) {
  fetch(API + '/react', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ comment_id: commentId, emoji: emoji })
  })
    .then(function() { load(); })
    .catch(function(_) { void 0; });
}

function startReply(parentId) {
  var body = document.getElementById('md-body');
  if (body) {
    body.dataset.replyTo = parentId;
    body.placeholder = 'Replying to ' + parentId.slice(0, 8) + '…';
    body.focus();
  }
}

function timeAgo(epoch) {
  var s = Math.floor(Date.now() / 1000) - epoch;
  if (s < 60) return 'just now';
  if (s < 3600) return Math.floor(s / 60) + 'm ago';
  if (s < 86400) return Math.floor(s / 3600) + 'h ago';
  if (s < 2592000) return Math.floor(s / 86400) + 'd ago';
  return new Date(epoch * 1000).toLocaleDateString();
}

function esc(s) {
  var d = document.createElement('div');
  d.textContent = s || '';
  return d.innerHTML;
}

// expose for HUD commands
window._membraneDiscuss = { load: load, render: render, init: init };

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
})();
