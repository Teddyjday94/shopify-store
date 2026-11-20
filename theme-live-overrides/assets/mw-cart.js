// Elsewhere Apparel Co.: slide-out cart and product quick view (2026-11-17).
// Markup lives in snippets/cart-drawer.liquid; styles in assets/mw-cart.css.
// Uses Shopify's Ajax Cart API (/cart.js, /cart/add.js, /cart/change.js) and /products/<handle>.js.
(() => {
  const cfg = window.mwCart;
  const drawer = document.querySelector('[data-cart-drawer]');
  const quick = document.querySelector('[data-quick-dialog]');
  if (!cfg || !drawer || !quick || typeof drawer.showModal !== 'function') return;

  const S = cfg.strings;
  const root = cfg.root.endsWith('/') ? cfg.root : cfg.root + '/';
  const onCartPage = location.pathname.replace(/\/$/, '') === cfg.cartUrl.replace(/\/$/, '');
  let cart = cfg.cart;

  // ---------- helpers ----------
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  function money(cents) {
    const fmt = cfg.moneyFormat || '${{amount}}';
    const value = (Number(cents) || 0) / 100;
    const group = (n, dec, thou, sep) => {
      const [whole, frac] = n.toFixed(dec).split('.');
      return whole.replace(/\B(?=(\d{3})+(?!\d))/g, thou) + (frac ? sep + frac : '');
    };
    return fmt.replace(/\{\{\s*(\w+)\s*\}\}/, (_, key) => ({
      amount: group(value, 2, ',', '.'),
      amount_no_decimals: group(value, 0, ',', '.'),
      amount_with_comma_separator: group(value, 2, '.', ','),
      amount_no_decimals_with_comma_separator: group(value, 0, '.', ','),
      amount_with_apostrophe_separator: group(value, 2, "'", '.'),
    }[key] ?? group(value, 2, ',', '.')));
  }

  function sized(url, width) {
    if (!url) return '';
    const u = url.startsWith('//') ? 'https:' + url : url;
    return u + (u.includes('?') ? '&' : '?') + 'width=' + width;
  }

  async function api(path, body) {
    const opts = body
      ? { method: 'POST', headers: { Accept: 'application/json', ...(body instanceof FormData ? {} : { 'Content-Type': 'application/json' }) },
          body: body instanceof FormData ? body : JSON.stringify(body) }
      : { headers: { Accept: 'application/json' } };
    const res = await fetch(root + path, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.description || data.message || S.error);
    return data;
  }

  // Product data by handle (quick view, and the drawer's per-color photos). Photos labeled
  // "<Title> in <Color>, <detail>" belong to that color.
  const products = new Map();  // handle -> Promise<product>
  const loaded = new Map();    // handle -> product, once it has arrived
  const LABEL = /^.* in ([^,]+), (.+)$/i;
  function loadProduct(handle) {
    if (!products.has(handle)) {
      const p = api(`products/${encodeURIComponent(handle)}.js`);
      p.then((data) => loaded.set(handle, data), () => products.delete(handle));
      products.set(handle, p);
    }
    return products.get(handle);
  }
  function colorPhoto(product, color) {
    if (!product || !color) return null;
    const hit = (product.media || []).find((m) => m.media_type === 'image'
      && ((LABEL.exec(m.alt || '') || [])[1] || '').toLowerCase() === color.toLowerCase());
    return hit ? (hit.src || hit.preview_image?.src) : null;
  }

  let lastFocus = null;
  function openDialog(dialog) {
    if (dialog.open) return;
    lastFocus = document.activeElement;
    document.documentElement.classList.add('mw-modal-open');
    dialog.showModal();
    requestAnimationFrame(() => dialog.classList.add('is-open'));
  }
  function closeDialog(dialog) {
    if (!dialog.open) return;
    dialog.classList.remove('is-open');
    const done = () => {
      dialog.close();
      if (!drawer.open && !quick.open) document.documentElement.classList.remove('mw-modal-open');
      if (lastFocus && document.contains(lastFocus)) lastFocus.focus({ preventScroll: true });
    };
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) done();
    else setTimeout(done, 260);
  }
  [drawer, quick].forEach((dialog) => {
    dialog.addEventListener('cancel', (e) => { e.preventDefault(); closeDialog(dialog); });
    dialog.addEventListener('click', (e) => { if (e.target === dialog) closeDialog(dialog); });  // backdrop
  });

  // ---------- cart drawer ----------
  const itemsEl = drawer.querySelector('[data-cart-items]');
  const footEl = drawer.querySelector('[data-cart-foot]');
  const statusEl = drawer.querySelector('[data-cart-status]');

  function updateCounts() {
    document.querySelectorAll('[data-cart-count]').forEach((el) => {
      el.textContent = cart.item_count;
      const link = el.closest('a');
      if (link) link.setAttribute('aria-label', link.textContent.replace(/\d+\s*$/, '').trim() + ', ' + cart.item_count);
    });
    drawer.querySelector('[data-cart-drawer-count]').textContent = cart.item_count ? `(${cart.item_count})` : '';
  }

  // Variants of colors added later have no photo of their own, so cart.js falls back to the product's
  // main photo (often another color). Show the line's own color photo instead once the product is loaded.
  function lineColor(item) {
    const opt = (item.options_with_values || []).find((o) => /colou?r/i.test(o.name));
    return opt ? opt.value : null;
  }
  function lineImage(item) {
    if (item.variant_id && item.featured_image && item.featured_image.variant_ids?.includes(item.variant_id)) return item.image;
    return colorPhoto(loaded.get(item.handle), lineColor(item)) || item.image;
  }
  function loadLinePhotos() {
    const missing = cart.items.filter((i) => lineColor(i) && !loaded.has(i.handle)).map((i) => loadProduct(i.handle).catch(() => null));
    if (missing.length) Promise.all(missing).then(() => { if (drawer.open) renderCart(); });
  }

  function renderShipBar() {
    const bar = drawer.querySelector('[data-ship-bar]');
    if (!bar) return;
    const goal = parseInt(bar.dataset.threshold, 10) || 0;
    if (!goal || !cart.item_count || (cart.currency && cart.currency !== 'USD')) { bar.hidden = true; return; }
    bar.hidden = false;
    const left = goal - cart.total_price;
    bar.classList.toggle('is-done', left <= 0);
    bar.querySelector('[data-ship-text]').innerHTML = left > 0
      ? `You're <strong>${money(left)}</strong> away from free US shipping`
      : '<strong>Free US shipping</strong> unlocked &mdash; applied at checkout';
    bar.querySelector('[data-ship-fill]').style.width = Math.min(100, (cart.total_price / goal) * 100) + '%';
  }

  // Koozie multi-buy nudge: counts koozies in the cart and says how many more reach the next price.
  function renderKoozieNudge() {
    const el = drawer.querySelector('[data-koozie-nudge]');
    if (!el) return;
    const n = cart.items.filter((i) => /koozie/i.test(i.handle)).reduce((t, i) => t + i.quantity, 0);
    const tiers = (el.dataset.koozieTiers || '').split(',').map((t) => t.split(':').map(Number)).filter((t) => t[0]);
    if (!n || !tiers.length) { el.hidden = true; return; }
    const next = tiers.find((t) => t[0] > n);
    const link = `<a href="${el.dataset.koozieUrl}">Shop koozies</a>`;
    if (next) {
      const more = next[0] - n;
      el.innerHTML = `Add <strong>${more} more koozie${more > 1 ? 's' : ''}</strong> and they're all <strong>${money(next[1])} each</strong>. ${link}`;
      el.classList.remove('is-done');
    } else {
      el.innerHTML = `<strong>Best koozie price unlocked:</strong> ${money(tiers[tiers.length - 1][1])} each, applied at checkout`;
      el.classList.add('is-done');
    }
    el.hidden = false;
  }

  function renderCart() {
    updateCounts();
    renderShipBar();
    renderKoozieNudge();
    loadLinePhotos();
    if (!cart.item_count) {
      itemsEl.innerHTML = `<div class="mw-drawer__empty"><p class="mw-drawer__empty-title">${esc(S.empty)}</p>
        <a class="btn" href="${esc(S.shopUrl)}">${esc(S.continueShopping)} &rarr;</a></div>`;
      footEl.hidden = true;
      return;
    }
    footEl.hidden = false;
    itemsEl.innerHTML = `<ul class="mw-lines">${cart.items.map((item) => {
      const variant = item.variant_title && !/default title/i.test(item.variant_title) ? item.variant_title : '';
      const was = item.original_line_price > item.final_line_price ? `<s>${money(item.original_line_price)}</s> ` : '';
      return `<li class="mw-line" data-key="${esc(item.key)}">
        <a class="mw-line__media" href="${esc(item.url)}" tabindex="-1" aria-hidden="true">
          ${lineImage(item) ? `<img src="${esc(sized(lineImage(item), 200))}" alt="" loading="lazy" width="100" height="100">` : ''}
        </a>
        <div class="mw-line__info">
          <a class="mw-line__title" href="${esc(item.url)}">${esc(item.product_title)}</a>
          ${variant ? `<p class="mw-line__variant fg-meta">${esc(variant)}</p>` : ''}
          <div class="mw-line__row">
            <div class="mw-qty" role="group" aria-label="${esc(S.quantity)}, ${esc(item.product_title)}">
              <button type="button" data-line-qty="${item.quantity - 1}" aria-label="${esc(S.decrease)}">&minus;</button>
              <span aria-live="polite">${item.quantity}</span>
              <button type="button" data-line-qty="${item.quantity + 1}" aria-label="${esc(S.increase)}">+</button>
            </div>
            <button class="mw-line__remove fg-meta" type="button" data-line-qty="0">${esc(S.remove)}</button>
          </div>
        </div>
        <p class="mw-line__price">${was}${money(item.final_line_price)}</p>
      </li>`;
    }).join('')}</ul>`;
    const discount = cart.total_discount || 0;
    const discountRow = drawer.querySelector('[data-cart-discount-row]');
    discountRow.hidden = !discount;
    drawer.querySelector('[data-cart-discount]').textContent = discount ? '−' + money(discount) : '';
    drawer.querySelector('[data-cart-subtotal]').textContent = money(cart.total_price);
  }

  async function refreshCart() {
    cart = await api('cart.js');
    renderCart();
    return cart;
  }

  itemsEl.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-line-qty]');
    if (!btn) return;
    const line = btn.closest('[data-key]');
    line.classList.add('is-busy');
    itemsEl.querySelectorAll('button').forEach((b) => { b.disabled = true; });
    try {
      cart = await api('cart/change.js', { id: line.dataset.key, quantity: Number(btn.dataset.lineQty) });
      renderCart();
      statusEl.textContent = '';
      const keep = itemsEl.querySelector(`[data-key="${CSS.escape(line.dataset.key)}"] [data-line-qty]`);
      (keep || drawer.querySelector('[data-cart-close]')).focus({ preventScroll: true });
    } catch (err) {
      statusEl.textContent = err.message;
      renderCart();
    }
  });

  drawer.querySelector('[data-cart-close]').addEventListener('click', () => closeDialog(drawer));

  function openCart() {
    renderCart();
    if (quick.open) { quick.classList.remove('is-open'); quick.close(); }
    openDialog(drawer);
    drawer.querySelector('[data-cart-close]').focus({ preventScroll: true });
  }
  window.mwOpenCart = openCart;

  // Header cart link opens the drawer (still a real link to /cart without JavaScript, and on the cart page).
  document.addEventListener('click', (e) => {
    if (onCartPage || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const link = e.target.closest('a[href]');
    if (!link || !link.querySelector('[data-cart-count]')) return;
    e.preventDefault();
    openCart();
    refreshCart().catch(() => {});
  });

  // Every add-to-cart form (product page, quick view) adds in place and opens the drawer.
  document.addEventListener('submit', async (e) => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement) || !/\/cart\/add\/?$/.test(new URL(form.action, location.href).pathname)) return;
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    const errorEl = form.querySelector('[data-form-error]');
    const label = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = S.adding; btn.setAttribute('aria-busy', 'true'); }
    if (errorEl) { errorEl.hidden = true; errorEl.textContent = ''; }
    try {
      // Hoodie page "Complete the set": when "yes" is ticked, add the hoodie and the chosen sweatpants together.
      // getAttribute: the product form has an input named "id", which shadows form.id.
      const formId = form.getAttribute('id');
      const addon = formId && document.querySelector(`[data-set-addon][data-for="${formId}"]`);
      const pantsId = addon && addon.querySelector('[data-set-yes]').checked ? addon.dataset.pantsVariant : '';
      if (pantsId) {
        const fd = new FormData(form);
        await api('cart/add.js', { items: [
          { id: Number(fd.get('id')), quantity: Number(fd.get('quantity') || 1) },
          { id: Number(pantsId), quantity: 1 }
        ] });
      } else {
        await api('cart/add.js', new FormData(form));
      }
      await refreshCart();
      statusEl.textContent = S.added;
      if (onCartPage) { location.reload(); return; }
      openCart();
    } catch (err) {
      if (errorEl) { errorEl.textContent = err.message; errorEl.hidden = false; }
      else alert(err.message);
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = label; btn.removeAttribute('aria-busy'); }
    }
  });

  // Back/forward cache can show a stale count; re-sync when the page is shown again.
  addEventListener('pageshow', (e) => { if (e.persisted) refreshCart().catch(() => {}); });

  // ---------- quick view ----------
  const body = quick.querySelector('[data-quick-body]');
  const SWATCH = {
    'black': '#121113', 'white': '#f4f2ee', 'navy': '#1f2742', 'dark grey heather': '#4b4a50', 'dark heather': '#414249',
    'charcoal': '#3d3e42', 'maroon': '#5a1b26', 'forest': '#1f3a2c', 'forest green': '#22402f', 'military green': '#4e5530',
    'dark chocolate': '#3b2820', 'purple': '#4f3480', 'light pink': '#f2c9d2', 'sport grey': '#a3a5a8', 'sand': '#d9c8a5',
    'light blue': '#a8c5e2', 'gold': '#e2a62a', 'red': '#a3262a', 'royal': '#2a4aa0', 'heather grey': '#a7a6a9', 'ash': '#d4d3cf',
  };

  // Warm the product data when a shopper points at or focuses a quick view button.
  ['pointerenter', 'focusin'].forEach((type) => document.addEventListener(type, (e) => {
    const btn = e.target instanceof Element && e.target.closest('[data-quick-view]');
    if (btn) loadProduct(btn.dataset.quickView).catch(() => {});
  }, true));

  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-quick-view]');
    if (!btn) return;
    e.preventDefault();
    body.innerHTML = '<div class="mw-quick__loading fg-meta">Loading…</div>';
    openDialog(quick);
    quick.querySelector('[data-quick-close]').focus({ preventScroll: true });
    try {
      renderQuick(await loadProduct(btn.dataset.quickView), btn.dataset.quickUrl);
    } catch (err) {
      body.innerHTML = `<p class="mw-quick__loading">${esc(S.error)}</p>`;
    }
  });
  quick.querySelector('[data-quick-close]').addEventListener('click', () => closeDialog(quick));

  function renderQuick(product, url) {
    const options = product.options.map((o) => (typeof o === 'string' ? { name: o } : o));
    const colorIndex = options.findIndex((o) => /colou?r/i.test(o.name));
    const images = (product.media || []).filter((m) => m.media_type === 'image')
      .map((m) => ({ src: m.src || m.preview_image?.src, alt: m.alt || '', color: (LABEL.exec(m.alt || '') || [])[1] || null }));
    const mainColor = (LABEL.exec((images[0] || {}).alt || '') || [])[1];
    let variant = (colorIndex >= 0 && mainColor && product.variants.find((v) => v.available
        && v.options[colorIndex].toLowerCase() === mainColor.toLowerCase()))
      || product.variants.find((v) => v.available) || product.variants[0];
    const id = 'qv-' + product.id;
    const view = document.createElement('div');
    view.className = 'mw-quick__grid';
    view.innerHTML = `
      <div class="mw-quick__gallery">
        <div class="mw-quick__stage">
          <img data-qv-main alt="">
          <button class="mw-quick__arrow mw-quick__arrow--prev" type="button" data-qv-step="-1" aria-label="Previous image">&#8249;</button>
          <button class="mw-quick__arrow mw-quick__arrow--next" type="button" data-qv-step="1" aria-label="Next image">&#8250;</button>
        </div>
        <div class="mw-quick__thumbs" data-qv-thumbs></div>
      </div>
      <div class="mw-quick__info">
        <p class="fg-meta mw-quick__kicker">${esc(product.type || 'Original artwork')}</p>
        <h2 class="mw-quick__title" id="QuickViewTitle">${esc(product.title)}</h2>
        <p class="mw-quick__price" data-qv-price></p>
        <form action="${esc(root)}cart/add" method="post" class="mw-quick__form" novalidate>
          <input type="hidden" name="id" data-qv-id>
          ${product.variants.length > 1 || !/default title/i.test(product.variants[0].title) ? options.map((o, i) => `
            <fieldset class="option mw-quick__option">
              <legend class="label">${esc(o.name)}: <span data-qv-label="${i}"></span></legend>
              <div class="option__values${i === colorIndex ? ' mw-swatches' : ''}">
                ${[...new Set(product.variants.map((v) => v.options[i]))].map((value, j) => {
                  const sw = i === colorIndex ? SWATCH[value.toLowerCase()] : null;
                  return `<input type="radio" id="${id}-${i}-${j}" name="${id}-${i}" value="${esc(value)}" data-qv-option="${i}">
                    <label for="${id}-${i}-${j}"${sw ? ` class="mw-swatch" style="--sw:${sw}" title="${esc(value)}"` : ''}>${sw ? `<span class="visually-hidden">${esc(value)}</span>` : esc(value)}</label>`;
                }).join('')}
              </div>
            </fieldset>`).join('') : ''}
          <div class="buy">
            <div class="qty">
              <button type="button" data-qv-qty="-1" aria-label="${esc(S.decrease)}">&minus;</button>
              <label class="visually-hidden" for="${id}-qty">${esc(S.quantity)}</label>
              <input type="number" id="${id}-qty" name="quantity" value="1" min="1" inputmode="numeric">
              <button type="button" data-qv-qty="1" aria-label="${esc(S.increase)}">+</button>
            </div>
            <button class="btn btn--block" type="submit" data-qv-add></button>
          </div>
          <p class="form-error" role="alert" data-form-error hidden></p>
        </form>
        <a class="mw-quick__details fg-meta" href="${esc(url || product.url)}">${esc(S.details)} &rarr;</a>
      </div>`;
    body.replaceChildren(view);

    const main = view.querySelector('[data-qv-main]');
    const thumbs = view.querySelector('[data-qv-thumbs]');
    let set = [];
    let index = 0;

    function show(i) {
      if (!set.length) { main.removeAttribute('src'); return; }
      index = (i + set.length) % set.length;
      main.src = sized(set[index].src, 900);
      main.alt = set[index].alt || product.title;
      thumbs.querySelectorAll('button').forEach((b, k) => b.setAttribute('aria-current', String(k === index)));
    }
    function useColor(color) {
      const labeled = images.filter((m) => m.color);
      let next = color ? labeled.filter((m) => m.color.toLowerCase() === color.toLowerCase()) : [];
      if (!next.length) next = labeled.length && !color ? labeled : images;
      set = next;
      thumbs.innerHTML = set.length > 1 ? set.map((m, k) =>
        `<button type="button" data-qv-thumb="${k}" aria-label="Show image ${k + 1}"><img src="${esc(sized(m.src, 160))}" alt="" loading="lazy"></button>`).join('') : '';
      view.querySelectorAll('[data-qv-step]').forEach((b) => { b.hidden = set.length < 2; });
      show(0);
    }

    function sync() {
      view.querySelector('[data-qv-id]').value = variant.id;
      const was = variant.compare_at_price > variant.price ? ` <s>${money(variant.compare_at_price)}</s>` : '';
      view.querySelector('[data-qv-price]').innerHTML = money(variant.price) + was;
      const add = view.querySelector('[data-qv-add]');
      add.disabled = !variant.available;
      add.textContent = variant.available ? S.addToCart : S.soldOut;
      variant.options.forEach((value, i) => {
        const radio = view.querySelector(`[data-qv-option="${i}"][value="${CSS.escape(value)}"]`);
        if (radio) radio.checked = true;
        const lbl = view.querySelector(`[data-qv-label="${i}"]`);
        if (lbl) lbl.textContent = value;
      });
      // Grey out values that can't be bought with the other current choices.
      view.querySelectorAll('[data-qv-option]').forEach((radio) => {
        const i = Number(radio.dataset.qvOption);
        const possible = product.variants.some((v) => v.available && v.options[i] === radio.value
          && v.options.every((val, k) => k === i || val === variant.options[k]));
        view.querySelector(`label[for="${radio.id}"]`).classList.toggle('is-unavailable', !possible);
      });
    }

    view.addEventListener('change', (e) => {
      const radio = e.target.closest('[data-qv-option]');
      if (!radio) return;
      const i = Number(radio.dataset.qvOption);
      const wanted = variant.options.map((v, k) => (k === i ? radio.value : v));
      variant = product.variants.find((v) => v.options.every((val, k) => val === wanted[k]))
        || product.variants.find((v) => v.available && v.options[i] === radio.value)
        || product.variants.find((v) => v.options[i] === radio.value) || variant;
      if (i === colorIndex) useColor(variant.options[colorIndex]);
      sync();
    });
    view.addEventListener('click', (e) => {
      const step = e.target.closest('[data-qv-step]');
      if (step) show(index + Number(step.dataset.qvStep));
      const thumb = e.target.closest('[data-qv-thumb]');
      if (thumb) show(Number(thumb.dataset.qvThumb));
      const qty = e.target.closest('[data-qv-qty]');
      if (qty) {
        const input = view.querySelector('input[name="quantity"]');
        input.value = Math.max(1, (parseInt(input.value, 10) || 1) + Number(qty.dataset.qvQty));
      }
    });

    useColor(colorIndex >= 0 ? variant.options[colorIndex] : null);
    sync();
  }

  updateCounts();
})();

// ---------- hoodie page: "Complete the set" add-on (2026-11-20, snippets/matching-sweatpants.liquid) ----------
(() => {
  document.querySelectorAll('[data-set-addon]').forEach((box) => {
    let data;
    try { data = JSON.parse(box.querySelector('[data-set-data]').textContent); } catch (e) { return; }
    const form = document.getElementById(box.dataset.for);
    if (!form) return;
    const fmt = box.dataset.money || '${{amount}}';
    const money = (cents) => fmt.replace(/\{\{\s*\w+\s*\}\}/, (cents / 100).toFixed(2));
    const yes = box.querySelector('[data-set-yes]');
    const panel = box.querySelector('[data-set-panel]');
    const colorsEl = box.querySelector('[data-set-colors]');
    const sizesEl = box.querySelector('[data-set-sizes]');
    const order = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL'];
    const colors = [...new Set(data.pants.map((v) => v.color))];
    const sizes = [...new Set(data.pants.map((v) => v.size))].sort((a, b) => order.indexOf(a) - order.indexOf(b));
    const uid = box.dataset.for + '-set';
    let color = colors[0];
    let size = null;

    const mainVariant = () => data.main[form.querySelector('[name="id"]').value];
    const mainSize = () => { const v = mainVariant(); return v && v.options.find((o) => sizes.includes(o)); };
    const pick = () => data.pants.find((v) => v.color === color && v.size === size);

    function buttons(el, values, name, current, onPick) {
      el.innerHTML = '';
      values.forEach((val, i) => {
        const id = `${uid}-${name}-${i}`;
        const input = Object.assign(document.createElement('input'), { type: 'radio', name: `${uid}-${name}`, id, value: val, checked: val === current });
        const label = Object.assign(document.createElement('label'), { htmlFor: id, textContent: val });
        if (name === 'size') {
          const v = data.pants.find((p) => p.color === color && p.size === val);
          if (!v || !v.available) { input.disabled = true; label.classList.add('is-unavailable'); }
        }
        input.addEventListener('change', () => onPick(val));
        el.append(input, label);
      });
    }

    let lastMainSize;
    function render() {
      // Default the pants size to the hoodie's size, and follow it when the hoodie size changes.
      const ms = mainSize();
      if (ms && ms !== lastMainSize && sizes.includes(ms)) size = ms;
      lastMainSize = ms;
      if (!size || !pick() || !pick().available) size = sizes.includes(ms) ? ms : (size || sizes[0]);
      buttons(colorsEl, colors, 'color', color, (v) => { color = v; render(); });
      buttons(sizesEl, sizes, 'size', size, (v) => { size = v; render(); });
      const m = mainVariant(); const p = pick();
      box.dataset.pantsVariant = p && p.available ? p.id : '';
      if (!m || !p) return;
      const list = m.price + p.price;
      box.querySelector('[data-set-main-price]').textContent = money(m.price);
      box.querySelector('[data-set-pants-price]').textContent = money(p.price);
      const note = box.querySelector('[data-set-note]');
      const totalEl = box.querySelector('[data-set-total]');
      if (box.dataset.phase === 'set') {
        const total = m.price + Math.round(p.price * 0.8);
        totalEl.innerHTML = `<s>${money(list)}</s> ${money(total)}`;
        note.textContent = `Set price: 20% off the sweatpants with this ${box.dataset.kind}, applied in your cart.`;
      } else if (box.dataset.phase === 'sale') {
        const total = Math.round(list * 0.85);
        totalEl.innerHTML = `<s>${money(list)}</s> ${money(total)}`;
        note.textContent = 'Holiday Sale: 15% off both, applied in your cart.';
      } else {
        totalEl.textContent = money(list);
        note.textContent = '';
      }
      const addBtn = form.querySelector('[data-add-button]');
      if (addBtn && !addBtn.disabled) addBtn.textContent = yes.checked ? 'Add both to cart' : (addBtn.dataset.label || addBtn.textContent);
    }

    const addBtn = form.querySelector('[data-add-button]');
    if (addBtn) addBtn.dataset.label = addBtn.textContent.trim();
    yes.addEventListener('change', () => {
      panel.hidden = !yes.checked;
      box.classList.toggle('is-on', yes.checked);
      if (!yes.checked && addBtn && !addBtn.disabled) addBtn.textContent = addBtn.dataset.label;
      render();
    });
    // Follow the hoodie's own colour/size picks (variant id changes) so prices and the default pants size stay right.
    form.addEventListener('change', () => setTimeout(render, 0));
    render();
  });
})();

