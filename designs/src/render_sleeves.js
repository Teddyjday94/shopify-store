// Sleeve lettering for the sleeve test drop: one tall PNG per sleeve (transparent, white-ish ink for black
// garments). Rendered horizontally, then rotated 90deg so it reads down the sleeve from shoulder to cuff.
// Canvas matches SwiftPOD's hoodie sleeve area (1181 x 4724 px); long sleeves reuse it scaled.
// Usage: node designs/src/render_sleeves.js
const fs = require('fs'); const path = require('path'); const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..', '..');
const font = (p) => `data:font/woff2;base64,${fs.readFileSync(path.join(ROOT, p)).toString('base64')}`;
const FACES = `
  @font-face{font-family:Anton;src:url(${font('theme/assets/anton.woff2')})}
  @font-face{font-family:Graduate;src:url(${font('designs/src/fonts/graduate-400.woff2')})}
  @font-face{font-family:Orbitron;src:url(${font('designs/src/fonts/orbitron-900.woff2')});font-weight:900}`;
const W = 4724, H = 1181; // horizontal canvas; rotated to 1181 x 4724
const STYLES = {
  legends: `font-family:Anton;color:#F1E5D1;letter-spacing:.04em;`,
  horror: `font-family:Graduate;color:#F1E5D1;-webkit-text-stroke:14px #B3261E;paint-order:stroke fill;letter-spacing:.03em;`,
  signal: `font-family:Orbitron;font-weight:900;font-style:italic;color:#F4F4F4;letter-spacing:.06em;`,
};
const SLEEVES = [
  ['rise-from-ruin-left', 'legends', 'RISE FROM RUIN'],
  ['rise-from-ruin-right', 'legends', 'LEGENDS NEVER DIE'],
  ['horror-club-left', 'horror', 'HORROR CLUB'],
  ['horror-club-right', 'horror', 'CREATURE FEATURE'],
  ['no-signal-left', 'signal', 'NO SIGNAL'],
  ['no-signal-right', 'signal', 'IN THIS UNIVERSE'],
];
(async () => {
  const out = path.join(ROOT, 'designs', 'sleeves'); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
  for (const [name, style, text] of SLEEVES) {
    await p.setContent(`<html><head><style>${FACES} html,body{margin:0;background:transparent}
      #c{width:${W}px;height:${H}px;display:flex;align-items:center;justify-content:center}
      #t{${STYLES[style]}white-space:nowrap;line-height:1}</style></head>
      <body><div id=c><span id=t>${text}</span></div></body></html>`);
    await p.evaluate(async () => { await document.fonts.ready; });
    // Fit: as large as possible within 92% of the length and 70% of the width.
    await p.evaluate(({ W, H }) => {
      const t = document.getElementById('t'); let s = 400; t.style.fontSize = s + 'px';
      const r = t.getBoundingClientRect(); s = Math.min(s * (W * 0.92) / r.width, s * (H * 0.7) / r.height);
      t.style.fontSize = s + 'px';
    }, { W, H });
    const file = path.join(out, `${name}-h.png`);
    await p.screenshot({ path: file, omitBackground: true });
    console.log('rendered', name);
  }
  await b.close();
})();
