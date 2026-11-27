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
- Collection trucker hats + beanies: $27
- Sweatpants: $42 (S-XL), $46 2XL, $48 3XL (two print spots; Gildan 18200 at SwiftPOD, Black/Navy)
- Koozies: $9.99; automatic tiers 2+ $8, 4+ $7.50, 6+ $7 each (best one applies, none stack)
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
- 2026-11-27, NEW theme "Elsewhere Apparel Co. | Gallery (new theme)" (157322379425, unpublished; owner decides
  whether to publish): a from-scratch marketplace layout inspired by Threadless (layout only, nothing copied;
  the site itself couldn't be fetched from the cloud session, so it was built from knowledge of its layout).
  Source: theme-gallery/ (README there), zip in dist/elsewhere-gallery-theme.zip. Search-first header + mega menu,
  hero carousel, "Shop by product" circles, tabbed grids, collection spotlight/tiles, filter sidebar, product
  gallery grouped by color label, "Available on" style picker (design-key handles), swatches, size guide,
  koozie table, cart drawer with $60 free-shipping bar. "from <collection>" on cards = theme setting world_handles.
  Not carried over from the live theme: lookbook, set add-on / matching sweatpants card, /pages/designs template,
  Doomsday editorial and lifestyle hover photos. themeFilesUpsert with URL bodies returned success but changed
  nothing on this theme; theme_bash edits + theme_commit worked. themeCreate from a raw.githubusercontent zip works.
  Tiles (2026-11-27): Here Be Dragons = Dragonfall Hoodie back print, Female Lead = Sisterhood tee at the graffiti
  wall (block image settings in templates/index.json; product photos are usable as shopify://shop_images/<file>).
- 2026-11-27, Legends Never Die hoodie art updated in Printify (owner): Born Ready, Fallen Not Finished, Going With the
  Flow and Queen Forever hoodies were republished with images, which replaced every Shopify photo with 33 unlabeled
  mockups (8 colors x front/back/back 2nd view/folded + Printify size chart); Going With the Flow also got 18 duplicate
  imports. Fixed: photos matched to Printify mockups by image comparison (printify/match_republished_photos.py), labeled
  "<Title> in <Color>, back print / back print, second view / front print / folded" and "<Title> size chart", ordered
  Black back print first then each color (option order), chart last; every variant linked to its color's back print;
  the 18 duplicates detached from the product (files kept in Files). Old lifestyle/model photos on these hoodies were
  replaced by the republish and are gone from the products. Tees, women's tees, crewnecks etc. were not republished.
- 2026-11-27, Urban Collection emptied and hidden until real products exist: removed tags "urban" and
  "urban collection" from its 4 products (Urban Collection Sweatpants, Beanie, Painted Beanie, Trucker Hat; the
  collection's only rule is a product tag) and removed its link from the main menu. The collection itself is
  still published (this connection blocks unpublishing): owner unpublishes it in admin. To bring it back, re-tag
  products "urban" and re-add the menu link.
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
  v3 (same day, owner asked for bigger art): text designs now fill to 95% of the radius; the illustrated ones
  (Moonwood Druid, Lantern Witch, Dragonfall) cover the whole circle edge to edge. Files *-v3.png; old photos
  deleted. Not AI, Dreamscape, Chrome Globe and Groovy were missing the accessory/gift/home tags (so missing from
  Home & Accessories and Gifts Under $30); added, plus brand/brand collection on the three Elsewhere ones.
- Koozies (2026-11-18): Can Cooler bp951/pp92 (Pic The Gift), Regular + Slim, $15. Sheet folds in half: top half is
  the front, bottom half is the back rotated 180. printify/koozie_art.py centres the art on a solid colour
  (front and back alike). Three listings (printify/koozies.json): WHADID I DO?! (white, the owner's main pick),
  Not AI. Just Tired. (white text on #3a2a66), Elsewhere Groovy Retro (white). Tags accessory/gift/home put them
  in Home & Accessories and Gifts Under $30; WHADID also in Tired But Here, Groovy in Elsewhere Bound.
  Colours (owner asked): the blank is white-only and variants are just Regular/Slim, so each colour is its own
  listing ("<design> – <Colour>"), made by printify/koozie_colors.py (cloned from the original, recorded in
  koozies.json). WHADID: White/Black/Navy/Red; Not AI: Purple/Black/White (dark text)/Red; Groovy:
  White/Black/Navy/Cream. Shopify imports Printify mockups in random order, so photos were matched to Printify's
  camera views by image comparison before setting alts, order (on-a-can front first) and Regular/Slim photos.
  Price (2026-11-19): $12 each (Printify + Shopify), plus automatic discount "Koozies: 2 or more for $10 each"
  ($2 off each koozie when the cart has 2+ of the 12 koozie products; combines with free shipping only). New koozie
  products must be added to that discount. Floor math: cost $4.99 + US ship $5.59 first / $0.89 extra (own
  supplier, so never shares shipping with apparel); at $12 a lone koozie on a free-shipping order still nets ~$0.75,
  2 at $10 ~$2.70, more grows from there. Below ~$11 a single koozie loses money on free-shipping orders.
  Added 2026-11-19: "Koozies: 4 or more for $9 each" ($3 off each) and "Koozies: 6 or more for $8.50 each" ($3.50
  off each); all three tiers have productDiscounts combine off, so Shopify applies only the best. All three must get
  any new koozie product. Worst case (free shipping): 4 at $9 ~$6.40, 6 at $8.50 ~$9.20. A 20-pack via Printify
  costs ~$122 before profit (no volume pricing), too dear for buyers; real bulk ($1-3 each) would need a bulk
  printer and our own stock.
- Koozie deal on the site (2026-11-19), theme copy "Elsewhere Apparel Co. | Koozie Deals" (156906258593, unpublished;
  duplicated from the live Shop Helpers theme): products tagged "koozie" show a "Buy more, pay less" price table
  under the price (snippets/koozie-deal.liquid), and the cart drawer says how many more koozies reach the next
  price (data-koozie-tiers in snippets/cart-drawer.liquid, renderKoozieNudge in assets/mw-cart.js; counts lines whose
  handle contains "koozie"). Change both if the discount tiers change. Tested: theme-live-overrides/koozie_test.js.
- Koozie price cut (2026-11-19, later): $9.99 each; the three discounts renamed and set to $1.99/$2.49/$2.99 off each
  (2+ $8, 4+ $7.50, 6+ $7). Koozie shipping is the Printify profile "Standard: Pic The Gift, 951, 5338,Accessories":
  US $5.59 up to 0.33 lb, +$0.89 per 0.22 lb, i.e. customers pay Printify's cost. Floor: extra koozies cost ~$6.10 with
  fees, so $7 is the lowest tier; at $6.50 a 10-koozie order (free shipping at $60) loses money. Every koozie-only
  order profits (9 at $7 with free shipping ~$3.25 is the low point). A koozie in a $60+ apparel order loses ~$0.90 on
  its own shipping, covered by the apparel. The Koozie Deals theme went live with the old table; copy "Elsewhere
  Apparel Co. | Koozie Prices" (156906782881) has the new prices and must be published.
- Printify Premium: free month, active until 2026-12-18. Costs with Premium (cheapest variant): koozie $3.62 (was
  $4.99), unisex tee $9.40 (was $11.77), women's tee $8.14 (was $10.82), crewneck $13.78, hoodie $16.71, long sleeve
  $20.27, mug $4.10, ornament $4.57, desk mat $7.74, hats $10.21-15.26. Shipping is not discounted. Premium costs
  $39/mo or $299/yr; worth keeping at roughly 15-25 items/month (monthly) or 10-15 (yearly).
- Holiday Sale (automatic discount, 2026-11-19 to end of 2026-12-17 ET, endsAt 2026-12-18T04:59Z): 15% off every
  product in the hidden smart collection "holiday-sale-2026" (title does not contain "Koozie"; unpublished, so not
  shown in the store; new non-koozie products join it automatically). Koozies keep their own tiers instead. The sale
  and the three koozie tiers all have productDiscounts combining ON; checked with draftOrderCalculate: tiers do not
  stack on each other (4 koozies $30, 6 $42), tee + 6 koozies $64.95 (both apply). Ends a day before Premium so every
  sale order is printed at Premium cost. Before it ends, nothing to do; afterwards delete the collection if wanted.
- Announcement bar (theme copy "Elsewhere Apparel Co. | Holiday Sale", 156907339937, duplicated from the live Koozie
  Prices theme; to be published): messages can carry an "ends" date (YYYY-MM-DD, store time zone) and stop showing
  after it (sections/announcement-bar.liquid). Messages: "Holiday Sale: 15% off everything through Dec 17" (ends
  2026-12-17, links /collections/all), "Koozies: 6 or more for $7 each" (links koozie search), then the two old ones.
  Not browser-tested: the store's bot check blocked the test browser that day; files verified by checksum.
- Printify vs Shopify sync check (2026-11-19): compared all 179 Printify products to Shopify (variant counts, price
  range). 12 products had in-stock Printify variants missing from Shopify (likely out of stock when first published):
  Forest M/XL on Not AI, Butterfly Effect, Sunflower Soul, Color Me Bold, Crown & Curls, Pink Crown, Sisterhood tees;
  Mustard M/L on Odysseus; Navy L/2XL on Post-Credits, Dragonfall, Lantern Witch, Moonwood hoodies. Republished
  those, plus all koozies and ornaments (edited in Printify after publishing), with publish flags variants=true and
  everything else false: only adds/syncs variants, leaves Shopify titles, descriptions, tags, SEO and photos alone
  (checked). New variants then got their colour photo. Light Blue 2XL on those 4 hoodies is out of stock at the
  supplier, so it stays off Shopify. 5 older Printify-only tees (Please Respect the Plot, Stacked Books, Skeleton
  Reading Book, Read Wildly, My Happy Place; $14.99-26.79) were never published; left for the owner to decide.
- Sweatpants (2026-11-20): 12 listings, Gildan 18200 at SwiftPOD (bp 1398 / pp 39, same maker as the hoodies),
  Black + Navy only (the art has dark painted edges made for dark fabric; checked on grey/sand, looked dirty),
  S-3XL, $37/$41/$43. Cost with Premium $16.24-18.47 S-XL, $20.51-25.15 2XL-3XL (about 20-25% more without).
  Owner's art (designs/pants-2026/*.png): per collection a Bold tall design and a Subtle emblem. "<Name> Sweatpants"
  = Bold down the left thigh (1140 px wide from 120 px below the waist on the 1200x4800 left_leg_front area);
  "<Name> Emblem Sweatpants" = Subtle, 860 px wide on the upper thigh. designs/pants-2026/make_print.py builds the
  print files (drops stray source-crop fragments; hand trims for Urban, Born Ready and Elsewhere emblems).
  Female Lead first came as one small 72 dpi image (1122x1402) holding both pieces; on 2026-11-20 the owner sent
  separate cleaned files (2600x5600 / 1800x1800, same art, upscaled from that source like the other five), now in
  designs/pants-2026 and on both Printify products (variants-only republish, Shopify listing untouched). printify/create_pants.py made and
  published them (ids in printify/pants.json). Collections: Side Quest, Elsewhere Bound, Legends Never Die
  (immortalized tag, Born Ready too), Female Lead (own lane), new "Urban Collection" (tag urban) and new
  "Sweatpants" (tag sweatpants); Women's got a second source, product type Sweatpants (all 12 now in Women's). Product type set to
  Sweatpants (Printify sets Trousers). Photos are Printify's flat drawings, alts "<title> in <Colour>, front/back".
  An earlier set (create_extras.py, ELSEWHERE wordmark, $42) had been removed before this.
  Same day, owner's call: one pair per collection with BOTH designs (left sleeve / right sleeve style): Bold down
  the left thigh, emblem on the right thigh (right_leg_front, same 860 px emblem file). The 6 "Emblem Sweatpants"
  listings were deleted (Printify delete removed them from Shopify too). The second print spot adds $5.26 per pair
  with Premium (S cost $18.47 -> $23.73; about $30 after Premium), so prices went to $42/$46/$48. Republishing
  images from Printify resets product type to Trousers and clears alts: set them again afterwards.
  Later the same day (owner: bigger print, more colours): moved to Gildan 18100 POCKET sweatpants at Fulfill Engine
  (bp 6039 / pp 217, DTF, ~3.2 business days), Black + Navy + Dark Heather, S-3XL, same $42/$46/$48. Cost with
  Premium $25.18 S-XL, $28.03 2XL, $29.43 3XL (both legs printed). Print areas are 1200x4200 px per leg (~4 x 14 in
  at 300 dpi); the old 18200 was 1200x4800 (~4 x 16 in). No Printify sweatpant prints wider than ~4 in on a leg, so
  the big design stays ~3.8 in wide; the emblem went to full width (1140 px, was 860). Print files:
  designs/pants-2026/print-pocket (make_print.py pocket). Products are new Shopify ids (old 18200 ones deleted;
  ids in printify/pants_18200_retired.json). Mockups are per-leg close-ups: per colour one left-leg (full design)
  and one right-leg (emblem) image, order Black, Dark Heather, Navy; alts and variant photos set by hand.
  Ships from Fulfill Engine, so not together with SwiftPOD hoodies. Rejected: Independent Trading fleece (Army/Red/
  Royal, ~$33 cost, $52 retail), AOP joggers (polyester, $20.79 US shipping), light colours (art's dark edges).
- Set deal (2026-11-20): automatic Buy X Get Y "Hoodie + sweatpants set: 20% off the sweatpants" (DiscountAutomaticNode
  1280963117217): buy 1 from Hoodies & Sweatshirts (hoodies + crewnecks), get 20% off 1 from Sweatpants; repeats per
  pair; combines with product + shipping discounts. Scheduled to start 2026-12-18T04:59Z, when the Holiday Sale ends:
  Shopify won't discount the "buy" item with another deal, so during the sale it always lost to 15% off both
  ($11.85 vs $8.40 on a hoodie + pair). Mechanism checked with a temporary koozie-as-buy test (pair $42 -> $33.60),
  test deleted. Correction (later): a set is over $60, so we pay ~$10-11 SwiftPOD shipping; after Premium a set ($37 + $33.60) nets ~$6.80, ~$16.90 with Premium renewed (see set economics below). Sweatpants descriptions end with a "Make it a
  set" line mentioning Dec 18; a scheduled check-in on Dec 18 tests the deal and trims that line. Urban Collection
  sweatpants description no longer claims matching Urban hoodies (there are none yet).
- Announcement bar (2026-11-20): messages also take a "starts" date (shows from that day, store time zone). Messages:
  Holiday Sale (ends 2026-12-17), "New: matching sweatpants for our collections" (ends 2026-12-17, links
  /collections/sweatpants), "Hoodie + sweatpants set: 20% off the sweatpants" (starts 2026-12-18), koozies, printed to
  order, free shipping. Store is at Shopify's 20-theme limit (this connection can't delete themes), so instead of a
  new copy the unpublished "Koozie Prices" theme (156906782881; every other file checked identical to the live
  Holiday Sale theme) got the two files and was renamed "Elsewhere Apparel Co. | Set Deal": owner publishes it.
  Preview checked: today shows sale + sweatpants messages, set message hidden. Old drafts to delete in admin when
  convenient: anything older than "Holiday Sale"/"Set Deal" except as a backup.
  Owner published Set Deal (2026-11-20) and deleted a few drafts (17 themes left).
- Main menu (2026-11-20): "Sweatpants" added to Shop after Hoodies & Crewnecks; "Urban Collection" added to
  Collections (menuUpdate replaces the whole list, so all existing items are resent with their ids). Checked live.
- Sweatpants back on Gildan 18200 / SwiftPOD (2026-11-20, owner preferred its full-pants mockups over the 18100's
  per-leg close-ups): Black + Navy, S-3XL, $42/$46/$48, emblem now full width (1140 px) on the right thigh, big
  design unchanged on the left. Cost with Premium $23.73 S-XL, $28.62 2XL, $30.40 3XL. New Shopify ids again
  (8915869171873, 8915869925537, 8915870711969, 8915871269025, 8915871727777, 8915872055457); the 18100 ones are
  in printify/pants_18100_retired.json. Descriptions keep the set-deal line and the Urban wording (now built in
  create_pants.py). Ships with SwiftPOD hoodies again. Dec 18 check-in updated with the new ids.
- "Complete the set" card (2026-11-20), theme copy "Elsewhere Apparel Co. | Complete the Set" (156956229793, from the
  live Set Deal theme; owner publishes): on product types Hoodie and Sweatshirt, under Add to cart, a card linking the
  matching sweatpants (snippets/matching-sweatpants.liquid, styles in assets/mw-cart.css). Match: design name in the
  title (Born Ready), else shared tag player two / immortalized / own lane / brand collection / urban; otherwise
  "Shop matching sweatpants" -> /collections/sweatpants (Tired But Here, Here Be Dragons, Currently Elsewhere,
  Seasonal Depression). From 2026-12-18 it adds "20% off with this hoodie/crewneck". Tested in preview: Final Boss
  hoodie + No Signal crewneck -> Side Quest, Born Ready hoodie/crewneck -> Born Ready, Fallen Not Finished -> LND,
  Sisterhood -> Female Lead, Dreamscape -> Elsewhere Signature, WHADID / Dragonfall / Post-Credits -> collection,
  tees -> no card. New sweatpants designs: add their collection tag to the keys list in the snippet.
  Owner published it, then asked for an opt-in: theme copy "Elsewhere Apparel Co. | Set Add-on" (156956393633,
  from the live Complete the Set theme; owner publishes). When a match exists the card is a checkbox "Add the
  matching <pants>?"; ticking it opens the pants colour + size (size follows the hoodie's size), a price summary
  (hoodie, pants, together; until 2026-12-17 shows the Holiday Sale 15% total, from 2026-12-18 the set price with
  20% off the pants) and turns the button into "Add both to cart". assets/mw-cart.js adds both with one
  /cart/add.js items call. Gotcha: the product form has an input named "id", which shadows form.id in JS; use
  form.getAttribute('id'). Tested (theme-live-overrides/set_addon_test.js): Final Boss hoodie L + Side Quest Navy
  L -> cart has both, $67.15 = page total; unticked -> hoodie only; iPhone layout fine, no overflow.
- Set economics (2026-11-20, SwiftPOD hoodie + 18200 pants, free shipping paid by us: ~$7.99 first + $2.09 extra,
  2.9% + 30c fees; post-Premium costs estimated ~25% above Premium: hoodie ~$20.90, pants ~$29.66):
  $79 no deal ~$15 | $70.60 (20% off pants, current) ~$6.80 | 25% off ~$4.75 | 30% off ~$2.70. With Premium kept add
  ~$10 to each. Owner chose to keep 20% for now.
- Print Geek (provider 27, Canada) makes 4 hoodies: Moonwood Druid, Lantern Witch, Dragonfall, Post-Credits. US
  shipping $28.09 first item (+$3.29); Shopify profile "Standard: Print Geek, Hoodie, Sweatshirt" charges customers the
  same. Any $60+ free-shipping order with one loses ~$13-21. Fix if wanted: move them to SwiftPOD (bp 77 / pp 39,
  ~$8 shipping). Owner declined for now (2026-11-20).
- Collection hats (2026-11-20): per collection (Side Quest, Elsewhere Signature, Legends Never Die, Born Ready, Urban
  Collection, Female Lead) a "<Name> Trucker Hat" (Yupoong 6606, bp 1446 / pp 99, embroidered front 1200x675, cost
  $13.94 with Premium) and "<Name> Beanie" (Yupoong 1501KC, bp 1691 / pp 99, embroidered cuff 1500x525, $14.05), $27
  each, 7 dark colours (trucker: Black, Black/White, Navy/White, Charcoal/White, Evergreen/White, Dark Heather Grey +
  one per design; beanie: Black, Navy, Dark Grey, Spruce, Olive, Brown, Royal). Light crowns skipped (cream/gold
  thread vanishes). Art: designs/hats-2026/flatten.py turns the painted sweatpants emblems into 1-5 solid thread
  colours (drops shading and Side Quest's clouds, merges blotchy letters, removes unsewable specks) -> flat/;
  printify/create_hats.py builds print files (designs/hats-2026/print) and products (ids in printify/hats.json).
  Printify maps colours to its nearest real threads (Urban teal looks greener, BR cream more golden on mockups).
  Photos: 28 per hat (7 colours x front, back, worn front, worn back). Shopify order as imported: the 7 fronts (in
  the order of the variants' featured photos), then back / worn front / worn back per colour in that same order.
  Alts "<Title> in <Colour>, front|back|worn, front|worn, back" set via fileUpdate; the Black front moved to first
  (productReorderMedia) so cards show Black. Variant photos link correctly as imported.
- Social Club hats (2026-11-20): the owner's 7 full-colour party designs (designs/party-2026/src: Cheers From
  Elsewhere, Weekend Ritual, Pour Decisions Club, Side Quest Social Club, After Hours Only, Night Shift Social,
  Midnight Mischief) as "<Design> Trucker Hat" (OTTO foam trucker bp 1735 / pp 99, DTF front 1650x750, cost $11.50,
  8 colours: Black, Dark Navy, Black/White, Navy/White, Red, Royal/White, Hot Pink/White, Kelly/White) and
  "<Design> Beanie" (bp 5254 / pp 99, Black/Graphite/Navy, $11.17), $27 each. printify/create_party_hats.py, ids in
  printify/party_hats.json. Smart collection Social Club (handle social-club, tag "social club", Collection
  337979244705), in the Collections menu. Trucker photos: 32 (8 fronts, then per colour side / worn / worn second
  model); alts set, variant photos linked by Printify, Black first. Other DTF-printable caps exist (Richardson
  printed truckers bp 5596 with 24 colours, at Fulfill Engine pp 217) if more colour choice is wanted.
- Painted beanies (2026-11-20, owner: "incorporate our actual designs"): "<Name> Painted Beanie" x6, the painted
  emblems unsimplified, DTF-printed on Port Authority C939 100% Cotton Beanie (bp 5254 / pp 99, front_dtf 1500x900,
  no cuff), Black/Graphite/Navy only, $27, cost $11.17, US ship $5.09. Sold ALONGSIDE the embroidered beanies (owner's
  call). printify/create_painted_beanies.py; art from designs/pants-2026/print/<slug>-subtle.png (the trimmed files:
  the raw ones have paint flecks that showed on Born Ready + Urban, fixed by an images-only republish). 3 flat
  mockups each (import order Graphite, Black, Navy); alts "<Title> in <Colour>, front", Black moved first. Printify
  sometimes doesn't link variant photos on first import: link with productVariantAppendMedia. Other printed beanie:
  none (all other Printify beanies are embroidery-only; AS Colour 5385 'front' is embroidery too).
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

- Tapstitch (2026-11-21, app installed by owner; no API from here, products are made in the Tapstitch app).
  tapstitch.com added to the environment allowlist; its pages embed Nuxt data (decode with __NUXT_DATA__ refs) with
  blankPrice / sidePrice (per print area) / printAreaList / fulfillmentInfoList (country CN or US) / colorList.
  'monthlySales' is a placeholder (250 everywhere). Rates API (api.service.tapstitch.com) not allowlisted; US
  shipping per reviews ~$5.50-6 first item + ~$2 each extra. US print area $3.49, China $2.99.
  US (LA, ~5-7 days) sets: Oversize Fleeced Hoodie R00286 ($14.92, 24 colours, DTF/embroidery, front/back/sleeves)
  + Solid Color Fleece Straight Leg Pants R00363 ($15.76, 9 colours, DTF); 8 shared colours. Fleeced Sweatshirt
  R00368 pairs with the same pants. Women's US set: Mock-Neck Crew WW0004 ($16.99) + Sweatshorts WK0004 ($12.99),
  18 colours, S-L. All jackets and the heavyweight/vintage-wash sets are China-only. Denim jacket UT0142: $29.99,
  440 gsm, Black/Blue/Navy, DTG or embroidery, front+back 40x52 cm, China only.
  Owner's plan: fleece set (US) + denim jacket for Legends Never Die, Urban Collection, Side Quest. Update: set
  hoodies carry the artwork from our tops (owner): 10 '<Design> Fleece Hoodie' (Legends: Born Ready, Fallen Not
  Finished, Going With the Flow, Queen Forever, back poster + chest mark; Side Quest: Main Character Syndrome, No
  Signal, I Paused My Game, My Other Outfit Is Also Black, Out of Orbit, Final Boss Energy, back art + Side Quest
  hearts emblem on chest) + Urban Collection hoodie (street-scene art, no tops yet); 3 '<Collection> Fleece Joggers'
  (emblem); 3 denim jackets. 17 products. Files: designs/tapstitch-2026/hoodies/<design>/ (backs capped 4000 px wide
  / 4700 tall for upload size). Zips in media/tapstitch-*.zip (gitignored). Print files:
  designs/tapstitch-2026/make_files.py (-dtf: soft paint flattened on black + hard edges for DTF; -dtg: original);
  GUIDE.md has placements, colours (Black/Navy/Gray Coffee/Eden Green for fleece), titles (<Name> Fleece Hoodie,
  <Name> Fleece Joggers, <Name> Denim Jacket) and prices ($49 / $42 / $79). Pending: owner creates them in the app,
  then descriptions, alts, collections, add-on (joggers vs Printify sweatpants) and set deal on the Shopify side.

- Varsity jackets (Tapstitch/ODMPOD, made by owner 2026-11-22): 10 live '<Design> Varsity Jacket' = Two-Tone Fleeced
  Varsity RQ0001 ($24.99 + 3 areas x $2.99 = $33.96; ~$10.30 shipping from China; 0.81 kg), $47; 10 draft '<Design>
  Blue Varsity Jacket' = Raglan RQ0006 ($22.99 + 3 x $2.99 = $31.95; ~$7.40 shipping). Store shipping: $8, free
  at $70+. At $47 with the 15% sale and free shipping a jacket lost ~$5.80. 2026-11-23: owner removing the
  collection logo (keeps back print + Elsewhere logo) -> 2 areas, $30.97; then price $44 (~$8.90 on a normal order).
  Holiday Sale collection now excludes title 'Varsity Jacket' (second DOES_NOT_CONTAIN condition); 5 jackets had
  been manually included in the sale source and were removed from its inclusion selections (manual inclusions
  override conditions). All 20 jackets set to product type Jacket. Tapstitch set drafts exist (owner): 11 '<Design>
  Fleece Hoodie' at $37 (cost $20.89 US) and 3 '<Collection> Fleece Joggers' at $42 ($17.74); not yet published.
- 2026-11-23: collection logo removed (owner) -> fleeced varsity cost $30.96, raglan drafts $28.96. All 10 live
  fleeced varsity jackets set to $45 (240 variants): ~$10.70 profit when the customer pays $8 shipping, ~$3.10 on
  a free-shipping order. Blue raglan drafts still at $47, unpublished.
- 2026-11-23: Blue raglan varsity drafts (10) set to $45, given custom descriptions (design story, raglan fabric, size chart,
  dotted print texture note, 1-2 week shipping) and tags (varsity jacket + 'drop 004'/'immortalized' for Legends or
  'player two'/'side quest' for Side Quest). Still DRAFT pending owner's go-ahead. Live fleeced jackets have no tags
  (not in their design collections).
- 2026-11-23: Blue raglan varsity jackets published (Online Store). Live fleeced jackets tagged (varsity jacket, fleece
  lined jacket + collection tags) so all 20 show in Legends Never Die / Side Quest; generic Tapstitch descriptions on
  Born Ready, Fallen Not Finished, Going With the Flow, Queen Forever, Main Character Syndrome replaced (the other five
  already had custom ones, kept).
- 2026-11-23: Tapstitch fleece set published: 11 '<Design> Fleece Hoodie' ($37, type Hoodie, tags hoodie/fleece hoodie/
  matching set + collection tags) and 3 '<Collection> Fleece Joggers' ($42, type Sweatpants, tags sweatpants/joggers/
  fleece joggers + collection tags); new descriptions with size charts. Costs show China fulfilment (hoodie $20.89 =
  14.92 + 2 x 2.99; joggers $17.74), so descriptions say 1-2 weeks. In the Holiday Sale. Known gap: the theme's
  matching-sweatpants card on fleece hoodies points to the Printify '<Name> Sweatpants' (title/tag match), not the
  Fleece Joggers; fix needs a snippet change (prefer 'fleece joggers' for 'fleece hoodie') in a theme copy.
- 2026-11-23 (later): owner no longer wants the fleece set; all 14 Fleece Hoodies/Joggers set back to DRAFT (not deleted).
- 2026-11-23 (later): owner asked to delete the fleece set; all 14 Fleece Hoodies/Joggers deleted from Shopify. If
  Tapstitch re-syncs them, remove the designs in the Tapstitch app.
- Doomsday Drop (2026-11-25 to 2026-12-17, limited): the owner's 8 designs, cleaned (no franchise marks, logos,
  titles or names anywhere: the originals in designs/doomsday-2026/src are gitignored and must never be sold),
  Kittl 4x upscales keyed to transparent (designs/doomsday-2026/print, prep.py), 303-382 DPI. 8 Black tees
  (Bella+Canvas 3001 / pp 29, front, $27, cost $9.40-11.49) + 8 Black hoodies (Gildan 18500 / SwiftPOD pp 39, back,
  $37, cost $16.71-18.31), S-2XL. printify/create_doomsday.py, ids in printify/doomsday.json. Tags "doomsday drop",
  "limited drop". Smart collection Doomsday Drop 338393530529 (tag), published, top-level Main menu item.
  2026-11-25: Doomsday Mask + Tree Spirit tee/hoodie deleted (owner); A Stolen Life added; Doomsday Incursion deleted (owner) -> 12 products. King of the 3 Realms: hood
  added, horns removed, then the stone throne swapped for an original throne forged from swords (not the HBO Iron
  Throne shape; owner sent that as the reference). Grimhold Crest (renamed L Crest 2026-11-25, handles l-crest-tee/-hoodie with redirects): big silver L instead of the three horns; "Grimhold" word removed (2026-11-25), just the L.
  Later on 2026-11-25 the owner switched the L to a big D everywhere: D Crest Tee / D Crest Hoodie (handles
  d-crest-tee/-hoodie, redirects from l-crest-*), art designs/doomsday-2026/print/crest-D.png, plus a new Tapstitch
  D Crest Varsity Jacket (green with white, $47, live) and a "Crest feature" band at the top of the live homepage.
  See designs/doomsday-2026/D-CREST.md.
  Included in the Holiday Sale (storewide 15%). Owner extended the drop through Dec 18 (2026-11-25). Ends via a
  send_later reminder at 00:05 ET Dec 19 (trig_01V5TysCN6Z4vFrFiSue9wef): products to draft, menu item removed,
  collection unpublished. Homepage: section limited-drop (sections/limited-drop.liquid, first on templates/index.json,
  countdown to the end of its 'ends' date, hides itself after; big image = Files doomsday-drop-hero.jpg) + an
  announcement message ending 2026-12-18, both on theme copy "Elsewhere Apparel Co. | Doomsday Drop" (157190258849,
  duplicated from the published No Denim; owner publishes). Tried on No Denim first and reverted: No Denim carries
  other committed-but-unpublished edits (denim-set, main-product, product-card, theme.liquid, lookbook...) not made
  by this session, so publishing it would ship those too.
  White + green skin (2026-11-25, owner asked for the limited run): assets/doomsday-skin.css loaded last in
  layout/theme.liquid of the Doomsday Drop copy only; overrides the dark surfaces (header, bars, cards, product page,
  filters, lookbook, the Doomsday band) to off-white #f7f8f3 / ink #0f1a12 / green #128a3a / acid #8dff3a; photo
  tiles and the hero film keep their dark art. After the drop, the owner republishes a regular theme (No Denim).
  Product + collection copy now say 'until December 18' / 'Six designs'.
  Hoodies: back-print photo moved to first (Printify puts the blank front first).
