// Christmas Collection: small chest marks (front of tees and hoodies) and embroidered dad-hat text.
// The back prints come from prep_xmas.py. White type with a red label, for black garments.
// Usage: node designs/src/render_xmas.js

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'print-xmas');
const font = (f) => `data:font/woff2;base64,${fs.readFileSync(path.join(ROOT, '..', 'theme', 'assets', f)).toString('base64')}`;

const designs = [
  ['01-on-the-naughty-list-again', ['Naughty', 'List Again'], ['NAUGHTY', 'LIST AGAIN']],
  ['02-suck-it-up-buttercup', ['Suck It Up', 'Buttercup'], ['SUCK IT UP', 'BUTTERCUP']],
  ['03-dear-santa-bring-bourbon', ['Dear Santa,', 'Bring Bourbon'], ['BRING', 'BOURBON']],
  ['04-the-gift-is-me', ['The Gift', 'Is Me'], ['THE GIFT', 'IS ME']],
  ['05-holly-jolly-chaos', ['Holly Jolly', 'Chaos'], ['HOLLY JOLLY', 'CHAOS']],
];

const head = `<style>
  @font-face{font-family:'Anton';src:url(${font('anton.woff2')})}
  @font-face{font-family:'Space Mono';src:url(${font('space-mono-700.woff2')});font-weight:700}
  html,body{margin:0;background:transparent}
</style>`;

const front = (lines) => `<!doctype html><html><head>${head}<style>
  #art{display:inline-block;padding:10px;color:#f6efe2}
  .t{font-family:'Anton';font-size:120px;line-height:.92;text-transform:uppercase;white-space:nowrap}
  .l{font:700 30px 'Space Mono';letter-spacing:.3em;margin-top:16px;color:#d4232b}
</style></head><body><div id="art"><div class="t">${lines.join('<br>')}</div><div class="l">ELSEWHERE / CHRISTMAS</div></div></body></html>`;

const hat = (lines) => `<!doctype html><html><head>${head}<style>
  #art{display:inline-block;padding:8px;font-family:'Anton';font-size:190px;line-height:1;letter-spacing:.03em;
    color:#fff;text-align:center;white-space:nowrap;-webkit-font-smoothing:none}
</style></head><body><div id="art">${lines.map((l) => `<div>${l}</div>`).join('')}</div></body></html>`;

(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 2400, height: 1400 }, deviceScaleFactor: 2.5 })).newPage();
  for (const [name, chest, cap] of designs) {
    for (const [file, html] of [[`${name}-front.png`, front(chest)], [`${name}-hat.png`, hat(cap)]]) {
      await page.setContent(html, { waitUntil: 'load' });
      await page.evaluate(async () => { await document.fonts.load('40px Anton'); await document.fonts.load('700 20px "Space Mono"'); });
      await page.locator('#art').screenshot({ path: path.join(OUT, file), omitBackground: true });
      console.log('rendered', file);
    }
  }
  await browser.close();
})();
