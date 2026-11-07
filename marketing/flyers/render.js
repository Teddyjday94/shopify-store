// Renders the Elsewhere print flyers to PDF (print shop / home printer) and PNG (sharing).
//   node marketing/flyers/render.js
// Needs: playwright (preinstalled in cloud sessions) and qrcode (npm i qrcode).
// Edit the FLYERS list below to change copy, products, prices or QR targets.

const fs = require('fs');
const path = require('path');
const QRCode = require('qrcode');
const { chromium } = require('playwright');

const DIR = __dirname;
const OUT = path.join(DIR, 'out');
const STORE = 'https://elsewheresupplyco.myshopify.com';
const STORE_LABEL = 'elsewheresupplyco.myshopify.com';

// UTM tags let you see flyer traffic in Shopify Analytics > Sessions by UTM campaign.
const utm = (campaign) => `utm_source=flyer&utm_medium=print&utm_campaign=${campaign}`;

const CORE_PRODUCTS = [
  { img: 'currently-elsewhere-hoodie.jpg', name: 'Currently Elsewhere Hoodie', note: 'Will respond upon return.', price: 'from $45' },
  { img: 'not-ai-just-tired-tee.jpg', name: 'Not AI. Just Tired. Tee', note: 'Verified human. Low battery.', price: 'from $24' },
  { img: 'ships-in-6-7-business-days-tee.jpg', name: 'Ships in 6–7 Business Days Tee', note: 'Estimated arrival: eventually.', price: 'from $24' },
  { img: 'odysseus-layover-tee.jpg', name: 'Odysseus Layover Tee', note: 'He took 10 years. You have a layover.', price: 'from $26' },
  { img: 'seasonal-depression-world-tour-hoodie.jpg', name: 'Seasonal Depression World Tour Hoodie', note: 'Now touring. Indoors.', price: 'from $45' },
  { img: 'do-not-perceive-me-beanie.jpg', name: 'Do Not Perceive Me Beanie', note: 'Embroidered. Mildly urgent.', price: '$26' },
];

const XMAS_ALL = [
  { art: 'dear-santa-bring-bourbon', name: 'Dear Santa, Bring Bourbon' },
  { art: 'the-gift-is-me', name: 'The Gift Is Me' },
  { art: 'holly-jolly-chaos', name: 'Holly Jolly Chaos' },
  { art: 'suck-it-up-buttercup', name: 'Suck It Up Buttercup' },
  { art: 'on-the-naughty-list-again', name: 'On the Naughty List Again' },
];
const XMAS_SAFE = XMAS_ALL.slice(0, 3);

const fontFaces = `
@font-face{font-family:'Instrument Serif';src:url(assets/fonts/instrument-serif-400.woff2) format('woff2');font-weight:400}
@font-face{font-family:'Instrument Serif';src:url(assets/fonts/instrument-serif-400-italic.woff2) format('woff2');font-style:italic}
@font-face{font-family:'Inter Tight';src:url(assets/fonts/inter-tight-var.woff2) format('woff2');font-weight:100 900}
@font-face{font-family:'Plex Mono';src:url(assets/fonts/plex-mono-500.woff2) format('woff2');font-weight:500}
@font-face{font-family:'Plex Mono';src:url(assets/fonts/plex-mono-600.woff2) format('woff2');font-weight:600}`;

const baseCss = `
${fontFaces}
:root{--paper:#0C0B0E;--ink:#F1E5D1;--accent:#B83128;--tan:#D6A674;--card:#171416}
@page{size:8.5in 11in;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:8.5in;height:11in;-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:'Inter Tight',Helvetica,sans-serif;overflow:hidden}
.mono{font-family:'Plex Mono',ui-monospace,monospace;text-transform:uppercase;letter-spacing:.14em;font-size:9.5px;font-weight:500}
.serif{font-family:'Instrument Serif',Georgia,serif;font-weight:400}
.page{position:relative;width:8.5in;height:11in;padding:.5in;display:flex;flex-direction:column}
.bar{display:flex;justify-content:space-between;padding-bottom:10px;border-bottom:1.5px solid currentColor}
.qr svg{display:block;width:100%;height:100%}
`;

async function qrSvg(url, dark, light) {
  return QRCode.toString(url, { type: 'svg', margin: 0, errorCorrectionLevel: 'M', color: { dark, light } });
}

// ---------- Flyer 1: core brand, cream paper (printer-friendly) ----------
async function coreFlyer() {
  const url = `${STORE}/?${utm('brand_flyer')}`;
  const qr = await qrSvg(url, '#0C0B0E', '#F1E5D1');
  const cards = CORE_PRODUCTS.map((p) => `
    <figure class="card">
      <div class="ph"><img src="assets/products/${p.img}" alt=""></div>
      <figcaption>
        <div class="nm">${p.name}</div>
        <div class="row"><span class="note serif">${p.note}</span><span class="mono pr">${p.price}</span></div>
      </figcaption>
    </figure>`).join('');
  return `<!doctype html><html><head><meta charset="utf-8"><title>Elsewhere Brand Flyer</title><style>
${baseCss}
body{background:#F1E5D1;color:#0C0B0E}
.hero{margin-top:22px;display:flex;align-items:flex-end;justify-content:space-between;gap:20px}
h1{font-size:108px;line-height:.82;letter-spacing:-.02em}
h1 em{display:block;color:var(--accent);font-style:italic;padding-left:.55in}
.tag{max-width:2.1in;font-size:14px;line-height:1.35;font-weight:500;padding-bottom:10px}
.tag b{display:block;margin-top:8px;font-weight:500}
.grid{margin:auto 0;padding-top:22px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px 18px}
.card{display:flex;flex-direction:column;border-top:1.5px solid #0C0B0E;padding-top:8px}
.ph{height:208px;display:flex;align-items:center;justify-content:center}
.ph img{width:100%;height:100%;object-fit:contain;mix-blend-mode:multiply}
.nm{font-weight:650;font-size:12.5px;line-height:1.2;margin-top:4px;min-height:2.4em}
.row{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-top:2px}
.note{font-style:italic;font-size:14px;color:#4a3f38}
.pr{white-space:nowrap;color:var(--accent);font-weight:600}
.foot{margin-top:auto;display:grid;grid-template-columns:1.2in 1fr auto;gap:20px;align-items:center;border-top:1.5px solid #0C0B0E;padding-top:18px}
.qr{width:1.2in;height:1.2in}
.cta{font-size:34px;line-height:1}
.cta em{color:var(--accent)}
.url{margin-top:8px;font-size:11px;letter-spacing:.06em}
.side{text-align:right;line-height:1.7}
</style></head><body><div class="page">
  <div class="bar mono"><span>Elsewhere Apparel Co. / The Crossing</span><span>Reality is optional.</span></div>
  <div class="hero">
    <h1 class="serif">Currently<em>Elsewhere.</em></h1>
    <p class="tag">Clothes for people who showed up but didn't fully arrive.<b>Tees, hoodies &amp; hats with very specific feelings.</b></p>
  </div>
  <div class="grid">${cards}</div>
  <div class="foot">
    <div class="qr">${qr}</div>
    <div><div class="cta serif">Scan to shop. <em>Or don't.</em></div><div class="mono url">${STORE_LABEL}</div></div>
    <div class="mono side">Printed to order<br>Sizes S–2XL<br>Unisex &amp; women's fits</div>
  </div>
</div></body></html>`;
}

// ---------- Flyer 2: Christmas Collection, dark ----------
async function xmasFlyer(designs, campaign) {
  const url = `${STORE}/collections/the-christmas-collection?${utm(campaign)}`;
  const qr = await qrSvg(url, '#0C0B0E', '#F1E5D1');
  const big = designs.length <= 3;
  const tiles = designs.map((d) => `
    <figure class="tile"><img src="assets/art/${d.art}.webp" alt=""><figcaption class="mono">${d.name}</figcaption></figure>`).join('');
  return `<!doctype html><html><head><meta charset="utf-8"><title>Elsewhere Holiday Flyer</title><style>
${baseCss}
body{background:var(--paper);color:var(--ink)}
.bar{color:var(--tan)}
.glow{position:absolute;inset:0;background:radial-gradient(ellipse 70% 45% at 50% 55%,rgba(184,49,40,.28),transparent 70%);pointer-events:none}
h1{margin-top:26px;font-size:${big ? 104 : 96}px;line-height:.86;letter-spacing:-.02em;text-align:center}
h1 em{color:#E0483A;font-style:italic}
.sub{text-align:center;margin-top:14px;font-size:15px;line-height:1.4;color:#d9cbb4}
.tiles{position:relative;flex:1;min-height:0;margin-top:22px;display:grid;
  grid-template-columns:${big ? 'repeat(3,1fr)' : 'repeat(6,1fr)'};gap:${big ? '14px' : '10px 14px'};align-content:center}
.tile{display:flex;flex-direction:column;align-items:center;gap:8px;min-height:0}
${big ? '' : '.tile{grid-column:span 2}.tile:nth-child(4){grid-column:2/span 2}'}
.tile img{width:100%;height:${big ? '3.9in' : '2.2in'};object-fit:contain;filter:drop-shadow(0 6px 16px rgba(0,0,0,.6))}
.tile figcaption{color:var(--tan);font-size:9px;text-align:center}
.prices{position:relative;margin-top:18px;display:flex;justify-content:center;flex-wrap:wrap;gap:6px 22px;padding:12px 0;border-top:1px solid #3a2e2a;border-bottom:1px solid #3a2e2a}
.prices span b{color:var(--ink);font-weight:600}
.prices span{color:var(--tan)}
.foot{position:relative;margin-top:18px;display:grid;grid-template-columns:1.15in 1fr;gap:20px;align-items:center}
.qr{width:1.15in;height:1.15in;background:var(--ink);padding:7px;border-radius:4px}
.cta{font-size:32px;line-height:1.02}
.cta em{color:#E0483A}
.url{margin-top:8px;color:var(--tan)}
</style></head><body><div class="glow"></div><div class="page">
  <div class="bar mono"><span>Elsewhere Apparel Co.</span><span>The Christmas Collection · 2026</span></div>
  <h1 class="serif">Naughty, nice,<br><em>or elsewhere.</em></h1>
  <p class="sub">Full-color holiday art on tees, hoodies, dad hats, mugs &amp; ornaments.<br>Gifts for people who'd rather not do the whole thing.</p>
  <div class="tiles">${tiles}</div>
  <div class="prices mono">
    <span>Tees <b>$30</b></span><span>Hoodies <b>$45</b></span><span>Dad hats <b>$26</b></span><span>Mugs <b>$18</b></span><span>Ornaments <b>$15</b></span>
  </div>
  <div class="foot">
    <div class="qr">${qr}</div>
    <div><div class="cta serif">Scan for the whole collection.<br><em>Santa's not checking anyway.</em></div><div class="mono url">${STORE_LABEL} / Christmas</div></div>
  </div>
</div></body></html>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const jobs = [
    ['elsewhere-brand-flyer', await coreFlyer()],
    ['elsewhere-holiday-flyer', await xmasFlyer(XMAS_ALL, 'holiday_flyer')],
    ['elsewhere-holiday-flyer-board-safe', await xmasFlyer(XMAS_SAFE, 'holiday_flyer_safe')],
  ];
  const browser = await chromium.launch();
  for (const [name, html] of jobs) {
    const htmlPath = path.join(DIR, `${name}.html`);
    fs.writeFileSync(htmlPath, html);
    // 300 dpi PNG: 8.5in x 11in at 96 css px/in = 816x1056, scale 3.125 -> 2550x3300.
    const page = await browser.newPage({ viewport: { width: 816, height: 1056 }, deviceScaleFactor: 3.125 });
    await page.goto('file://' + htmlPath);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: path.join(OUT, `${name}.png`) });
    await page.pdf({ path: path.join(OUT, `${name}.pdf`), width: '8.5in', height: '11in', printBackground: true });
    await page.close();
    console.log('rendered', name);
  }
  await browser.close();
})();
