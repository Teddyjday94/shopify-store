// Elsewhere Supply Co. theme scripts: mobile menu, product gallery, variant picker, quantity.

document.addEventListener('DOMContentLoaded', () => {
  initMenu();
  document.querySelectorAll('[data-product]').forEach(initProduct);
});

function initMenu() {
  const toggle = document.querySelector('[data-menu-toggle]');
  const nav = document.getElementById('HeaderNav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
  });
}

function initProduct(root) {
  const section = root.closest('section');
  const jsonEl = section && section.querySelector('[data-product-json]');
  if (!jsonEl) return;
  const product = JSON.parse(jsonEl.textContent);

  const main = root.querySelector('.gallery__main img');
  const thumbs = Array.from(root.querySelectorAll('.gallery__thumb'));
  const idInput = root.querySelector('[data-variant-id]');
  const priceEl = root.querySelector('[data-product-price]');
  const addBtn = root.querySelector('[data-add-button]');
  const radios = Array.from(root.querySelectorAll('input[data-option-index]'));

  function showMedia(thumb) {
    if (!thumb || !main) return;
    main.src = thumb.dataset.src;
    main.srcset = thumb.dataset.srcset;
    thumbs.forEach((t) => t.setAttribute('aria-current', String(t === thumb)));
  }
  thumbs.forEach((thumb) => thumb.addEventListener('click', () => showMedia(thumb)));

  function selectedOptions() {
    const selected = [];
    radios.filter((r) => r.checked).forEach((r) => { selected[Number(r.dataset.optionIndex)] = r.value; });
    return selected;
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

  function update() {
    const selected = selectedOptions();
    selected.forEach((value, i) => {
      const label = root.querySelector(`[data-option-label="${i}"]`);
      if (label) label.textContent = value;
    });
    markAvailability(selected);

    const variant = product.variants.find((v) => v.options.every((value, i) => value === selected[i]));
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
    if (variant.featured_media) {
      showMedia(thumbs.find((t) => t.dataset.mediaId === String(variant.featured_media.id)));
    }
    const url = new URL(window.location.href);
    url.searchParams.set('variant', variant.id);
    window.history.replaceState({}, '', url);
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
