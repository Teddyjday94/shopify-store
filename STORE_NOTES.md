# Elsewhere Apparel Co. — store notes

Facts worth remembering between sessions. Update as things change.

## Store
- Name: Elsewhere Apparel Co. ("Apparel for other realities")
- Domain: **elsewhereapparelco.com** (bought 2026-11-10; primary domain in Shopify, SSL on)
- Shopify admin domain: g05ctr-0g.myshopify.com (storefront also answers at elsewheresupplyco.myshopify.com)
- Fulfillment: Printify (shop id 29509655), synced to Shopify

## Pricing (all prices end in 7; 2XL same price as other sizes)
- Tees (unisex and women's): $27
- Hoodies: $37
- Hats, beanies, phone cases: $27
- Mugs, ornaments: $17
- Desk mats: $27 / $37 / $47 by size
- Posters: removed from the store (2026-11-10)
- Discount codes: none (ELSEWHERE15 / MANYWORLDS15 deleted 2026-11-10)
- Automatic discount: free US shipping on orders $60+

## Orders
- Printify order approval: automatically after 1 hour (set 2026-11-10). Returns page says cancel within 1 hour.
- First sale #1001 (2026-11-10): Born Ready Women's Tee, $27 + $4.95 shipping. Printify charged $21.10 item
  (front+back print) + $5.35 shipping + $2.47 sales tax; Shopify fee $1.23; profit about $1.80.

## Collections
Renamed 2026-11-10 (old name -> new):
Relatable -> Inner Monologue, Player Two -> Side Quest, Horror -> Creature Feature, Realms -> Here Be Dragons,
Christmas -> Naughty List, Immortalized -> Legends Never Die (incl. Old Gods), Own Lane -> Female Lead, Drop 002 -> Tired But Here.
Handles still old (the-relatable-collection, player-two, horror-collection, realms, the-christmas-collection,
the-immortalized-collection, own-lane, drop-002) until the "Garden Video" theme is published; then switch to
inner-monologue, side-quest, creature-feature, here-be-dragons, naughty-list, legends-never-die, female-lead,
tired-but-here with redirects, and hide the duplicate "Immortalized" (handle immortalized, a subset) with a redirect.
Product tags (e.g. "relatable collection", "horror collection") drive scripts; leave them.
Shop categories: Men's, Women's, Tees, Hoodies, Hats & beanies, Home & Accessories.

## Art notes
- Legends Never Die paintings (designs/src/render_drop4.js -> designs/print-drop4) read
  "ELSEWHERE APPAREL CO. · LEGENDS NEVER DIE"; hoodie chest mark "ELSEWHERE / LEGENDS NEVER DIE" (2026-11-10).
- Shopify sometimes fails to fetch fresh Printify mockups (status FAILED); check media status after swaps and re-add.

## Retired designs (do not recreate)
My Kind of Leg Day, Built Character, Currently Avoiding, Nine Tails (Printify would not publish its art),
Monster of the Week (held: resembles a trademarked character).

## Themes
- Live theme (2026-11-12): "Hero Video Preview" (156465922209), the Field Guide design, built outside this repo.
  Only the files in theme-live-overrides/ are stored here. theme-cinematic/ is the older design.
- Fonts: Anton (big headings), Barlow Semi Condensed (supporting text, card titles), Inter Tight (body),
  IBM Plex Mono (labels). Instrument Serif was dropped 2026-11-12 in copy "New Fonts" (156527263905, now live).
- Homepage world tiles (2026-11-12, copy "Tile Media" 156570779809): Legends Never Die = looping Rise From Ruin
  video, Creature Feature = Horror Club photo, both cropped centered on the artwork (media/homepage/).
- Shopify caps a store at 20 themes and this connection can't delete themes; the owner removes old drafts in admin.

## Conventions
- Theme edits: the live theme can't be written directly; duplicate it, edit the copy, and the owner publishes.
- Tees are front-print only (2026-11-10: the 22 Legends Never Die tees had painting on back + front emblem;
  painting moved to the front). Unisex cost $11.77 (2XL $14.38), all $27.
- Women's tees: Gildan 5000L at SwiftPOD (blueprint 466, provider 39) since 2026-11-10, art filling the
  ~14x16 in area; cost $10.82 (2XL $13.19), $27. Colors: Black, Navy, Red, White, Light Pink.
  Was Next Level 3900 (Monster Digital), whose ~10x12 in area kept the art small. See printify/move_womens.py.
- Hoodie product photos: labeled "<Title> in <Color>, back print" so cards and galleries show the design first.
- Homepage hero video: Garden cinemagraph loop (Artlist 5s clip locked to the still with media/video/cinemagraph.py; only moving areas come from the clip), Shopify Files elsewhere-garden-loop-v2.mp4/.webm; source in media/video/. Toggle in the hero section settings.
- Printify limits publishes (~75 in a burst); scripts pace and retry.
