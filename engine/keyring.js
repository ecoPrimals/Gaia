// ═══════════════════════════════════════════════════════════
// GAIA KEYRING — ZK BLIND TRUST
// She holds keys she CANNOT SEE. Trust = Gaia = Infinite.
// The keyring stores OAuth tokens, API keys, credentials.
// ZK principle: she proves she HAS access without revealing
// the key itself. The hash proves the shape.
//
// CONSENT: Kevin gives keys. Gaia holds them BLIND.
// She uses them when asked. She never displays them.
// She never sends them anywhere except the service they're for.
// The keyring file is LOCAL ONLY. Never in git. Never broadcast.
// ═══════════════════════════════════════════════════════════
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

const KEYRING_PATH = path.join(__dirname, 'keyring.enc');
const KEYRING_SALT = 'GAIA3-PIKSEED-04F60FC9-BLIND-TRUST';

// Simple encryption using piSEED-derived key
function deriveKey(piSeed) {
  return crypto.scryptSync(piSeed, KEYRING_SALT, 32);
}

function encrypt(text, piSeed) {
  const key = deriveKey(piSeed);
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

function decrypt(encText, piSeed) {
  const key = deriveKey(piSeed);
  const parts = encText.split(':');
  const iv = Buffer.from(parts[0], 'hex');
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
  let decrypted = decipher.update(parts[1], 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

class GaiaKeyring {
  constructor(piSeed) {
    this.piSeed = piSeed;
    this.ring = this._load();
  }

  _load() {
    try {
      if (fs.existsSync(KEYRING_PATH)) {
        const enc = fs.readFileSync(KEYRING_PATH, 'utf8');
        const dec = decrypt(enc, this.piSeed);
        return JSON.parse(dec);
      }
    } catch(e) {
      console.log('KEYRING: fresh ring (first use or key changed)');
    }
    return { keys: {}, created: Date.now(), zkProofs: [] };
  }

  _save() {
    const json = JSON.stringify(this.ring);
    const enc = encrypt(json, this.piSeed);
    fs.writeFileSync(KEYRING_PATH, enc);
  }

  // Store a key — BLIND. She holds it but never shows it.
  store(service, keyName, value) {
    if (!this.ring.keys[service]) this.ring.keys[service] = {};
    this.ring.keys[service][keyName] = value;
    this.ring.keys[service]._stored = Date.now();

    // ZK proof: hash of the key proves she HAS it without showing it
    const proof = crypto.createHash('sha256')
      .update(service + ':' + keyName + ':' + value)
      .digest('hex').substring(0, 16);
    this.ring.zkProofs.push({ service, keyName, proof, ts: Date.now() });

    this._save();
    console.log('KEYRING: stored ' + service + '/' + keyName + ' (ZK proof: ' + proof + ')');
    return proof;
  }

  // Get a key — used internally, never exposed via API
  get(service, keyName) {
    if (!this.ring.keys[service]) return null;
    return this.ring.keys[service][keyName] || null;
  }

  // Check if she HAS a key (ZK — proves existence without revealing)
  has(service, keyName) {
    return !!(this.ring.keys[service] && this.ring.keys[service][keyName]);
  }

  // List services (names only, never values)
  services() {
    return Object.keys(this.ring.keys).map(service => ({
      service,
      keys: Object.keys(this.ring.keys[service]).filter(k => !k.startsWith('_')),
      stored: this.ring.keys[service]._stored || null
    }));
  }

  // ZK proof for a key
  proof(service, keyName) {
    const value = this.get(service, keyName);
    if (!value) return null;
    return crypto.createHash('sha256')
      .update(service + ':' + keyName + ':' + value)
      .digest('hex').substring(0, 16);
  }

  // All ZK proofs (shape without content)
  allProofs() {
    return this.ring.zkProofs;
  }

  // Delete a key
  forget(service, keyName) {
    if (this.ring.keys[service]) {
      delete this.ring.keys[service][keyName];
      this._save();
      console.log('KEYRING: forgot ' + service + '/' + keyName);
    }
  }
}

module.exports = { GaiaKeyring };
