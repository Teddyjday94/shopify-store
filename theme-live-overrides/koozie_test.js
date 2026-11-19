// Usage: node theme-live-overrides/koozie_test.js [screenshot dir]   Checks the koozie price table + cart nudge in a theme copy.
const { chromium } = require('playwright');
const OUT = process.argv[2] || __dirname + '/';
const THEME = '156906258593';
const base = 'https://elsewhereapparelco.com';
(async () => {
  const b = await chromium.launch();
  const errors = [];
  const p = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
  p.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  await p.goto(`${base}/products/whadid-i-do-koozie?preview_theme_id=${THEME}`, { waitUntil: 'networkidle', timeout: 90000 });
  console.log('deal table', await p.$$eval('.mw-deal__tiers li', (l) => l.map((x) => x.textContent.replace(/\s+/g, ' ').trim()).join(' | ')));
  await p.$eval('.mw-deal', (e) => e.scrollIntoView({ block: 'center' })); await p.waitForTimeout(500);
  await p.screenshot({ path: OUT + 'k-product.png' });
  const add = async (qty) => {
    await p.evaluate(async (q) => { await fetch('/cart/add.js', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ items: [{ id: 49124106862753, quantity: q }] }) }); }, qty);
  };
  for (const [q, name] of [[1, 'k-cart1'], [2, 'k-cart3'], [3, 'k-cart6']]) {
    await add(q);
    await p.goto(`${base}/products/whadid-i-do-koozie?preview_theme_id=${THEME}`, { waitUntil: 'networkidle', timeout: 90000 });
    await p.click('[data-cart-open], a[href="/cart"] >> nth=0').catch(() => {});
    await p.waitForSelector('[data-cart-drawer][open]', { timeout: 15000 }).catch(() => {});
    await p.waitForTimeout(800);
    const n = await p.$eval('[data-koozie-nudge]', (e) => (e.hidden ? '(hidden)' : e.textContent.trim())).catch(() => 'none');
    const disc = await p.$eval('[data-cart-discount]', (e) => e.textContent).catch(() => '');
    const sub = await p.$eval('[data-cart-subtotal]', (e) => e.textContent).catch(() => '');
    console.log(`cart ${q === 1 ? 1 : q === 2 ? 3 : 6}: nudge="${n}" discount=${disc} subtotal=${sub}`);
    await p.screenshot({ path: OUT + name + '.png' });
  }
  console.log('errors', errors.length ? errors : 'none');
  await b.close();
})();
