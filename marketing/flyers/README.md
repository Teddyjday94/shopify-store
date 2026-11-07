# Print flyers

US Letter (8.5" × 11"), ready to print. Files in `out/`:

| File | What it is | Print on |
|---|---|---|
| `elsewhere-brand-flyer.pdf` | Core brand: "Currently Elsewhere." + 6 best-known products | Any printer — cream background, light on ink |
| `elsewhere-holiday-flyer.pdf` | The Christmas Collection, all 5 designs | Print shop recommended (full dark background) |
| `elsewhere-holiday-flyer-board-safe.pdf` | Same, without the pin-up and middle-finger Santa — for coffee shops, campus boards, anywhere family-friendly | Print shop recommended |

The `.png` versions are 300 dpi (2550 × 3300) for texting, emailing or posting.

## Tracking
Each QR code carries UTM tags (`utm_source=flyer`, `utm_campaign=brand_flyer` /
`holiday_flyer` / `holiday_flyer_safe`). In Shopify admin go to **Analytics → Reports →
Sessions by UTM campaign** to see how many people each flyer brought in.

## Editing
Copy, products, prices and QR links live at the top of `render.js`. Rebuild with:

    npm i qrcode   # once
    node marketing/flyers/render.js

Prices are the store's starting prices as of Nov 2026 (2XL costs a bit more). Update them here if you reprice.
