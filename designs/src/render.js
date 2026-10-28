// Renders every design in designs.js to a transparent PNG in designs/print/,
// plus designs/preview.png showing each one on a shirt-colored background.
// Usage: node designs/src/render.js

const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');
const { designs } = require('./designs');

const OUT = path.join(__dirname, '..', 'print');
const FONTS =
  'https://fonts.googleapis.com/css2?family=Anton&family=Archivo+Black&family=Cinzel:wght@700' +
  '&family=Oswald:wght@500;600&family=Space+Mono:wght@400;700&display=block';

function page(design) {
  return `<!doctype html><html><head><meta charset="utf-8">
    <link rel="stylesheet" href="${FONTS}">
    <style>html,body{margin:0;background:transparent}#art{width:${design.width}px;padding:12px;box-sizing:content-box}</style>
    </head><body><div id="art">${design.html}</div></body></html>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  for (const design of designs) {
    const ctx = await browser.newContext({ deviceScaleFactor: design.scale, viewport: { width: 1400, height: 1000 } });
    const p = await ctx.newPage();
    await p.setContent(page(design), { waitUntil: 'networkidle' });
    const missing = await p.evaluate(async () => {
      const fonts = ['Anton', 'Archivo Black', '700 40px Cinzel', '500 40px Oswald', '600 40px Oswald', 'Space Mono', '700 40px "Space Mono"'];
      const specs = fonts.map((f) => (f.includes('px') ? f : `40px "${f}"`));
      await Promise.all(specs.map((s) => document.fonts.load(s)));
      await document.fonts.ready;
      return specs.filter((s) => !document.fonts.check(s));
    });
    if (missing.length) throw new Error(`${design.file}: fonts not loaded: ${missing.join(', ')}`);
    await p.locator('#art').screenshot({ path: path.join(OUT, design.file), omitBackground: true });
    console.log('rendered', design.file);
    await ctx.close();
  }

  // Preview sheet: each PNG on a background matching the shirt color it's meant for.
  const tiles = designs
    .map((d) => {
      const bg = d.file.includes('white') ? '#1d1d1f' : '#efe9dd';
      const data = fs.readFileSync(path.join(OUT, d.file)).toString('base64');
      return `<figure style="background:${bg}"><img src="data:image/png;base64,${data}"><figcaption>${d.file}</figcaption></figure>`;
    })
    .join('');
  const ctx = await browser.newContext({ viewport: { width: 1600, height: 900 } });
  const p = await ctx.newPage();
  await p.setContent(`<!doctype html><html><body style="margin:0;font-family:sans-serif;background:#888">
    <style>
      .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;padding:12px}
      figure{margin:0;padding:24px;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:300px}
      img{max-width:100%;max-height:340px}
      figcaption{font-size:12px;color:#888;margin-top:12px}
    </style><div class="grid">${tiles}</div></body></html>`);
  await p.screenshot({ path: path.join(__dirname, '..', 'preview.png'), fullPage: true });
  await browser.close();
  console.log('wrote preview.png');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
