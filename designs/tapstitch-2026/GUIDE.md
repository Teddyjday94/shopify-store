# Tapstitch: matching fleece sets + denim jackets

Make these in the **Tapstitch app** (Shopify admin > Apps > Tapstitch > Catalog). When you're done, tell Claude:
it finishes the Shopify side (descriptions, photo labels, collections, the matching-joggers add-on, the set deal).

**17 products in all:**
- 11 set hoodies: the 10 designs from our tops, plus Urban Collection.
- 3 joggers, one per collection.
- 3 denim jackets.

## 1. Set hoodies: Oversize Fleeced Hoodie (R00286), same for every hoodie
- **Fulfilment: choose US (Los Angeles)**, about 5-7 days to US customers. Method: DTF.
- Colours: **Black, Navy Blue, Gray Coffee, Eden Green** (dark only: the art has light type and painted edges).
- Price: **$37**, same as our other hoodies (owner, 2026-11-21). Cost $20.90 front + back, US shipping $10.30.
- Back file: upload `back-dtf-5500.png` (3600+ x 5500 px). The capped `back-dtf.png` is under 300 DPI at full back size.
- Title: `<Design> Fleece Hoodie` (e.g. `Born Ready Fleece Hoodie`).

Files are in `hoodies/<design>/`. **Back:** `back-dtf.png`, centred, as big as the back area allows.

| Design | Collection | Front (`front-dtf.png`) |
|---|---|---|
| Born Ready | Legends Never Die | small chest mark, about 4 in wide, left chest |
| Fallen, Not Finished | Legends Never Die | same |
| Going With the Flow | Legends Never Die | same |
| Queen Forever | Legends Never Die | same |
| Main Character Syndrome | Side Quest | Side Quest hearts emblem, about 3.5 in wide, left chest |
| No Signal | Side Quest | same |
| I Paused My Game to Be Here | Side Quest | same |
| My Other Outfit Is Also Black | Side Quest | same |
| Out of Orbit | Side Quest | same |
| Final Boss Energy | Side Quest | same |
| Urban Collection | Urban Collection | `urban-collection/emblem-dtf.png` on the chest, about 9 in wide; back: `urban-collection/back-dtf.png` |

(Urban Collection has no tops yet, so its hoodie uses the Urban street-scene art.)

## 2. Joggers: Unisex Solid Color Fleece Straight Leg Pants (R00363), one per collection
- **Fulfilment: US (Los Angeles).** Method: DTF.
- **Front:** the collection's `emblem-dtf.png` on the **upper left thigh**, about **4.5 in (11 cm) wide**:
  `legends-never-die/`, `side-quest/`, `urban-collection/`.
- Same 4 colours as the hoodies. Price: **$42** (cost about $19.25 + shipping).
- Titles: `Legends Never Die Fleece Joggers`, `Side Quest Fleece Joggers`, `Urban Collection Fleece Joggers`.
  (The Legends joggers match all four Legends hoodies; the Side Quest joggers match all six Side Quest hoodies.)

## 3. Denim jacket: Unisex Vintage Wash Denim Jacket (UT0142), one per collection
- Fulfilment: China only (1-3 days production, then about 7-12 days shipping). For Christmas, orders need to come
  in by about Dec 8.
- Method: **DTG**. **Back:** the collection's `back-dtg.png`, centred, as tall as the area allows (about 18-20 in).
- **Front:** `emblem-dtg.png`, about **3.5 in (9 cm) wide** on the left chest. Check the mockup: if it overlaps the
  pocket flap, move it above the flap or leave the front blank.
- Colours: **Black, Blue, Navy Blue**. Title: `<Collection> Denim Jacket`. Price: **$79** (cost about $35.97 + shipping).

## Tips
- `-dtf` files are for hoodies and joggers, and `-dtg` files are for the jacket.
- "Left chest" means the wearer's left, which is the right side of the mockup as you look at it.
- Leave descriptions as Tapstitch fills them in; Claude rewrites them in Shopify afterwards.
