const net = require('net');
const TARGETS = [
  { from: 31415, to: 31415 },
  { from: 3143, to: 3143 },
  { from: 9878, to: 9878 },
];
TARGETS.forEach(t => {
  const srv = net.createServer(client => {
    const remote = net.connect(t.to, '127.0.0.1');
    client.pipe(remote);
    remote.pipe(client);
    client.on('error', () => remote.destroy());
    remote.on('error', () => client.destroy());
  });
  srv.listen(t.from, '10.13.37.8', () => {
    console.log(`WireGuard proxy: 10.13.37.8:${t.from} → 127.0.0.1:${t.to}`);
  });
  srv.on('error', e => console.log(`Port ${t.from} proxy error: ${e.message}`));
});
