// Elsewhere Apparel Co. product page helpers (2026-11-17): sticky add-to-cart bar on phones, size guide dialog,
// "Complete the look" recommendations. Markup in sections/main-product.liquid, snippets/size-guide.liquid,
// sections/mw-recs.liquid; styles in assets/mw-cart.css.
(() => {
  const product = document.querySelector('[data-product]');
  if (!product) return;

  // ---------- size guide ----------
  const sizeDialog = document.querySelector('[data-size-dialog]');
  if (sizeDialog && typeof sizeDialog.showModal === 'function') {
    document.addEventListener('click', (e) => {
      if (e.target.closest('[data-size-open]')) { e.preventDefault(); sizeDialog.showModal(); }
      else if (e.target.closest('[data-size-close]') || e.target === sizeDialog) sizeDialog.close();
    });
  }

  // ---------- sticky add-to-cart bar (shown once the real button scrolls out of view) ----------
  const bar = document.querySelector('[data-sticky-buy]');
  const addBtn = product.querySelector('[data-add-button]');
  if (bar && addBtn && 'IntersectionObserver' in window) {
    const barBtn = bar.querySelector('[data-sticky-add]');
    const barPrice = bar.querySelector('[data-sticky-price]');
    const price = product.querySelector('[data-product-price]');
    const sync = () => {
      barBtn.disabled = addBtn.disabled;
      barBtn.textContent = addBtn.textContent.trim();
      if (price) barPrice.innerHTML = price.innerHTML;
    };
    sync();
    new MutationObserver(sync).observe(addBtn, { attributes: true, childList: true, characterData: true, subtree: true });
    if (price) new MutationObserver(sync).observe(price, { childList: true, subtree: true, characterData: true });
    new IntersectionObserver(([entry]) => {
      const past = !entry.isIntersecting && entry.boundingClientRect.top < 0;
      bar.classList.toggle('is-shown', past);
      bar.setAttribute('aria-hidden', String(!past));
      barBtn.tabIndex = past ? 0 : -1;
    }).observe(addBtn);
  }

  // ---------- "Complete the look" ----------
  const recs = document.querySelector('[data-recs]');
  if (recs) {
    const load = () => fetch(recs.dataset.url)
      .then((r) => (r.ok ? r.text() : ''))
      .then((html) => {
        const found = new DOMParser().parseFromString(html, 'text/html').querySelector('[data-recs-loaded]');
        if (found) recs.replaceChildren(found);
      })
      .catch(() => {});
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); load(); } }, { rootMargin: '600px 0px' });
      io.observe(recs);
    } else load();
  }
})();
