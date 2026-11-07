// The Immortalized Collection print files: each painting, unframed, with its title underneath (back),
// and a small chest mark (front). White type, for dark garments.
// Usage: node designs/src/render_drop4.js [slug ...]   (no slugs = render all)

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'print-drop4');
const data = (file, type) => `data:${type};base64,${fs.readFileSync(file).toString('base64')}`;
const ANTON = data(path.join(ROOT, '..', 'theme', 'assets', 'anton.woff2'), 'font/woff2');
const MONO = data(path.join(ROOT, '..', 'theme', 'assets', 'space-mono-700.woff2'), 'font/woff2');

const designs = [
  ['01-lead-the-charge', 'Lead the Charge', 'Someone has to go first.', ['Lead', 'the Charge']],
  ['02-rise-from-ruin', 'Rise From Ruin', 'Down bad. Getting up anyway.', ['Rise', 'From Ruin']],
  ['03-sleep-paralysis-club', 'Sleep Paralysis Club', 'Members only. Meetings at 3 a.m.', ['Sleep Paralysis', 'Club']],
  ['04-one-way-ferry', 'One Way Ferry', 'No return ticket required.', ['One Way', 'Ferry']],
  ['05-born-ready', 'Born Ready', 'Arrived fashionably late. On a shell.', ['Born', 'Ready']],
  ['06-fallen-not-finished', 'Fallen, Not Finished', 'Heaven can wait. So can I.', ['Fallen,', 'Not Finished']],
  ['07-above-it-all', 'Above It All', 'Physically here. Mentally up there.', ['Above', 'It All']],
  ['08-going-with-the-flow', 'Going With the Flow', 'Floating through it.', ['Going With', 'the Flow']],
  ['09-long-live-the-king', 'Long Live the King', "Crowns don't retire.", ['Long Live', 'the King']],
  ['10-queen-forever', 'Queen Forever', 'Death is no reason to dress down.', ['Queen', 'Forever']],
  ['11-nine-tails', 'Nine Tails', 'Protector or punisher. Your call.', ['Nine', 'Tails']],
  ['12-masterless', 'Masterless', 'No lord. No rush.', ['Master', 'less']],
];

const css = `
  @font-face{font-family:'Anton';src:url(${ANTON})}
  @font-face{font-family:'Space Mono';src:url(${MONO});font-weight:700}
  html,body{margin:0;background:transparent;color:#f4ecdc}
  .label{font:700 22px 'Space Mono';letter-spacing:.3em;text-transform:uppercase}
`;

function back(name, title, line) {
  const img = data(path.join(ROOT, 'drop4-src', `${name}-3x.jpg`), 'image/jpeg');
  return `<!doctype html><html><head><style>${css}
    #art{width:1346px;padding:0}
    .frame{border:0;padding:0}
    .frame img{display:block;width:100%}
    .title{font-family:'Anton';font-size:150px;line-height:1;text-transform:uppercase;letter-spacing:.01em;
      white-space:nowrap;margin-top:22px;text-align:center}
    .row{margin-top:16px;padding-top:18px;border-top:4px solid #f4ecdc;text-align:center;white-space:nowrap}
    /* Sized to stay legible on the garment and in product photos (about 2x the original 22-24px). */
    .row .label{font:700 44px 'Space Mono';letter-spacing:.16em;margin-right:-.16em;color:#fff}
    .line{font:700 36px 'Space Mono';margin-top:10px;color:#f4ecdc}
  </style></head><body><div id="art">
    <div class="frame"><img src="${img}"></div>
    <div class="title">${title}</div>
    <div class="row"><div class="label">Elsewhere Apparel Co. · Immortalized</div><div class="line">${line}</div></div>
  </div></body></html>`;
}

function front(lines) {
  return `<!doctype html><html><head><style>${css}
    #art{display:inline-block;padding:10px;text-align:left}
    .t{font-family:'Anton';font-size:120px;line-height:.9;text-transform:uppercase;white-space:nowrap}
    .label{font-size:33px;letter-spacing:.2em;margin-top:18px}
  </style></head><body><div id="art"><div class="t">${lines.join('<br>')}</div>
    <div class="label">Elsewhere / Immortalized</div></div></body></html>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1500, height: 2400 }, deviceScaleFactor: 10 / 3 })).newPage();
  const only = process.argv.slice(2);
  for (const [name, title, line, lines] of designs.filter(([n]) => !only.length || only.includes(n))) {
    for (const [file, html] of [[`${name}-back.png`, back(name, title, line)], [`${name}-front.png`, front(lines)]]) {
      await page.setContent(html, { waitUntil: 'load' });
      await page.evaluate(async () => { await document.fonts.load('40px Anton'); await document.fonts.load('700 20px "Space Mono"'); });
      await page.locator('#art').screenshot({ path: path.join(OUT, file), omitBackground: true });
      console.log('rendered', file);
    }
  }
  await browser.close();
})();
