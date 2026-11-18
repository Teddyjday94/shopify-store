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

## Sleeve test drop (2026-11-13)
- Horror Club, No Signal (Rise From Ruin removed 2026-11-14): Long Sleeve Tee (Gildan 2400, front + both sleeves, $37, cost $26.63)
  and Sleeve Edition Hoodie (Gildan 18500, back + both sleeves, $47, cost $35.79), SwiftPOD, Black only.
- Each sleeve print adds about $6.50. Lettering: designs/sleeves (designs/src/render_sleeves.js);
  products: printify/create_sleeve_drop.py, printify/sleeve_drop.json.

## Designs removed (2026-11-13)
- Deleted (Printify + Shopify, all product types): the whole Inner Monologue collection (13 designs, 65
  products; collection the-relatable-collection deleted and removed from the main menu); Side Quest:
  Forbidden Knowledge, Talk Nerdy to Me, PhD in Overthinking, Critical Failure; Creature Feature: Sweet
  Dreams Are Cancelled, Sweet Dreams Don't Live Here, Horror Movies Raised Me, Sleep Deprived & Horror
  Obsessed, Sleep Is for People Without Nightmares; Here Be Dragons: Midnight Leap, Rain on the Gargoyle,
  My Origin Story Is Mostly Bad Decisions, Happily Ever After? Hard Pass.; Legends Never Die: One Way
  Ferry, Above It All, Lead the Charge; Tired But Here: Systems Still Functional, A Quieter Mind, Same
  Mind Brighter Days. 114 products total.
- 2026-11-14: also deleted Long Live the King, Sleep Paralysis Club and Rise From Ruin (13 products,
  including the Rise From Ruin long sleeve and Sleeve Edition hoodie from the sleeve test drop).
  Masterless (tee, women's tee, hoodie) deleted the same day.
  Also deleted: In My Own Lane, Lucky Charm, Respawn Pending (tee, women's tee, hoodie each), Resting Witch
  Face Tee, This House Eats People Tee. Side Quest tile moved to No Signal.
- 2026-11-17: the whole Creature Feature collection deleted (handle horror-collection; Printify + Shopify):
  Horror Club (tee, long sleeve, hoodie, Sleeve Edition hoodie), Dead Tired, Dead Inside Dressed to Kill,
  I Came. I Screamed. I Left. (tee + hoodie each), Don't Open the Basement Tee. 11 products. Its menu link went
  with the collection; its homepage tile hides itself (the grid now shows three tiles, numbered 01/03/04).
  Promo pack rebuilt without them. Its tile was replaced by Elsewhere Bound (see Themes).

## Product photos and promo pack (2026-11-16)
- Every tee and women's tee got Printify model and hanging shots (alts "... in <Color>, on a model" / "hanging").
  Women's tees open on the model shot (fixes the boxy flat look of the Gildan 5000L photo); since
  2026-11-17 tees open on a model shot too (the man; back view for back-printed tees), so phones show people.
- Back-printed designs (Final Boss Energy, Out of Orbit, My Other Outfit Is Also Black, I Paused My Game,
  Main Character Syndrome, No Signal) use back-view model shots on tees; their women's tees keep the flat
  back shot (Printify has no back model shot for the 5000L).
- Printify mockup camera ids: tee (Bella+Canvas 3001) front 102044, back 102045, folded 102046, hanging 102047,
  chair 102049, pairs 102051-102053, models front 102057/102059/102061, models back 102054/102058/102060;
  women's (Gildan 5000L) front 87728, back 87729, hanging 87730, flat lay 87731, model 87732; hoodie
  (Gildan 18500) front 98424, back 98425, back-2 98426, models (front only) 98427-98430.
- Product page gallery (theme-live-overrides/assets/theme.js + mw-gallery.css, copy "Swipe Gallery"
  156788424865, waiting for the owner to publish): a photo labeled "<Title> in <Color>, <anything>" joins
  that color's gallery, so model/hanging shots show; swipe, arrows and dots step through them.
- Female Lead (tag "own lane") is women's tees + hoodies only: the six unisex tees lost the tag 2026-11-17.
- More model shots: Printify has none beyond the ids above (tee 102062 = second woman, back view, added to
  the six back-printed tees as "on a model, back view 3").
  Kittl has hundreds of hoodie/tee model mockups but the account is on the free plan: premium templates
  (incl. Gildan 18500 back views) won't render; the free hoodie ones (#46, #181, #798) are front views only.
- Promo pack: media/promo/<design>/ (337 shots, 37 designs, 2048 px), rebuilt by printify/promo_pack.py.

## Brand collection (2026-11-16), renamed Elsewhere Bound 2026-11-17
- 2026-11-17: renamed "Elsewhere Bound" (handle elsewhere-bound; /collections/brand redirects), caption
  "Wear the destination.", menu item renamed. Still driven by the tag "brand collection" (scripts use it).
- Collection "Brand" (handle brand, auto by tag "brand collection"), in the main menu under Collections.
- Five Elsewhere Apparel Co. logo designs from the owner: Psychedelic Drip, Groovy Retro, Chrome Globe,
  Ransom Note, Chrome Script. Each: tee $27, women's tee $27, hoodie $37 (back print), Black only.
- Sources were phone screenshots (designs/logo-src); upscaled 4x, background cut out with
  designs/src/logo_cutout.py (--pockets also clears paper trapped inside the art), 4500 px longest side =
  15 in at 300 DPI (designs/print-brand). Raw upscales (designs/logo-up) are git-ignored.
- Products: printify/create_brand.py, ids in printify/brand.json.
- 2026-11-17 batch 2: Elsewhere Graffiti and Elsewhere Dreamscape (tee, women's tee, back-print hoodie;
  printify/create_brand2.py). Dreamscape art came in at 1145x1374 and was upscaled 4x.
- WHADID I DO?! (owner's art; the first version had the Tune Squad logo on the jersey and was not used):
  Tired But Here (tag "drop 002"), tee, women's tee and hoodie, printify/create_whadid.py, ids in printify/whadid.json.
- Hoodies & Sweatshirts and Brand are sorted by hand (MANUAL); Brand is grouped by design (tee, women's tee,
  hoodie). New products land at the end of manual collections, so reorder them after each drop.
- Photos for new products: printify/photo_mutations.py PROGRESS.json OUT.graphql [slug prefixes].
- Hats collection now matches tag "hat" only; its old title rule (contains Hat/Cap/Beanie) caught
  "Dreamscape".
- 2026-11-17: front-print hoodie versions (Printify's hoodie models) were added, then removed the same day
  at the owner's request: back print is the only hoodie. Currently Elsewhere Hoodie (always front print) keeps
  Printify's four hoodie model shots, one as its main photo.

## More shirt colors (2026-11-17)
- 38 single-color products got more colors, same price per size, same art and placement
  (printify/add_colors.py; results in printify/colors.json):
  tees + Navy, Dark Grey Heather, Maroon, Forest, Military Green; women's tees + Navy, Purple
  (the four White women's tees + Light Pink); hoodies + Navy, Dark Heather, Maroon, Forest Green, Dark Chocolate.
- Sleeve Edition hoodies stay Black (their sleeve lettering was made for black).
- Each new color has a labeled flat photo ("<Title> in <Color>, front/back print") so the gallery switches
  with the color picker (printify/color_photos.py OUT.graphql --need-black ...). Older listings whose
  original photos had no color label also got a labeled photo in their original color.

- 2026-11-17: hoodie back prints made as big as SwiftPOD's 14 x 16 in back area allows (full width, or full
  height for tall art; top-aligned) on all 32 hoodies: printify/enlarge_hoodie_backs.py, log in
  printify/hoodie_backs.json. The labeled "back print" photos were swapped in place with fileUpdate
  (printify/hoodie_back_photos.py). The 178 older launch photos on 18 hoodies (unlabeled or description-only)
  were matched to their Printify mockup by thumbnail and swapped the same way (printify/hoodie_launch_photos.py,
  matches in printify/hoodie_launch_matches.json). Every hoodie photo now shows the current print size.

## Christmas line removed (2026-11-13)
- Deleted all 60 Christmas products (batch 1: Naughty List Again, Suck It Up Buttercup, Bring Bourbon,
  Gift Is Me, Holly Jolly Chaos; batch 2: the six added 2026-11-13) from Printify and Shopify, plus the
  Naughty List collection (handle the-christmas-collection) and its main-menu link. Homepage tile hides
  itself when the collection is missing. Art and scripts stay in the repo (designs/xmas2-src, create_xmas2.py).

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
- Homepage world tiles (2026-11-12, copy "Tile Media" 156570779809, live 2026-11-13): Legends Never Die =
  looping Rise From Ruin video, Creature Feature = Horror Club photo, cropped centered (media/homepage/).
- 2026-11-14, copy "Born Ready Tile" (156638544033), waiting for the owner to publish: Legends tile = Born Ready
  painting (media/homepage/elsewhere-legends-born-ready.jpg, no video; Rise From Ruin was deleted), and the
  empty Naughty List block removed. Side Quest tile = No Signal art on dark (media/homepage/
  elsewhere-side-quest-no-signal.jpg, art right of center so it clears the tile label on phones and fits the
  square desktop crop); Respawn Pending was deleted.
- 2026-11-17, copy "Elsewhere Bound Tile" (156797599905, from live Swipe Gallery), waiting for the owner to
  publish: the Creature Feature tile (World / 02) became Elsewhere Bound, using the owner's campaign photo
  (Chrome Globe tee at a bar; original media/homepage/source-elsewhere-bound-chrome-globe.jpg, cropped to
  head-to-logo as elsewhere-bound-chrome-globe.jpg in Shopify Files).
- 2026-11-17, copy "Cart Drawer + Quick View" (156798746785, from live Elsewhere Bound Tile), waiting for the
  owner to publish: slide-out cart and product quick view, written from scratch in the Field Guide style
  (inspired by the paid Omega theme's features, nothing copied). Files: snippets/cart-drawer.liquid,
  assets/mw-cart.js, assets/mw-cart.css, snippets/product-card.liquid (card is now div.card holding
  a.card__link + button.card__quick), layout/theme.liquid (css/js/render hooks). All in theme-live-overrides/.
  Every /cart/add form adds in place and opens the drawer; the header Cart link opens it (still /cart without JS
  and on the cart page). Quick view reads /products/<handle>.js, uses the "<Title> in <Color>, ..." photo labels,
  starts on the main photo's color. Drawer shows each line's color photo (new-color variants have no variant
  image, so checkout still shows the product's main photo for them). Browser test: theme-live-overrides/qv_test.js.
  Theme files can be pushed with themeFilesUpsert body type URL pointing at raw.githubusercontent.com/<commit>.
- 2026-11-17, owner's promo photos (media/promo-photos/, 25 shots; posters keep text and stay off the site):
  * Product galleries (live): 30 lifestyle photos on 14 products, labeled "<Title> in <Color>, worn ..." (no
    "print" in the label, so the gallery treats them as extra shots of that color) and moved to position 2,
    which also makes them the card hover image. Elsewhere Dreamscape/Graffiti/Chrome Globe/Groovy Retro/Ransom
    Note tees, Graffiti + No Signal hoodies, Main Character tee, Sisterhood/Sunflower Soul/Crown & Curls tees
    (women's in White, unisex in Natural/White). Skipped: shots showing a print on the wrong side for what we
    sell (No Signal and Main Character tees are back prints; the trio's front-print Graffiti hoodie) and My
    Social Battery (no product). Note: elsewhere-drip_tee-woman-street.png actually shows the Dreamscape tee.
  * Collection banners (live, collection.image is the header background): Side Quest, Hoodies, T-Shirts, Men's
    use wide crops centered on the print (media/promo-photos/banners/); Elsewhere Bound and Women's use full shots.
  * Homepage "Worn elsewhere" lookbook (sections/mw-lookbook.liquid, 8 looks linking to products) is in the
    "Cart Drawer + Quick View" theme copy, waiting to be published with the drawer.
- 2026-11-17, browsing by design (in the "Cart Drawer + Quick View" theme copy, waiting to be published):
  * Designs are matched by handle: <design>-<style> (born-ready-tee, -womens-tee, -hoodie, -crewneck,
    -long-sleeve-tee, -sleeve-edition-hoodie, -mug, -dad-hat, -trucker-hat, -bucket-hat, -cuffed-beanie, -beanie,
    -desk-mat, -ornament, -sticker, -poster, -tote-bag, -phone-case). snippets/design-key.liquid holds the list;
    NEW PRODUCT TYPES MUST USE ONE OF THESE SUFFIXES (or be added there and in snippets/style-switcher.liquid,
    which may hold at most ~18 because a page can look up only 20 products by handle).
  * Product pages: "Choose your style" row under the price (snippets/style-switcher.liquid, in main-product).
  * Page /pages/designs ("Shop by design", template page.designs, sections/main-designs.liquid): each design once,
    grouped by Elsewhere Bound, Legends, Side Quest, Here Be Dragons, Female Lead, Tired But Here, then the rest;
    filter chips by style (?style=hoodie etc). The page exists live with a fallback text until the theme is
    published. "Shop by design" is added to the Shop dropdown by the theme copy's header (not the menu), so it
    appears only with the new theme.
- 2026-11-17: the crewnecks (Gildan 18000, created by the "Shopify product research" session) reached Shopify
  with no photos although Printify had mockups. Added 293 labeled photos with printify/fix_missing_photos.py
  (per color "<Title> in <Color>, front print", plus back view + folded for the main color), sent as batched
  productUpdate calls (bulkOperationRunMutation is blocked on this connection). The other session also began
  adding crewneck photos, so 7 crewnecks (Chrome Script, Ransom Note, Chrome Globe, Groovy Retro, Psychedelic
  Drip, Moonwood Druid, Lantern Witch) briefly had a second set; that session removed its copies (checked:
  one set per crewneck, all READY; 4 light-color crewnecks keep one extra "in Gold, folded" shot).
- 2026-11-17: theme copy "Elsewhere Apparel Co. | Shop Helpers" (156808577185, unpublished) adds to product pages:
  a "Size guide" link + dialog by the Size option (snippets/size-guide.liquid; charts in Shopify Files
  size-chart-*.jpg from Printify: Bella+Canvas 3001 tee, Comfort Colors for Odysseus, Gildan 2400 long sleeve,
  18500 hoodie, 18000 crewneck; women's tees have no chart from Printify so no link), a sticky "Add to cart" bar
  on phones once the main button scrolls away, and "Complete the look" (sections/mw-recs.liquid, loaded by
  assets/mw-product.js from /recommendations/products?intent=related; skips other styles of the same design).
  Tested in preview: right chart per garment, 4 recs shown, sticky add opens the cart drawer.
- Free shipping: the automatic discount "Free US shipping over $60" (active since 2026-10-30, US only, combines with
  other discounts) makes the $60 banner true, whatever the shipping profiles charge. The Shop Helpers theme copy shows
  a "$X away from free US shipping" bar in the cart drawer (threshold 6000 cents in snippets/cart-drawer.liquid;
  change it there if the discount changes).
- Variant photos (printify/variant_photos.py, 2026-11-17): every variant now has its own colour's photo, so checkout,
  order emails and the cart show the colour the shopper picked (2,216 variants on 102 products; checked one by one with
  printify/variant_photos_check.py, and a rescan finds none left). New colours added later need the script run again.
  This connection caps a mutation at 16KB of query text, so printify/variant_photos_vars.py turns the batches into
  GraphQL variables (the IDs go in variables, not the query).
- Colour range (2026-11-17): 150 colours added to 91 apparel products so every design has 4+ colours with a
  lighter or mid-tone option and a colour pop where the art allows. printify/color_plan.py checks each design's print
  art against each shirt colour (contrast) and color_plan.json holds the result; hand overrides in MANUAL for designs
  whose thin white caption/title vanishes on light shirts (Fallen Not Finished, Going With the Flow, Queen Forever,
  Born Ready, No Signal, Seasonal Depression: they get deep pops like Purple/Royal/Team Purple instead) and for
  Ransom Note (red letters fade on Red). "My Other Outfit Is Also Black" keeps its range on purpose.
  apply_color_plan.py enables the colours in Printify (variants only, so neck-label text layers survive), then
  new_color_photos.py adds one labeled photo per colour and variant_photos.py links all 754 new variants to it
  (checked one by one). Result: 135 of 137 apparel products have 4-11 colours (the two at 2 are My Other Outfit).
  Contact sheet of the light pairings: media/color_readability_check.jpg.
- Ornaments (2026-11-18): the 9 graphic-design ornaments (Not AI, Dreamscape, Chrome Globe, Groovy Retro,
  Psychedelic Drip, Post-Credits, Moonwood, Lantern Witch, Dragonfall) were square art on flat black, so the round
  ornament cut off the edges and showed black around the design. printify/ornament_art.py now scales each design so
  every visible pixel sits within 85% of the circle's radius (nudged down, clear of the hanging hole) on a blurred
  glow of the design's own colours; Not AI uses white text on a dusk-purple gradient. Art in media/ornaments/,
  uploaded to Printify (printify/ornament_v2_done.json) and the Shopify photos replaced with the new mockups.
  The 4 painting ornaments (Queen Forever, Going With the Flow, Fallen Not Finished, Born Ready) already fill the
  circle and were left as they were.
- Koozie options in Printify (checked 2026-11-18, cost before shipping; US shipping first item):
  Can Cooler bp951 (Pic The Gift, regular + slim, edge-to-edge print) $4.99, ship $5.59;
  Can Cooler Sleeve bp636 (neoprene, front+back) $7.92, ship $5.59; Slim Can Cooler bp808 $9.28, ship $5.89;
  Can Holder bp355 (stainless, vacuum insulated, 12oz) $19.70, ship $6.19;
  Polar Camel Slim Beverage Holder bp1518 (stainless, 16 colours) $22.63, ship $6.79. Stubby Cooler bp1329 is AU-only.
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
