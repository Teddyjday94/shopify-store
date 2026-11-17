const { chromium, devices } = require('playwright');
const OUT = __dirname + '/';
const T = '156798746785';
const U = (p) => `https://elsewhereapparelco.com${p}${p.includes('?') ? '&' : '?'}preview_theme_id=${T}&nc=${Date.now()}`;
(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
  const errs = [];
  p.on('pageerror', (e) => errs.push(e.message));
  const t0 = Date.now();
  const res = await p.goto(U('/pages/designs'), { waitUntil: 'load', timeout: 90000 });
  console.log('status', res.status(), 'load ms', Date.now() - t0);
  const liquidErr = await p.evaluate(() => (document.body.innerText.match(/Liquid (syntax )?error[^\n]*/gi) || []).slice(0, 5));
  console.log('liquid errors', liquidErr);
  const groups = await p.$$eval('[data-design-group]', (g) => g.map((x) => x.querySelector('h2').textContent.trim() + ': ' + x.querySelectorAll('.mw-design').length));
  console.log('groups', groups);
  const cards = await p.$$eval('.mw-design', (c) => c.map((x) => x.querySelector('.mw-design__name').textContent.trim() + ' [' + [...x.querySelectorAll('.mw-pill')].map((y) => y.textContent.replace(/\s+/g, ' ').trim()).join(', ') + ']'));
  console.log('total designs', cards.length);
  console.log(cards.join('\n'));
  const names = cards.map((c) => c.split(' [')[0]);
  console.log('duplicates', names.filter((n, i) => names.indexOf(n) !== i));
  await p.screenshot({ path: OUT + 'd-top.png' });
  await p.click('.mw-chip[data-kind="hoodie"]'); await p.waitForTimeout(400);
  console.log('hoodie filter visible', await p.$$eval('.mw-design:not([hidden])', (c) => c.length), await p.textContent('[data-designs-status]'));
  await p.screenshot({ path: OUT + 'd-hoodies.png' });
  await p.click('.mw-chip[data-kind="extras"]'); await p.waitForTimeout(400);
  console.log('extras visible', await p.$$eval('.mw-design:not([hidden]) .mw-design__name', (c) => c.map((x) => x.textContent.trim())));
  for (const h of ['born-ready-tee', 'born-ready-ornament', 'lantern-witch-crewneck', 'elsewhere-dreamscape-hoodie', 'currently-elsewhere-hoodie', 'no-signal-tee', 'many-worlds-cuffed-beanie']) {
    await p.goto(U('/products/' + h), { waitUntil: 'domcontentloaded', timeout: 90000 });
    const styles = await p.$$eval('.mw-style', (s) => s.map((x) => x.querySelector('.mw-style__name').textContent.trim() + (x.classList.contains('is-current') ? '*' : '') + ' ' + x.querySelector('.mw-style__price').textContent.trim()));
    console.log(h, '->', styles.join(' | ') || '(none)');
    if (h === 'elsewhere-dreamscape-hoodie') { await p.waitForTimeout(1500); await (await p.$('.product__info')).screenshot({ path: OUT + 'd-product.png' }); }
  }
  const m = await (await b.newContext(devices['iPhone 13'])).newPage();
  await m.goto(U('/pages/designs'), { waitUntil: 'load', timeout: 90000 });
  await m.evaluate(() => window.scrollTo(0, 500)); await m.waitForTimeout(1500);
  await m.screenshot({ path: OUT + 'd-phone.png' });
  console.log('errors', errs);
  await b.close();
})().catch((e) => { console.error('FAIL', e.message); process.exit(1); });
