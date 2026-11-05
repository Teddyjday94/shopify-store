// Home & accessories print files: wraparound mugs and round ornaments.
// Christmas art keeps its black background and fills the whole printed area, so the mug or ornament
// reads as black with the painting on it (no box). Slogan mugs are black type on the white mug, both sides.
// Usage: node designs/src/render_home.js

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'print-home');
const data = (file, type) => `data:${type};base64,${fs.readFileSync(file).toString('base64')}`;
const ANTON = data(path.join(ROOT, '..', 'theme', 'assets', 'anton.woff2'), 'font/woff2');
const MONO = data(path.join(ROOT, '..', 'theme', 'assets', 'space-mono-700.woff2'), 'font/woff2');

const XMAS = ['01-on-the-naughty-list-again', '02-suck-it-up-buttercup', '03-dear-santa-bring-bourbon',
  '04-the-gift-is-me', '05-holly-jolly-chaos'];
const SLOGANS = [
  ['21-not-ai-just-tired', ['NOT AI.', 'JUST TIRED.']],
  ['22-same-chaos-different-day', ['SAME CHAOS', 'DIFFERENT DAY']],
  ['23-do-not-perceive-me', ['DO NOT', 'PERCEIVE ME']],
  ['24-currently-elsewhere', ['CURRENTLY', 'ELSEWHERE']],
];
// Mug wrap print area is 2475 x 1155 at 300 dpi; render at 2x.
const MUG_W = 4950, MUG_H = 2310;

const head = `<style>
  @font-face{font-family:'Anton';src:url(${ANTON})}
  @font-face{font-family:'Space Mono';src:url(${MONO});font-weight:700}
  html,body{margin:0;background:transparent}
</style>`;

const xmasMug = (img) => `<!doctype html><html><head>${head}<style>
  #art{width:${MUG_W}px;height:${MUG_H}px;background:#000;display:flex;justify-content:space-around;align-items:center}
  #art img{height:${MUG_H - 60}px}
</style></head><body><div id="art"><img src="${img}"><img src="${img}"></div></body></html>`;

// Circle ornament: the whole art fits inside the circle, on black.
const xmasOrnament = (img) => `<!doctype html><html><head>${head}<style>
  #art{width:2400px;height:2400px;background:#000;display:flex;justify-content:center;align-items:center}
  #art img{width:1560px}
</style></head><body><div id="art"><img src="${img}"></div></body></html>`;

const sloganMug = (lines) => {
  const side = `<div class="side"><div class="t">${lines.join('<br>')}</div><div class="l">MANY WORLDS SUPPLY CO.</div></div>`;
  return `<!doctype html><html><head>${head}<style>
  #art{width:${MUG_W}px;height:${MUG_H}px;display:flex;justify-content:space-around;align-items:center;color:#111}
  .side{width:42%;text-align:center}
  .t{font-family:'Anton';font-size:380px;line-height:.95;white-space:nowrap}
  .l{font:700 64px 'Space Mono';letter-spacing:.3em;margin-top:60px}
</style></head><body><div id="art">${side}${side}</div></body></html>`;
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 5000, height: 2500 } })).newPage();
  const shot = async (html, file) => {
    await page.setContent(html, { waitUntil: 'load' });
    await page.evaluate(async () => { await document.fonts.load('40px Anton'); await document.fonts.load('700 20px "Space Mono"'); });
    await page.locator('#art').screenshot({ path: path.join(OUT, file), omitBackground: true });
    console.log('rendered', file);
  };
  for (const name of XMAS) {
    const img = data(path.join(ROOT, 'xmas-src', `${name}.png`), 'image/png');
    await shot(xmasMug(img), `${name}-mug.png`);
    await shot(xmasOrnament(img), `${name}-ornament.png`);
  }
  for (const [name, lines] of SLOGANS) await shot(sloganMug(lines), `${name}-mug.png`);
  await browser.close();
})();
