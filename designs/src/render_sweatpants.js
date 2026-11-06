// Renders the left-leg print for the collection sweatpants: "ELSEWHERE" running down the thigh,
// with the collection name and a colored rule beside it. One file per ink (white for dark pants,
// black for light ones) to designs/print-pants/<slug>-<ink>.png.
// Usage: node designs/src/render_sweatpants.js

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const OUT = path.join(__dirname, '..', 'print-pants');
const font = (file) => `url(data:font/woff2;base64,${fs.readFileSync(file).toString('base64')})`;
const ANTON = font(path.join(__dirname, '..', '..', 'theme', 'assets', 'anton.woff2'));
const MONO = font(path.join(__dirname, '..', '..', 'theme', 'assets', 'space-mono-700.woff2'));

const designs = [
  ['core', 'APPAREL CO.', null],
  ['relatable', 'RELATABLE COLLECTION', '#ff6a2b'],
  ['own-lane', 'OWN LANE', '#ff3ea5'],
  ['immortalized', 'IMMORTALIZED', '#c8302a'],
  ['christmas', 'CHRISTMAS COLLECTION', '#d4a64a'],
];
const inks = { white: '#ffffff', black: '#111111' };

function page(sub, accent, ink) {
  const rule = accent || ink;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    @font-face{font-family:'Anton';src:${ANTON}}
    @font-face{font-family:'Space Mono';src:${MONO};font-weight:700}
    html,body{margin:0;background:transparent}
    #art{display:inline-flex;align-items:center;gap:40px;padding:20px 30px;color:${ink}}
    .word{font-family:'Anton';font-size:520px;line-height:.86;letter-spacing:.04em;white-space:nowrap}
    .side{display:flex;flex-direction:column;gap:24px}
    .rule{height:14px;width:100%;background:${rule}}
    .sub{font:700 74px 'Space Mono';letter-spacing:.22em;white-space:nowrap}
  </style></head><body><div id="art">
    <div class="word">ELSEWHERE</div>
    <div class="side"><div class="rule"></div><div class="sub">${sub}</div><div class="rule"></div></div>
  </div></body></html>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page_ = await browser.newPage({ viewport: { width: 6000, height: 1000 }, deviceScaleFactor: 3 });
  for (const [slug, sub, accent] of designs) {
    for (const [name, ink] of Object.entries(inks)) {
      await page_.setContent(page(sub, accent, ink));
      await page_.evaluate(async () => { await document.fonts.load('40px Anton'); await document.fonts.load('700 20px "Space Mono"'); });
      const file = path.join(OUT, `${slug}-${name}-h.png`);
      await page_.locator('#art').screenshot({ path: file, omitBackground: true });
      console.log(file);
    }
  }
  await browser.close();
})();
