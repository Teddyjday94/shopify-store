// Elsewhere Supply Co. theme scripts: mobile menu, product gallery, variant picker, quantity.

document.addEventListener('DOMContentLoaded', () => {
  initMenu();
  initFilters();
  initReveal();
  document.querySelectorAll('[data-product]').forEach(initProduct);
});

// Scroll reveal: fade/slide items in as they enter the viewport, staggered within a row.
function initReveal() {
  if (!document.body.classList.contains('motion')) return;
  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const items = document.querySelectorAll('.card, .ship-label, .section-head, .tour__row, .product__info, .gallery, .page-narrow, .edit-piece, .wardrobe-edit__heading, .supply-note');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -40px 0px', threshold: 0.01 });
  items.forEach(el => {
    if (el.classList.contains('cinema-reveal')) return;
    if (el.getBoundingClientRect().top < window.innerHeight - 40) return;
    const siblings = Array.from(el.parentElement.children);
    el.style.setProperty('--reveal-delay', String((siblings.indexOf(el) % 3) * 0.09) + 's');
    el.classList.add('cinema-reveal');
    observer.observe(el);
  });
}
document.addEventListener('shopify:section:load', initReveal);

// Collection filters: apply on change; price inputs apply after a short pause.
function initFilters() {
  const form = document.querySelector('[data-filter-form]');
  if (!form) return;
  let timer;
  form.addEventListener('change', (e) => {
    clearTimeout(timer);
    timer = setTimeout(() => form.requestSubmit(), e.target.type === 'number' ? 600 : 0);
  });
  form.addEventListener('submit', (e) => {
    // Drop empty fields so URLs stay clean.
    e.preventDefault();
    const params = new URLSearchParams();
    new FormData(form).forEach((value, key) => { if (value !== '') params.append(key, value); });
    window.location.search = params.toString();
  });
  const panels = Array.from(form.querySelectorAll('[data-dropdown]'));
  document.addEventListener('click', (e) => {
    panels.forEach((d) => { if (!d.contains(e.target)) d.open = false; });
  });
}

function initMenu() {
  const toggle = document.querySelector('[data-menu-toggle]');
  const nav = document.getElementById('HeaderNav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
  });

  // Dropdowns: one open at a time; close on outside click or Escape.
  const dropdowns = Array.from(nav.querySelectorAll('[data-dropdown]'));
  dropdowns.forEach((d) => d.addEventListener('toggle', () => {
    if (d.open) dropdowns.forEach((other) => { if (other !== d) other.open = false; });
  }));
  document.addEventListener('click', (e) => {
    dropdowns.forEach((d) => { if (!d.contains(e.target)) d.open = false; });
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    dropdowns.filter((d) => d.open).forEach((d) => { d.open = false; d.querySelector('summary').focus(); });
  });
}

function initProduct(root) {
  const section = root.closest('section');
  const jsonEl = section && section.querySelector('[data-product-json]');
  if (!jsonEl) return;
  const product = JSON.parse(jsonEl.textContent);

  const main = root.querySelector('.gallery__main img');
  const thumbs = Array.from(root.querySelectorAll('.gallery__thumb'));
  const prevBtn = root.querySelector('[data-gallery-prev]');
  const nextBtn = root.querySelector('[data-gallery-next]');
  const sideTag = root.querySelector('[data-gallery-side]');
  const idInput = root.querySelector('[data-variant-id]');
  const priceEl = root.querySelector('[data-product-price]');
  const addBtn = root.querySelector('[data-add-button]');
  const radios = Array.from(root.querySelectorAll('input[data-option-index]'));

  // Photos labeled "<Title> in <Color>, <front|back> print" belong to one color and side.
  // When a product has them, the gallery shows only the chosen color's front and back;
  // otherwise it shows every photo. Either way, arrows and swipes step through what is shown.
  thumbs.forEach((t) => {
    const m = (t.dataset.alt || '').match(/ in (.+), (front|back) print$/i);
    if (m) { t.dataset.color = m[1].toLowerCase(); t.dataset.side = m[2].toLowerCase(); }
  });
  const labeled = thumbs.filter((t) => t.dataset.color);
  const colorIndex = (product.options || []).findIndex((name) => /colou?r/i.test(typeof name === 'string' ? name : name.name));
  let visible = thumbs;
  let current = 0;

  function show(i) {
    if (!visible.length || !main) return;
    current = (i + visible.length) % visible.length;
    const thumb = visible[current];
    main.src = thumb.dataset.src;
    main.srcset = thumb.dataset.srcset;
    main.alt = thumb.dataset.alt || main.alt;
    thumbs.forEach((t) => t.setAttribute('aria-current', String(t === thumb)));
    if (sideTag) {
      sideTag.hidden = !thumb.dataset.side;
      sideTag.textContent = thumb.dataset.side === 'back' ? 'Back' : 'Front';
    }
  }

  function filterTo(color) {
    let set = thumbs;
    if (labeled.length) {
      const want = (color || '').toLowerCase();
      set = labeled.filter((t) => t.dataset.color === want);
      if (!set.length) set = labeled.filter((t) => t.dataset.color === labeled[0].dataset.color);
    }
    visible = set;
    thumbs.forEach((t) => { t.hidden = !visible.includes(t); });
    const many = visible.length > 1;
    [prevBtn, nextBtn].forEach((b) => { if (b) b.hidden = !many; });
    root.classList.toggle('gallery--single', !many);
    show(0);
  }

  thumbs.forEach((thumb) => thumb.addEventListener('click', () => {
    const i = visible.indexOf(thumb);
    if (i >= 0) show(i);
  }));
  if (prevBtn) prevBtn.addEventListener('click', () => show(current - 1));
  if (nextBtn) nextBtn.addEventListener('click', () => show(current + 1));

  // Swipe on touch screens.
  const stage = root.querySelector('.gallery__main');
  let touchX = null;
  if (stage) {
    stage.addEventListener('touchstart', (e) => { touchX = e.touches[0].clientX; }, { passive: true });
    stage.addEventListener('touchend', (e) => {
      if (touchX === null) return;
      const dx = e.changedTouches[0].clientX - touchX;
      touchX = null;
      if (Math.abs(dx) > 40) show(current + (dx < 0 ? 1 : -1));
    });
  }
  root.addEventListener('keydown', (e) => {
    if (!e.target.closest('.gallery')) return;
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });

  function selectedOptions() {
    const selected = [];
    radios.filter((r) => r.checked).forEach((r) => { selected[Number(r.dataset.optionIndex)] = r.value; });
    return selected;
  }

  function selectedColor() {
    if (colorIndex >= 0) return selectedOptions()[colorIndex];
    const variant = product.variants.find((v) => String(v.id) === String(idInput && idInput.value));
    return variant ? variant.option1 : '';
  }

  function formatMoney(cents) {
    return new Intl.NumberFormat(document.documentElement.lang || 'en', {
      style: 'currency',
      currency: (window.Shopify && Shopify.currency && Shopify.currency.active) || 'USD',
    }).format(cents / 100);
  }

  // Strike through values that can't be combined with the other current selections.
  function markAvailability(selected) {
    radios.forEach((radio) => {
      const index = Number(radio.dataset.optionIndex);
      const candidate = selected.slice();
      candidate[index] = radio.value;
      const possible = product.variants.some((v) =>
        v.available && v.options.every((value, i) => i === index || candidate[i] === undefined || value === candidate[i]) &&
        v.options[index] === radio.value);
      const label = root.querySelector(`label[for="${radio.id}"]`);
      if (label) label.classList.toggle('is-unavailable', !possible);
    });
  }

  let lastColor = null;
  function syncGallery(variant) {
    if (labeled.length) {
      const color = selectedColor();
      if (color !== lastColor) { lastColor = color; filterTo(color); }
    } else if (variant && variant.featured_media) {
      const i = visible.findIndex((t) => t.dataset.mediaId === String(variant.featured_media.id));
      if (i >= 0) show(i);
    }
  }

  function update() {
    const selected = selectedOptions();
    selected.forEach((value, i) => {
      const label = root.querySelector(`[data-option-label="${i}"]`);
      if (label) label.textContent = value;
    });
    markAvailability(selected);

    const variant = product.variants.find((v) => v.options.every((value, i) => value === selected[i]));
    syncGallery(variant);
    if (!variant) {
      addBtn.disabled = true;
      addBtn.textContent = window.themeStrings.unavailable;
      return;
    }
    idInput.value = variant.id;
    addBtn.disabled = !variant.available;
    addBtn.textContent = variant.available ? window.themeStrings.addToCart : window.themeStrings.soldOut;

    if (priceEl) {
      const compare = variant.compare_at_price > variant.price ? `<s>${formatMoney(variant.compare_at_price)}</s>` : '';
      priceEl.innerHTML = `<span class="price">${compare}${formatMoney(variant.price)}</span>`;
    }
    const url = new URL(window.location.href);
    url.searchParams.set('variant', variant.id);
    window.history.replaceState({}, '', url);
  }

  // Initial gallery: the selected color's photos, or everything with the current photo shown.
  if (labeled.length) {
    lastColor = selectedColor();
    filterTo(lastColor);
  } else {
    filterTo(null);
    const i = thumbs.findIndex((t) => t.getAttribute('aria-current') === 'true');
    show(i >= 0 ? i : 0);
  }

  radios.forEach((radio) => radio.addEventListener('change', update));
  if (radios.length) markAvailability(selectedOptions());

  root.querySelectorAll('[data-qty]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = btn.parentElement.querySelector('input');
      input.value = Math.max(1, (parseInt(input.value, 10) || 1) + Number(btn.dataset.qty));
    });
  });
}
