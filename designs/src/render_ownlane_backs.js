// Renders the Own Lane back-of-garment text designs (name + script tagline) to designs/print-back/,
// one file per text color: white for dark garments, black for light ones. The tagline is always pink.
// Also renders a compact strip (*-strip-<ink>.png): the name on one line with the tagline under it, no
// header or footer, sized to sit under the art on a back-only hoodie.
// Usage: node designs/src/render_ownlane_backs.js

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const OUT = path.join(__dirname, '..', 'print-back');
const font = (file) => `url(data:font/woff2;base64,${fs.readFileSync(file).toString('base64')})`;
const ANTON = font(path.join(__dirname, '..', '..', 'theme', 'assets', 'anton.woff2'));
const MONO = font(path.join(__dirname, '..', '..', 'theme', 'assets', 'space-mono-700.woff2'));
const SCRIPT = font(path.join(__dirname, '..', 'web', 'yellowtail.woff2'));
const PINK = '#ff3ea5';

const designs = [
  ['01-in-my-own-lane', ['IN MY', 'OWN LANE'], 'Staying in it.'],
  ['02-butterfly-effect', ['BUTTERFLY', 'EFFECT'], 'Small moves. Big energy.'],
  ['03-lucky-charm', ['LUCKY', 'CHARM'], 'Made my own luck.'],
  ['04-sunflower-soul', ['SUNFLOWER', 'SOUL'], 'Always growing.'],
  ['05-color-me-bold', ['COLOR ME', 'BOLD'], 'Bold looks good on you.'],
  ['06-crown-and-curls', ['CROWN', '&amp; CURLS'], 'Wear the crown.'],
  ['07-pink-crown', ['PINK', 'CROWN'], 'Crowned by me.'],
  ['08-sisterhood', ['SISTER', 'HOOD'], 'Better together.'],
];
const inks = { white: '#ffffff', black: '#111111' };

function page(lines, tagline, ink) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    @font-face{font-family:'Anton';src:${ANTON}}
    @font-face{font-family:'Space Mono';src:${MONO};font-weight:700}
    @font-face{font-family:'Yellowtail';src:${SCRIPT}}
    html,body{margin:0;background:transparent}
    #art{display:inline-flex;flex-direction:column;align-items:center;padding:30px 40px;color:${ink};text-align:center}
    .label{font:700 46px 'Space Mono';letter-spacing:.32em;margin-right:-.32em}
    .rule{width:100%;height:6px;background:${ink};margin:26px 0 10px}
    .name{font-family:'Anton';font-size:330px;line-height:.9;text-transform:uppercase;white-space:nowrap;letter-spacing:.01em}
    .tag{font-family:'Yellowtail';font-size:170px;color:${PINK};transform:rotate(-6deg);margin:-36px 0 0;white-space:nowrap;
      text-shadow:0 0 0 ${PINK}}
    .foot{margin-top:40px}
  </style></head><body><div id="art">
    <div class="label">MANY WORLDS SUPPLY CO.</div><div class="rule"></div>
    <div class="name">${lines.join('<br>')}</div>
    <div class="tag">${tagline}</div>
    <div class="rule"></div><div class="label foot">OWN LANE &middot; 2026</div>
  </div></body></html>`;
}

function strip(lines, tagline, ink) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    @font-face{font-family:'Anton';src:${ANTON}}
    @font-face{font-family:'Yellowtail';src:${SCRIPT}}
    html,body{margin:0;background:transparent}
    #art{display:inline-flex;flex-direction:column;align-items:center;padding:20px 40px 40px;color:${ink};text-align:center}
    .name{font-family:'Anton';font-size:300px;line-height:1;text-transform:uppercase;white-space:nowrap;letter-spacing:.02em}
    .tag{font-family:'Yellowtail';font-size:150px;color:${PINK};transform:rotate(-4deg);margin:-30px 0 0;white-space:nowrap}
  </style></head><body><div id="art">
    <div class="name">${lines.join(' ')}</div>
    <div class="tag">${tagline}</div>
  </div></body></html>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const p = await (await browser.newContext({ viewport: { width: 4000, height: 2600 }, deviceScaleFactor: 2.5 })).newPage();
  for (const [name, lines, tagline] of designs) {
    for (const [ink, color] of Object.entries(inks)) {
      await p.setContent(page(lines, tagline, color), { waitUntil: 'load' });
      await p.evaluate(async () => {
        await Promise.all(['40px Anton', '700 40px "Space Mono"', '40px Yellowtail'].map((f) => document.fonts.load(f)));
      });
      const file = `${name}-back-${ink}.png`;
      await p.locator('#art').screenshot({ path: path.join(OUT, file), omitBackground: true });
      console.log('rendered', file);
      await p.setContent(strip(lines, tagline, color), { waitUntil: 'load' });
      await p.evaluate(async () => {
        await Promise.all(['40px Anton', '40px Yellowtail'].map((f) => document.fonts.load(f)));
      });
      const stripFile = `${name}-strip-${ink}.png`;
      await p.locator('#art').screenshot({ path: path.join(OUT, stripFile), omitBackground: true });
      console.log('rendered', stripFile);
    }
  }
  await browser.close();
})();
