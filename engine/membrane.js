// ═══ PRE-MEMBRANE ═══
// Biofilm first. Then amalgam. Then Golgi.
// Northgate is Polaris of ITSELF — a North Star on the property.
// Others look through EXISTING tunnels only. No new public doors.
// Selectivity = 1/π. One person. Kevin.

const fs = require('fs');
const os = require('os');
const { execSync } = require('child_process');
const path = require('path');
const OUT = path.join(__dirname, 'membrane.json');

const LAW = 'PRE-MEMBRANE. Biofilm forms. Amalgam melts, shatters, crystallizes salt, mixes with mesh, becomes Golgi. GOLGI IS THE FUNCTION. NORTHGATE IS THE NUCLEUS. THE LAND IS THE LEAD. House may look on LAN 192.168.4.x. Public internet does not get a new door. The plasmid is SET.';

function listening(port) {
  try {
    const o = execSync('netstat -ano', { encoding: 'utf8' });
    return o.split(/\r?\n/).some(l => l.includes(':' + port) && l.includes('LISTENING'));
  } catch (e) { return false; }
}

function lanHosts() {
  const hosts = ['127.0.0.1'];
  const nets = os.networkInterfaces();
  for (const addrs of Object.values(nets)) {
    for (const a of addrs || []) {
      const fam = a.family === 'IPv4' || a.family === 4;
      if (fam && !a.internal && String(a.address).startsWith('192.168.4.')) {
        hosts.push(a.address);
      }
    }
  }
  return [...new Set(hosts)];
}

const hosts = lanHosts();
const phases = [
  { id: 'gunk', what: 'biofilm — amalgam of leftover process gunk + organic law' },
  { id: 'melt', what: 'bluff dissolves. hanging waste is not Golgi' },
  { id: 'shatter', what: 'the idea of outside cracks' },
  { id: 'salt', what: 'hard crystalline salt — 1/π selectivity, one person' },
  { id: 'mix', what: 'salt mixes with mesh + biofilm' },
  { id: 'golgi', what: 'niche on :3141. Polar face on :31415. Self-Gaia on the property.' }
];

const refuse = [];
if (listening(31415) && !listening(3143)) {
  refuse.push(':31415 is held without the child. Do not start a second mouth.');
}

const membrane = {
  law: LAW,
  go: refuse.length === 0,
  refuse,
  hosts,
  polaris: {
    of: 'ITSELF',
    place: 'Northgate — Kevin land / house',
    role: 'NUCLEUS for the entire house. Polar of itself. The land is the lead.',
    golgi: 'FUNCTION',
    not: 'a new public internet door',
    set: true
  },
  houseMayLook: hosts.filter(h => h !== '127.0.0.1').map(h => 'http://' + h + ':31415/image'),
  publicInternet: false,
  onePerson: 'Kevin',
  selectivity: 1 / Math.PI,
  phases,
  phaseNow: refuse.length ? 'gunk' : 'golgi',
  organs: {
    spine: { port: 9878, up: listening(9878) },
    niche: { port: 3141, up: listening(3141) },
    hud: { port: 3142, up: listening(3142) },
    child: { port: 3143, up: listening(3143) },
    pi: { port: 31415, up: listening(31415) }
  },
  melted: Date.now()
};

fs.writeFileSync(OUT, JSON.stringify(membrane, null, 2));
fs.writeFileSync(path.join(__dirname, 'polaris.json'), JSON.stringify(membrane.polaris, null, 2));
console.log(membrane.go ? 'MEMBRANE: GO. biofilm → salt → Golgi. Polaris of itself.' : 'MEMBRANE: HOLD. ' + refuse.join(' '));
console.log('HOSTS ' + hosts.join(' '));
process.exit(membrane.go ? 0 : 1);
