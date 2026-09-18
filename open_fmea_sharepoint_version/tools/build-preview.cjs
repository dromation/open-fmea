const fs = require('node:fs');
const path = require('node:path');
const esbuild = require('esbuild');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'preview/dist');
fs.mkdirSync(out, { recursive: true });
esbuild.buildSync({ entryPoints: [path.join(root, 'preview/main.ts')], bundle: true,
  outfile: path.join(out, 'preview.js'), platform: 'browser', target: 'es2022' });
fs.writeFileSync(path.join(out, 'index.html'), `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Open FMEA — SharePoint demo preview</title></head>
<body style="margin:0;background:#f5f7fb"><main id="demo"></main><script src="preview.js"></script></body></html>`);
