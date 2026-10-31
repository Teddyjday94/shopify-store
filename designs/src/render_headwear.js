// Renders the embroidered headwear designs to transparent PNGs in designs/print/,
// one per thread color (white for dark hats, black for light ones).
// Usage: node designs/src/render_headwear.js

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const OUT = path.join(__dirname, '..', 'print');
const FONTS = path.join(__dirname, '..', '..', 'theme', 'assets');

const designs = [
  { name: '07-currently-elsewhere-hat', font: 'Archivo Black', size: 150, lh: 1.0, ls: '0.02em',
    lines: ['CURRENTLY', 'ELSEWHERE'] },
  { name: '08-not-ai-just-tired-trucker', font: 'Anton', size: 190, lh: 1.0, ls: '0.03em',
    lines: ['NOT AI.', 'JUST TIRED.'] },
  { name: '09-elsewhere-beanie', font: 'Archivo Black', size: 170, lh: 1.0, ls: '0.12em',
    lines: ['ELSEWHERE'] },
  { name: '10-same-chaos-bucket', font: 'Anton', size: 170, lh: 1.0, ls: '0.03em',
    lines: ['SAME CHAOS', 'DIFFERENT DAY'] },
];
const inks = { white: '#ffffff', black: '#000000' };

const font = (file) => `url(data:font/woff2;base64,${fs.readFileSync(path.join(FONTS, file)).toString('base64')})`;
const ANTON = font('anton.woff2');
const ARCHIVO = font('archivo-black.woff2');

function page(d, color) {
  const lines = d.lines.map((l) => `<div>${l}</div>`).join('');
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    @font-face{font-family:'Anton';src:${ANTON}}
    @font-face{font-family:'Archivo Black';src:${ARCHIVO}}
    html,body{margin:0;background:transparent}
    #art{display:inline-block;padding:8px;font-family:'${d.font}';font-size:${d.size}px;line-height:${d.lh};
      letter-spacing:${d.ls};color:${color};text-align:center;white-space:nowrap;-webkit-font-smoothing:none}
  </style></head><body><div id="art">${lines}</div></body></html>`;
}

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ deviceScaleFactor: 2, viewport: { width: 2400, height: 1200 } });
  const p = await ctx.newPage();
  for (const d of designs) {
    for (const [ink, color] of Object.entries(inks)) {
      await p.setContent(page(d, color), { waitUntil: 'load' });
      const ok = await p.evaluate(async (f) => { await document.fonts.load(`40px "${f}"`); return document.fonts.check(`40px "${f}"`); }, d.font);
      if (!ok) throw new Error(`${d.name}: font ${d.font} not loaded`);
      const file = `${d.name}-${ink}.png`;
      await p.locator('#art').screenshot({ path: path.join(OUT, file), omitBackground: true });
      console.log('rendered', file);
    }
  }
  await browser.close();
})();
