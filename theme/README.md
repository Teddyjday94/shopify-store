# Elsewhere theme

Custom Shopify theme for Elsewhere Supply Co. Paper-and-ink look, Anton + Space Mono,
shipping-label / auto-reply / tour-poster motifs.

- `sections/` — header, footer, home sections (auto-reply hero, featured collection,
  collection labels, tour dates, rich text) and the main page types.
- `templates/*.json` — which sections each page uses; all editable in the Shopify theme editor.
- `assets/` — `theme.css`, `theme.js` and self-hosted fonts (SIL Open Font License).

Package for upload: `cd theme && zip -qr ../dist/elsewhere-theme.zip assets config layout locales sections snippets templates`
