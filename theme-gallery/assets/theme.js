// Elsewhere Gallery theme scripts. Every feature works on plain links and forms first; this file adds
// drawers, the mega menu, carousels, tabs, live filters, the product page and the cart drawer.

(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function formatMoney(cents) {
    const fmt = (window.theme && theme.moneyFormat) || '${{amount}}';
    const amount = (cents / 100).toFixed(2);
    const noZeros = amount.replace(/\.00$/, '');
    const withCommas = (s) => s.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return fmt
      .replace(/\{\{\s*amount_no_decimals\s*\}\}/, withCommas(Math.round(cents / 100).toString()))
      .replace(/\{\{\s*amount_with_comma_separator\s*\}\}/, amount.replace('.', ','))
      .replace(/\{\{\s*amount_without_trailing_zeros\s*\}\}/, withCommas(noZeros))
      .replace(/\{\{\s*amount\s*\}\}/, withCommas(amount.split('.')[0]) + '.' + amount.split('.')[1]);
  }

  // ---------- drawers (menu, filters, cart) ----------
  let lastFocus = null;
  function openDrawer(drawer) {
    if (!drawer) return;
    lastFocus = document.activeElement;
    drawer.hidden = false;
    drawer.classList.remove('is-closing');
    requestAnimationFrame(() => requestAnimationFrame(() => drawer.classList.add('is-open')));
    document.body.classList.add('is-locked');
    $$(`[aria-controls="${drawer.id}"]`).forEach((b) => b.setAttribute('aria-expanded', 'true'));
    const panel = $('.drawer__panel', drawer);
    if (panel) setTimeout(() => panel.focus({ preventScroll: true }), 50);
  }
  function closeDrawer(drawer) {
    if (!drawer || !drawer.classList.contains('is-open')) return;
    drawer.classList.remove('is-open');
    drawer.classList.add('is-closing');
    document.body.classList.remove('is-locked');
    $$(`[aria-controls="${drawer.id}"]`).forEach((b) => b.setAttribute('aria-expanded', 'false'));
    const done = () => {
      drawer.classList.remove('is-closing');
      if (!drawer.matches('[data-filter-drawer]')) drawer.hidden = true;
    };
    reduceMotion ? done() : setTimeout(done, 300);
    if (lastFocus) lastFocus.focus({ preventScroll: true });
  }
  document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-drawer-open]');
    if (opener) { e.preventDefault(); openDrawer(document.getElementById(opener.dataset.drawerOpen)); return; }
    const closer = e.target.closest('[data-drawer-close]');
    if (closer) { e.preventDefault(); closeDrawer(closer.closest('.drawer')); }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    $$('.drawer.is-open').forEach(closeDrawer);
    closeMegas();
  });

  // ---------- announcement bar ----------
  const announce = $('[data-announce]');
  if (announce) {
    const msgs = $$('.announce__msg', announce);
    let i = 0;
    let timer;
    const show = (n) => {
      i = (n + msgs.length) % msgs.length;
      msgs.forEach((m, k) => { m.classList.toggle('is-active', k === i); m.setAttribute('aria-hidden', String(k !== i)); });
    };
    const start = () => {
      clearInterval(timer);
      if (msgs.length > 1 && !reduceMotion) timer = setInterval(() => show(i + 1), (Number(announce.dataset.interval) || 5) * 1000);
    };
    const prev = $('[data-announce-prev]', announce);
    const next = $('[data-announce-next]', announce);
    if (prev) prev.addEventListener('click', () => { show(i - 1); start(); });
    if (next) next.addEventListener('click', () => { show(i + 1); start(); });
    announce.addEventListener('mouseenter', () => clearInterval(timer));
    announce.addEventListener('mouseleave', start);
    start();
  }

  // ---------- mega menu ----------
  const megas = $$('[data-mega]');
  function closeMegas(except) {
    megas.forEach((li) => {
      if (li === except) return;
      const btn = $('button', li);
      btn.setAttribute('aria-expanded', 'false');
      $('.mega', li).hidden = true;
    });
  }
  megas.forEach((li) => {
    const btn = $('button', li);
    const panel = $('.mega', li);
    let hoverTimer;
    const open = () => { closeMegas(li); btn.setAttribute('aria-expanded', 'true'); panel.hidden = false; };
    const close = () => { btn.setAttribute('aria-expanded', 'false'); panel.hidden = true; };
    btn.addEventListener('click', () => (panel.hidden ? open() : close()));
    if (window.matchMedia('(hover: hover)').matches) {
      li.addEventListener('mouseenter', () => { clearTimeout(hoverTimer); hoverTimer = setTimeout(open, 80); });
      li.addEventListener('mouseleave', () => { clearTimeout(hoverTimer); hoverTimer = setTimeout(close, 150); });
    }
    li.addEventListener('focusout', (e) => { if (!li.contains(e.relatedTarget)) close(); });
  });
  document.addEventListener('click', (e) => { if (!e.target.closest('[data-mega]')) closeMegas(); });

  // ---------- hero carousel ----------
  $$('[data-carousel]').forEach((root) => {
    const slides = $$('[data-slide]', root);
    if (slides.length < 2) return;
    const dots = $$('[data-dot]', root);
    let i = 0;
    let timer;
    const show = (n) => {
      i = (n + slides.length) % slides.length;
      slides.forEach((s, k) => {
        s.classList.toggle('is-active', k === i);
        s.setAttribute('aria-hidden', String(k !== i));
        $$('a, button', s).forEach((el) => { el.tabIndex = k === i ? 0 : -1; });
      });
      dots.forEach((d, k) => d.classList.toggle('is-active', k === i));
    };
    const play = () => {
      clearInterval(timer);
      if (root.dataset.autoplay === 'true' && !reduceMotion) timer = setInterval(() => show(i + 1), 6500);
    };
    $('[data-prev]', root).addEventListener('click', () => { show(i - 1); play(); });
    $('[data-next]', root).addEventListener('click', () => { show(i + 1); play(); });
    dots.forEach((d) => d.addEventListener('click', () => { show(Number(d.dataset.dot)); play(); }));
    root.addEventListener('mouseenter', () => clearInterval(timer));
    root.addEventListener('mouseleave', play);
    root.addEventListener('focusin', () => clearInterval(timer));
    swipe($('.hero__frame', root), () => { show(i + 1); play(); }, () => { show(i - 1); play(); });
    show(0);
    play();
  });

  function swipe(el, onLeft, onRight) {
    if (!el) return;
    let x0 = null;
    let y0 = null;
    el.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    el.addEventListener('touchend', (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      const dy = e.changedTouches[0].clientY - y0;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) (dx < 0 ? onLeft : onRight)();
      x0 = null;
    }, { passive: true });
  }

  // ---------- tabs ----------
  $$('[data-tabs]').forEach((root) => {
    const tabs = $$('[role="tab"]', root);
    const select = (tab) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.classList.toggle('is-active', on);
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
      });
    };
    tabs.forEach((t, k) => {
      t.addEventListener('click', () => select(t));
      t.addEventListener('keydown', (e) => {
        const dir = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!dir) return;
        const next = tabs[(k + dir + tabs.length) % tabs.length];
        select(next);
        next.focus();
      });
    });
  });

  // ---------- collection filters ----------
  const filterForm = $('[data-filter-form]');
  if (filterForm) {
    let timer;
    const submit = () => {
      const params = new URLSearchParams();
      new FormData(filterForm).forEach((value, key) => { if (value !== '') params.append(key, value); });
      const qs = params.toString();
      window.location.search = qs;
    };
    filterForm.addEventListener('change', (e) => {
      clearTimeout(timer);
      timer = setTimeout(submit, e.target.type === 'number' ? 700 : 0);
    });
    filterForm.addEventListener('submit', (e) => { e.preventDefault(); submit(); });
    const sort = $('[data-sort]');
    if (sort) sort.addEventListener('change', submit);
  }

  // ---------- product page ----------
  $$('[data-product]').forEach(initProduct);

  function initProduct(root) {
    const section = root.closest('section');
    const jsonEl = section && $('[data-product-json]', section);
    if (!jsonEl) return;
    const product = JSON.parse(jsonEl.textContent);
    const colorIndex = Number(root.dataset.colorIndex);
    const form = $('.buy__form', root);
    const idInput = $('[data-variant-id]', root);
    const priceEl = $('[data-product-price]', root);
    const addBtn = $('[data-add-button]', root);
    const errorEl = $('[data-form-error]', root);
    const radios = $$('input[data-option-index]', root);

    // gallery
    const slides = $$('.gallery__slide', root);
    const thumbs = $$('.gallery__thumb', root);
    const pos = $('[data-gallery-pos]', root);
    const total = $('[data-gallery-total]', root);
    let visible = slides.slice();
    let current = Math.max(0, slides.findIndex((s) => s.classList.contains('is-active')));

    function showSlide(slide) {
      if (!slide) return;
      slides.forEach((s) => s.classList.toggle('is-active', s === slide));
      thumbs.forEach((t) => t.setAttribute('aria-current', String(t.dataset.thumb === slide.dataset.mediaId)));
      const img = $('img', slide);
      if (img) img.loading = 'eager';
      current = visible.indexOf(slide);
      if (pos) pos.textContent = String(current + 1);
      const thumb = thumbs.find((t) => t.dataset.thumb === slide.dataset.mediaId);
      if (thumb && thumb.parentElement.scrollTo) {
        const box = thumb.parentElement;
        const vertical = box.scrollHeight > box.clientHeight + 4;
        box.scrollTo({
          [vertical ? 'top' : 'left']: vertical ? thumb.offsetTop - box.clientHeight / 2 : thumb.offsetLeft - box.clientWidth / 2,
          behavior: reduceMotion ? 'auto' : 'smooth',
        });
      }
    }
    function step(dir) { if (visible.length) showSlide(visible[(current + dir + visible.length) % visible.length]); }
    // Only the chosen color's photos show when photos are labeled "<Title> in <Color>, ...".
    function filterByColor(color, preferId) {
      const matches = color ? slides.filter((s) => s.dataset.color && s.dataset.color.toLowerCase() === color.toLowerCase()) : [];
      visible = matches.length ? matches : slides.slice();
      const ids = new Set(visible.map((s) => s.dataset.mediaId));
      thumbs.forEach((t) => { t.hidden = !ids.has(t.dataset.thumb); });
      if (total) total.textContent = String(visible.length);
      const preferred = preferId && visible.find((s) => s.dataset.mediaId === String(preferId));
      showSlide(preferred || visible[0]);
    }
    thumbs.forEach((t) => t.addEventListener('click', () => showSlide(slides.find((s) => s.dataset.mediaId === t.dataset.thumb))));
    const prevBtn = $('[data-gallery-prev]', root);
    const nextBtn = $('[data-gallery-next]', root);
    if (prevBtn) prevBtn.addEventListener('click', () => step(-1));
    if (nextBtn) nextBtn.addEventListener('click', () => step(1));
    swipe($('.gallery__main', root), () => step(1), () => step(-1));

    // variants
    const selected = () => {
      const out = [];
      radios.filter((r) => r.checked).forEach((r) => { out[Number(r.dataset.optionIndex)] = r.value; });
      return out;
    };
    function markAvailability(sel) {
      radios.forEach((radio) => {
        const index = Number(radio.dataset.optionIndex);
        const possible = product.variants.some((v) => v.available && v.options[index] === radio.value &&
          v.options.every((value, k) => k === index || sel[k] === undefined || value === sel[k]));
        const label = $(`label[for="${radio.id}"]`, root);
        if (label) label.classList.toggle('is-unavailable', !possible);
      });
    }
    function update(changedIndex) {
      const sel = selected();
      sel.forEach((value, k) => { const l = $(`[data-option-label="${k}"]`, root); if (l) l.textContent = value; });
      markAvailability(sel);
      const variant = product.variants.find((v) => v.options.every((value, k) => value === sel[k]));
      if (errorEl) errorEl.hidden = true;
      if (!variant) {
        addBtn.disabled = true;
        addBtn.textContent = theme.strings.unavailable;
        return;
      }
      idInput.value = variant.id;
      addBtn.disabled = !variant.available;
      addBtn.textContent = variant.available ? theme.strings.addToCart : theme.strings.soldOut;
      if (priceEl) {
        let html = '<span class="price" data-price>';
        if (variant.compare_at_price > variant.price) html += `<s>${formatMoney(variant.compare_at_price)}</s>`;
        html += `${formatMoney(variant.price)}</span>`;
        if (variant.compare_at_price > variant.price) {
          html += `<span class="badge badge--sale">Save ${Math.floor(((variant.compare_at_price - variant.price) * 100) / variant.compare_at_price)}%</span>`;
        }
        priceEl.innerHTML = html;
      }
      if (colorIndex >= 0 && (changedIndex === undefined || changedIndex === colorIndex)) {
        filterByColor(sel[colorIndex], variant.featured_media && variant.featured_media.id);
      } else if (variant.featured_media) {
        const s = visible.find((x) => x.dataset.mediaId === String(variant.featured_media.id));
        if (s) showSlide(s);
      }
      const url = new URL(window.location.href);
      url.searchParams.set('variant', variant.id);
      window.history.replaceState({}, '', url);
    }
    radios.forEach((r) => r.addEventListener('change', () => update(Number(r.dataset.optionIndex))));
    if (radios.length) {
      markAvailability(selected());
      if (colorIndex >= 0) {
        const activeSlide = slides.find((s) => s.classList.contains('is-active'));
        filterByColor(selected()[colorIndex], activeSlide && activeSlide.dataset.mediaId);
      }
    }

    $$('[data-qty]', root).forEach((btn) => btn.addEventListener('click', () => {
      const input = $('input', btn.parentElement);
      input.value = Math.max(1, (parseInt(input.value, 10) || 1) + Number(btn.dataset.qty));
    }));

    // add to cart in place
    if (form && $('[data-cart-drawer]')) {
      form.addEventListener('submit', async (e) => {
        if (e.submitter && e.submitter.name !== 'add') return;
        e.preventDefault();
        addBtn.disabled = true;
        try {
          const res = await fetch(`${theme.routes.cartAdd}.js`, {
            method: 'POST',
            headers: { Accept: 'application/json' },
            body: new FormData(form),
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.description || data.message || 'Could not add to cart');
          addBtn.classList.add('is-added');
          addBtn.textContent = theme.strings.added;
          setTimeout(() => { addBtn.classList.remove('is-added'); addBtn.textContent = theme.strings.addToCart; }, 1600);
          await Cart.refresh(true);
        } catch (err) {
          if (errorEl) { errorEl.textContent = err.message; errorEl.hidden = false; }
        } finally {
          addBtn.disabled = false;
        }
      });
    }

    // sticky add bar on phones
    const bar = $('[data-sticky-buy]', section);
    if (bar && 'IntersectionObserver' in window) {
      const barBtn = $('[data-sticky-add]', bar);
      const barPrice = $('[data-sticky-price]', bar);
      const sync = () => {
        barBtn.disabled = addBtn.disabled;
        barBtn.textContent = addBtn.textContent.trim();
        const p = priceEl && $('.price', priceEl);
        if (p) barPrice.innerHTML = p.outerHTML;
      };
      sync();
      new MutationObserver(sync).observe(addBtn, { attributes: true, childList: true, characterData: true, subtree: true });
      if (priceEl) new MutationObserver(sync).observe(priceEl, { childList: true, subtree: true });
      barBtn.addEventListener('click', () => addBtn.click());
      new IntersectionObserver(([entry]) => {
        const past = !entry.isIntersecting && entry.boundingClientRect.top < 0;
        bar.classList.toggle('is-shown', past);
        bar.setAttribute('aria-hidden', String(!past));
        barBtn.tabIndex = past ? 0 : -1;
      }).observe(addBtn);
    }
  }

  // ---------- dialogs (size guide) ----------
  document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-dialog-open]');
    if (opener) {
      const d = document.getElementById(opener.dataset.dialogOpen);
      if (d && d.showModal) { e.preventDefault(); d.showModal(); }
      return;
    }
    if (e.target.closest('[data-dialog-close]')) e.target.closest('dialog').close();
    else if (e.target.tagName === 'DIALOG') e.target.close();
  });

  // ---------- recommendations ----------
  $$('[data-recs]').forEach((box) => {
    if ($('[data-recs-loaded]', box)) return;
    const load = () => fetch(box.dataset.url)
      .then((r) => (r.ok ? r.text() : ''))
      .then((html) => {
        const found = new DOMParser().parseFromString(html, 'text/html').querySelector('[data-recs-loaded]');
        if (found) box.replaceChildren(found);
      })
      .catch(() => {});
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(([en]) => { if (en.isIntersecting) { io.disconnect(); load(); } }, { rootMargin: '600px 0px' });
      io.observe(box);
    } else load();
  });

  // ---------- cart drawer ----------
  const Cart = {
    drawer: $('[data-cart-drawer]'),
    async refresh(open) {
      const cart = await fetch(`${theme.routes.cart}.js`, { headers: { Accept: 'application/json' } }).then((r) => r.json());
      this.render(cart);
      if (open) openDrawer(this.drawer);
      return cart;
    },
    render(cart) {
      $$('[data-cart-count]').forEach((el) => {
        el.textContent = cart.item_count;
        el.classList.toggle('is-empty', cart.item_count === 0);
        el.classList.remove('is-bump');
        void el.offsetWidth;
        el.classList.add('is-bump');
      });
      if (!this.drawer) return;
      const count = $('[data-cart-drawer-count]', this.drawer);
      if (count) count.textContent = cart.item_count ? `(${cart.item_count})` : '';
      const lines = $('[data-cart-lines]', this.drawer);
      const foot = $('[data-cart-foot]', this.drawer);
      foot.hidden = cart.item_count === 0;
      $('[data-cart-subtotal]', this.drawer).textContent = formatMoney(cart.total_price);
      if (!cart.items.length) {
        lines.innerHTML = `<div class="drawer__empty"><p>${esc(theme.strings.cartEmpty)}</p><a class="btn" href="${theme.routes.root}collections/all">Start shopping</a></div>`;
      } else {
        lines.innerHTML = cart.items.map((item, k) => {
          const img = item.image ? `<img src="${imgUrl(item.image, 200)}" alt="" width="84" height="84" loading="lazy">` : '';
          const variant = item.variant_title && !item.product_has_only_default_variant ? `<p class="muted small">${esc(item.variant_title)}</p>` : '';
          const discounts = (item.discounts || []).map((d) => `<p class="small sale">${esc(d.title)}</p>`).join('');
          const was = item.original_line_price > item.final_line_price ? `<s class="muted small">${formatMoney(item.original_line_price)}</s>` : '';
          return `<div class="line" data-line="${k + 1}">
            <a class="line__img" href="${item.url}">${img}</a>
            <div class="line__info">
              <a class="line__title" href="${item.url}">${esc(item.product_title)}</a>${variant}${discounts}
              <div class="line__row">
                <div class="qty">
                  <button type="button" data-line-qty="-1" aria-label="Decrease quantity">&minus;</button>
                  <input type="number" value="${item.quantity}" min="0" inputmode="numeric" aria-label="Quantity" data-line-input>
                  <button type="button" data-line-qty="1" aria-label="Increase quantity">+</button>
                </div>
                <button class="link-btn" type="button" data-line-remove>${esc(theme.strings.remove)}</button>
              </div>
            </div>
            <div class="line__price">${was}<strong>${formatMoney(item.final_line_price)}</strong></div>
          </div>`;
        }).join('');
      }
      const bar = $('[data-ship-bar]', this.drawer);
      if (bar && theme.freeShipping > 0) {
        const left = theme.freeShipping - cart.total_price;
        bar.classList.toggle('is-done', left <= 0);
        $('[data-ship-text]', bar).textContent = left <= 0 ? bar.dataset.done : bar.dataset.away.replace('__AMOUNT__', formatMoney(left));
        $('[data-ship-fill]', bar).style.width = `${Math.min(100, (cart.total_price / theme.freeShipping) * 100)}%`;
        bar.hidden = cart.item_count === 0;
      }
    },
    async change(line, quantity) {
      const lines = $('[data-cart-lines]', this.drawer);
      lines.classList.add('is-busy');
      try {
        const res = await fetch(`${theme.routes.cartChange}.js`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({ line, quantity }),
        });
        this.render(await res.json());
      } finally {
        lines.classList.remove('is-busy');
      }
    },
  };
  function esc(s) { return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
  function imgUrl(src, width) {
    try { const u = new URL(src, window.location.origin); u.searchParams.set('width', width); return u.toString(); } catch (e) { return src; }
  }

  if (Cart.drawer) {
    document.addEventListener('click', (e) => {
      const opener = e.target.closest('[data-cart-open]');
      if (opener && !document.body.classList.contains('template-cart')) { e.preventDefault(); Cart.refresh(true); return; }
      const lineEl = e.target.closest('[data-line]');
      if (!lineEl || !Cart.drawer.contains(lineEl)) return;
      const line = Number(lineEl.dataset.line);
      const input = $('[data-line-input]', lineEl);
      if (e.target.closest('[data-line-remove]')) Cart.change(line, 0);
      const stepBtn = e.target.closest('[data-line-qty]');
      if (stepBtn) Cart.change(line, Math.max(0, (parseInt(input.value, 10) || 0) + Number(stepBtn.dataset.lineQty)));
    });
    Cart.drawer.addEventListener('change', (e) => {
      if (!e.target.matches('[data-line-input]')) return;
      Cart.change(Number(e.target.closest('[data-line]').dataset.line), Math.max(0, parseInt(e.target.value, 10) || 0));
    });
  }
})();
