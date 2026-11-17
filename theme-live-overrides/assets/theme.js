// Elsewhere Apparel Co. theme scripts: mobile menu, product gallery, variant picker, quantity.

document.addEventListener('DOMContentLoaded', () => {
  initMenu();
  initFilters();
  initReveal();
  initCollectionSwap();
  document.querySelectorAll('[data-product]').forEach(initProduct);
});

// Save the product card's position in its own history entry before opening it.
document.addEventListener('click', (event) => {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const link = event.target instanceof Element ? event.target.closest('main a[href]') : null;
  if (!link || (link.target && link.target !== '_self') || link.hasAttribute('download')) return;
  if (link.origin !== window.location.origin || !/\/products\/[^/]+\/?$/.test(link.pathname)) return;

  window.history.replaceState({
    ...window.history.state,
    productReturn: {
      href: link.getAttribute('href'),
      top: link.getBoundingClientRect().top,
      scrollY: window.scrollY,
    },
  }, '');
});

window.addEventListener('pageshow', (event) => {
  const position = window.history.state?.productReturn;
  if (!position || (!event.persisted && performance.getEntriesByType('navigation')[0]?.type !== 'back_forward')) return;

  requestAnimationFrame(() => {
    let target = position.scrollY;
    let closest = Infinity;
    document.querySelectorAll('main a[href]').forEach((link) => {
      if (link.getAttribute('href') !== position.href || !link.getClientRects().length) return;
      const offset = link.getBoundingClientRect().top + window.scrollY - position.top;
      const distance = Math.abs(offset - position.scrollY);
      if (distance < closest) {
        target = offset;
        closest = distance;
      }
    });
    const { productReturn, ...historyState } = window.history.state || {};
    window.history.replaceState(historyState, '');
    window.scrollTo({ top: target, behavior: 'instant' });
  });
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
// Called again after every in-place swap, once the new form is in the page.
const readyForms = new WeakSet();
function initFilters() {
  const form = document.querySelector('[data-filter-form]');
  if (!form || readyForms.has(form)) return;
  readyForms.add(form);
  let timer;
  form.addEventListener('change', (e) => {
    clearTimeout(timer);
    timer = setTimeout(() => form.requestSubmit(), e.target.type === 'number' ? 600 : 0);
  });
  form.addEventListener('submit', (e) => {
    // Drop empty fields so URLs stay clean, then load the filtered list in place.
    e.preventDefault();
    const params = new URLSearchParams();
    new FormData(form).forEach((value, key) => { if (value !== '') params.append(key, value); });
    const url = new URL(window.location.href);
    url.search = params.toString();
    if (!loadCollection(url.href)) window.location.search = params.toString();
  });
}
// Close open filter panels on an outside click (one listener for whichever form is current).
document.addEventListener('click', (e) => {
  document.querySelectorAll('[data-filter-form] [data-dropdown][open]').forEach((d) => {
    if (!d.contains(e.target)) d.open = false;
  });
});

// Collection pages: moving between collections (Shop / Collections tabs, header dropdowns, filter chips,
// pagination) swaps the product list in place, like a filter, instead of loading a new page.
function collectionUrl(href) {
  let url;
  try { url = new URL(href, window.location.href); } catch { return null; }
  if (url.origin !== window.location.origin) return null;
  return /^\/collections\/[^/]+\/?$/.test(url.pathname) ? url : null;  // a collection, not /collections or a product
}

let collectionRequest = 0;
let renderedCollectionUrl;
const collectionPages = new Map();  // url -> Promise<html>; tapped or hovered collections load early and stay cached

function fetchCollection(href) {
  const url = collectionUrl(href);
  if (!url) return null;
  if (!collectionPages.has(url.href)) {
    const page = fetch(url.href, { headers: { 'X-Requested-With': 'fetch' } })
      .then((r) => { if (!r.ok) throw new Error(r.status); return r.text(); });
    page.catch(() => collectionPages.delete(url.href));
    collectionPages.set(url.href, page);
  }
  return collectionPages.get(url.href);
}

// Instant feedback on the tapped tab: it lights up (or, tapping the selected collection, clears) within its row.
// The swapped-in page then renders the real state.
function markActiveTab(href) {
  const tab = Array.from(document.querySelectorAll('[data-collection-tabs] .tab')).find((t) => t.href === href);
  if (!tab) return;
  const turnOn = !tab.classList.contains('is-active');
  tab.parentElement.querySelectorAll('.tab').forEach((t) => {
    const on = t === tab && turnOn;
    t.classList.toggle('is-active', on);
    if (on) t.setAttribute('aria-current', 'page'); else t.removeAttribute('aria-current');
  });
}

function loadCollection(href, { push = true } = {}) {
  const view = document.querySelector('[data-collection-view]');
  const url = collectionUrl(href);
  if (!view || !url) return false;
  const request = ++collectionRequest;
  markActiveTab(url.href);
  view.setAttribute('aria-busy', 'true');
  fetchCollection(url.href)
    .then((html) => {
      if (request !== collectionRequest) return;
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const next = doc.querySelector('[data-collection-view]');
      if (!next) throw new Error('no collection view');
      const swap = () => {
        if (request !== collectionRequest) return;
        view.replaceWith(next);
        next.querySelectorAll('.card').forEach((card) => card.classList.add('is-visible'));
        initFilters();
        initReveal();
        document.title = doc.title;
        renderedCollectionUrl = url.href.split('#')[0];
        if (push) window.history.pushState({ collection: true }, '', url.href);
        document.querySelectorAll('#HeaderNav details[open]').forEach((d) => { d.open = false; });
        const nav = document.getElementById('HeaderNav');
        if (nav && nav.classList.contains('is-open')) {
          nav.classList.remove('is-open');
          const toggle = document.querySelector('[data-menu-toggle]');
          if (toggle) toggle.setAttribute('aria-expanded', 'false');
        }
        const anchor = next.querySelector('[data-collection-tabs]') || next;
        if (anchor.getBoundingClientRect().top < 0) anchor.scrollIntoView({ block: 'start', behavior: 'instant' });
      };
      const allowsMotion = document.body.classList.contains('motion')
        && !document.documentElement.classList.contains('motion-paused')
        && !matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (document.startViewTransition && allowsMotion) {
        const transition = document.startViewTransition(swap);
        transition.types?.add('fg-collection');
      } else {
        swap();
      }
    })
    .catch(() => { if (request === collectionRequest) window.location.assign(url.href); });
  return true;
}

function initCollectionSwap() {
  if (!document.querySelector('[data-collection-view]')) return;
  renderedCollectionUrl = window.location.href.split('#')[0];
  window.history.replaceState({ ...window.history.state, collection: true }, '');
  collectionPages.set(renderedCollectionUrl, Promise.resolve(document.documentElement.outerHTML));
  // Start loading a collection as soon as a finger touches its link or the mouse rests on it.
  const warm = (e) => {
    const link = e.target instanceof Element ? e.target.closest('a[href]') : null;
    if (link && collectionUrl(link.href)) fetchCollection(link.href);
  };
  document.addEventListener('pointerdown', warm, { passive: true });
  document.addEventListener('mouseover', warm, { passive: true });
  // Once the page has settled, quietly preload every tab's collection (one at a time) so switching is instant.
  const idle = window.requestIdleCallback || ((fn) => setTimeout(fn, 1));
  setTimeout(() => idle(async () => {
    const links = Array.from(document.querySelectorAll('[data-collection-tabs] .tab')).map((a) => a.href);
    for (const href of links) {
      try { await fetchCollection(href); } catch { /* a failed preload just loads on tap */ }
    }
  }), 1500);
  document.addEventListener('click', (e) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const link = e.target instanceof Element ? e.target.closest('a[href]') : null;
    if (!link || (link.target && link.target !== '_self') || link.hasAttribute('download')) return;
    if (!collectionUrl(link.href)) return;
    if (loadCollection(link.href)) e.preventDefault();
  }, true);
  window.addEventListener('popstate', (e) => {
    const url = window.location.href.split('#')[0];
    if (e.state?.collection && url !== renderedCollectionUrl) loadCollection(url, { push: false });
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
  const stage = root.querySelector('.gallery__main');

  // Photos labeled "<Title> in <Color>, <detail>" belong to one color: the print photos
  // ("..., front print" / "..., back print") and the extra shots of the same color ("..., on a model",
  // "..., hanging", "..., on a model, back view"). When a product has labeled print photos, the gallery
  // shows every photo of the chosen color; otherwise it shows every photo. Arrows, swipes and the dots
  // step through what is shown.
  thumbs.forEach((t) => {
    const m = (t.dataset.alt || '').match(/^.* in ([^,]+), (.+)$/i);
    if (!m) return;
    t.dataset.color = m[1].trim().toLowerCase();
    const print = m[2].match(/^(front|back) print$/i);
    if (print) {
      t.dataset.print = 'true';
      t.dataset.side = print[1].toLowerCase();
    }
  });
  const labeled = thumbs.filter((t) => t.dataset.print);
  const colorIndex = (product.options || []).findIndex((name) => /colou?r/i.test(typeof name === 'string' ? name : name.name));
  let visible = thumbs;
  let current = 0;

  // Dots under the photo: one per photo shown, so shoppers can see there is more to swipe through.
  let dots = null;
  if (stage && thumbs.length > 1) {
    dots = document.createElement('div');
    dots.className = 'gallery__dots';
    dots.setAttribute('aria-hidden', 'true');
    stage.appendChild(dots);
  }

  function renderDots() {
    if (!dots) return;
    dots.innerHTML = visible.length > 1 ? visible.map((_, i) => `<span class="gallery__dot${i === current ? ' is-active' : ''}"></span>`).join('') : '';
    dots.hidden = visible.length < 2;
  }

  function show(i, step = 0) {
    if (!visible.length || !main) return;
    current = (i + visible.length) % visible.length;
    const thumb = visible[current];
    if (step && main.animate && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      main.animate([{ opacity: 0.25, transform: `translateX(${step * 24}px)` }, { opacity: 1, transform: 'none' }],
        { duration: 220, easing: 'ease-out' });
    }
    main.src = thumb.dataset.src;
    main.srcset = thumb.dataset.srcset;
    main.alt = thumb.dataset.alt || main.alt;
    thumbs.forEach((t) => t.setAttribute('aria-current', String(t === thumb)));
    if (sideTag) {
      sideTag.hidden = !thumb.dataset.side;
      sideTag.textContent = thumb.dataset.side === 'back' ? 'Back' : 'Front';
    }
    if (dots) dots.querySelectorAll('.gallery__dot').forEach((d, n) => d.classList.toggle('is-active', n === current));
    // Keep the active thumbnail in view by scrolling the thumbnail row sideways only (never the page).
    const row = thumb.parentElement;
    if (step && row && row.scrollWidth > row.clientWidth) {
      const left = thumb.offsetLeft - row.offsetLeft;
      if (left < row.scrollLeft || left + thumb.offsetWidth > row.scrollLeft + row.clientWidth) {
        row.scrollTo({ left: Math.max(0, left - 12), behavior: 'smooth' });
      }
    }
  }

  function filterTo(color) {
    let set = thumbs;
    if (labeled.length) {
      const want = (color || '').toLowerCase();
      set = thumbs.filter((t) => t.dataset.color === want);
      if (!set.some((t) => t.dataset.print)) set = thumbs.filter((t) => t.dataset.color === labeled[0].dataset.color);
    }
    visible = set;
    thumbs.forEach((t) => { t.hidden = !visible.includes(t); });
    const many = visible.length > 1;
    [prevBtn, nextBtn].forEach((b) => { if (b) b.hidden = !many; });
    root.classList.toggle('gallery--single', !many);
    current = 0;
    renderDots();
    show(0);
  }

  thumbs.forEach((thumb) => thumb.addEventListener('click', () => {
    const i = visible.indexOf(thumb);
    if (i >= 0) show(i);
  }));
  if (prevBtn) prevBtn.addEventListener('click', () => show(current - 1, -1));
  if (nextBtn) nextBtn.addEventListener('click', () => show(current + 1, 1));

  // Swipe on touch screens: a mostly sideways flick of 40px or more moves one photo.
  let touchX = null;
  let touchY = null;
  if (stage) {
    stage.addEventListener('touchstart', (e) => { touchX = e.touches[0].clientX; touchY = e.touches[0].clientY; }, { passive: true });
    stage.addEventListener('touchend', (e) => {
      if (touchX === null) return;
      const dx = e.changedTouches[0].clientX - touchX;
      const dy = e.changedTouches[0].clientY - touchY;
      touchX = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) show(current + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
    });
  }
  root.addEventListener('keydown', (e) => {
    if (!e.target.closest('.gallery')) return;
    if (e.key === 'ArrowLeft') show(current - 1, -1);
    if (e.key === 'ArrowRight') show(current + 1, 1);
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
