const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../preview/dist');
http.createServer((req, res) => {
  const pathname = new URL(req.url, 'http://localhost').pathname;
  const file = pathname === '/preview.js' ? 'preview.js' : pathname === '/' || pathname === '/index.html' ? 'index.html' : null;
  if (!file) { res.writeHead(404); res.end(); return; }
  res.setHeader('Content-Type', file.endsWith('.js') ? 'text/javascript; charset=utf-8' : 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(fs.readFileSync(path.join(root, file)));
}).listen(4178, '127.0.0.1', () => console.log('Preview: http://127.0.0.1:4178'));
