Files changed on top of the live Shopify theme "Hero Video Preview" (built outside this repo; the rest of
that theme is not stored here). Applied to the copy "Elsewhere Apparel Co. | New Fonts" (156527263905).
- layout/theme.liquid: loads Barlow Semi Condensed and assets/type-pairing.css last.
- assets/type-pairing.css: font overrides. assets/barlow-semi-condensed-*.woff2: SIL OFL, from @fontsource.
- sections/field-guide-home.liquid: world tiles can show a looping video (block setting video_url) over the
  still, and "center_art" turns off the per-tile zoom/offset for artwork pre-cropped around the design.
- templates/index.json: Legends Never Die tile = Rise From Ruin video (+ still), Creature Feature tile = Horror
  Club photo. Media sources in media/homepage/.
