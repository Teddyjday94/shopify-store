const { chromium, devices } = require('playwright');
const OUT = process.argv[2] || __dirname + '/';  // screenshots folder
// Usage: node theme-live-overrides/qv_test.js [screenshot dir]  (THEME = the theme copy to preview)
const THEME = '156798746785';
const base = 'https://elsewhereapparelco.com';
(async () => {
  const b = await chromium.launch();
  const errors = [];
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  p.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  p.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await p.goto(`${base}/collections/t-shirts?preview_theme_id=${THEME}`, { waitUntil: 'networkidle', timeout: 90000 });
  console.log('cards', await p.$$eval('.card', (c) => c.length), 'quick buttons', await p.$$eval('[data-quick-view]', (c) => c.length));
  const first = (await p.$$('.card'))[0];
  await first.scrollIntoViewIfNeeded(); await p.waitForTimeout(800);
  await first.screenshot({ path: OUT + 't-card.png' });

  // quick view
  await p.click('[data-quick-view] >> nth=0');
  await p.waitForSelector('[data-quick-dialog][open] .mw-quick__title', { timeout: 20000 });
  await p.waitForTimeout(700);
  console.log('qv title', await p.textContent('.mw-quick__title'), '| price', await p.textContent('[data-qv-price]'));
  const swatches = await p.$$eval('.mw-swatch', (l) => l.map((x) => x.title));
  console.log('swatches', swatches.join(', '), '| starts on', await p.textContent('.mw-swatches').then(()=>p.$eval('.mw-swatches input:checked', (i) => i.value)));
  await p.screenshot({ path: OUT + 't-qv.png' });
  const before = await p.getAttribute('[data-qv-main]', 'src');
  if (swatches.includes('Navy')) {
    await p.click('label.mw-swatch[title="Navy"]');
    await p.waitForTimeout(800);
    const after = await p.getAttribute('[data-qv-main]', 'src');
    console.log('color label', await p.textContent('[data-qv-label="0"]'), '| image changed', before !== after, '| alt', await p.getAttribute('[data-qv-main]', 'alt'));
  }
  const sizeLabels = await p.$$eval('.mw-quick__option:not(:has(.mw-swatches)) label', (l) => l.map((x) => x.textContent.trim()));
  console.log('sizes', sizeLabels.join(','));
  if (sizeLabels.includes('L')) await p.click('.mw-quick__option:not(:has(.mw-swatches)) label:text-is("L")');
  await p.screenshot({ path: OUT + 't-qv2.png' });
  await p.click('[data-qv-add]');
  await p.waitForSelector('[data-cart-drawer][open] .mw-line', { timeout: 20000 });
  await p.waitForTimeout(600);
  console.log('quick closed', !(await p.$('[data-quick-dialog][open]')), '| drawer lines', await p.$$eval('.mw-line', (l) => l.map((x) => x.querySelector('.mw-line__title').textContent + ' / ' + (x.querySelector('.mw-line__variant')?.textContent || ''))));
  console.log('header count', await p.textContent('[data-cart-count]'), '| subtotal', await p.textContent('[data-cart-subtotal]'));
  await p.screenshot({ path: OUT + 't-drawer.png' });
  // quantity +
  await p.click('.mw-line [data-line-qty] >> nth=1');
  await p.waitForTimeout(1500);
  console.log('after +: qty', await p.textContent('.mw-qty span'), '| count', await p.textContent('[data-cart-count]'), '| subtotal', await p.textContent('[data-cart-subtotal]'));
  // close with Escape, reopen via header
  await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  console.log('drawer closed', !(await p.$('[data-cart-drawer][open]')));
  await p.click('a:has([data-cart-count])');
  await p.waitForSelector('[data-cart-drawer][open]', { timeout: 5000 });
  console.log('reopened from header', true, 'url still', p.url().includes('/collections/'));
  await p.keyboard.press('Escape'); await p.waitForTimeout(500);

  // product page add
  await p.goto(`${base}/products/elsewhere-chrome-globe-tee?preview_theme_id=${THEME}`, { waitUntil: 'networkidle', timeout: 90000 });
  await p.click('[data-add-button]');
  await p.waitForSelector('[data-cart-drawer][open]', { timeout: 20000 });
  await p.waitForTimeout(600);
  console.log('product page -> drawer lines', await p.$$eval('.mw-line', (l) => l.length), '| url', p.url().split('?')[0]);
  // remove everything
  while (await p.$('.mw-line__remove')) { await p.click('.mw-line__remove >> nth=0'); await p.waitForTimeout(1500); }
  console.log('empty text', (await p.textContent('.mw-drawer__body')).trim().slice(0, 40), '| count', await p.textContent('[data-cart-count]'));
  await p.screenshot({ path: OUT + 't-empty.png' });

  // phone quick view
  const m = await (await b.newContext(devices['iPhone 13'])).newPage();
  m.on('pageerror', (e) => errors.push('m pageerror: ' + e.message));
  await m.goto(`${base}/collections/hoodies-sweatshirts?preview_theme_id=${THEME}`, { waitUntil: 'networkidle', timeout: 90000 });
  const c = (await m.$$('.card'))[0]; await c.scrollIntoViewIfNeeded(); await m.waitForTimeout(800);
  await m.screenshot({ path: OUT + 'm-grid.png' });
  await m.tap('[data-quick-view] >> nth=0');
  await m.waitForSelector('[data-quick-dialog][open] .mw-quick__title', { timeout: 20000 }); await m.waitForTimeout(800);
  await m.screenshot({ path: OUT + 'm-qv.png' });
  console.log('m starts on', await m.$eval('.mw-swatches input:checked', (i) => i.value));
  await m.tap('label.mw-swatch[title="Maroon"]'); await m.waitForTimeout(500);
  await m.tap('[data-qv-add]');
  await m.waitForSelector('[data-cart-drawer][open] .mw-line', { timeout: 20000 }); await m.waitForTimeout(2500);
  await m.screenshot({ path: OUT + 'm-drawer.png' });
  console.log('m line', await m.textContent('.mw-line__variant'), '| img', await m.getAttribute('.mw-line__media img', 'src'));
  await m.tap('.mw-line__remove'); await m.waitForTimeout(1500);
  console.log('errors', JSON.stringify(errors));
  await b.close();
})().catch((e) => { console.error('FAIL', e.message); process.exit(1); });
