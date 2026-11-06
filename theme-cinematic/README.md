Files added to the "Elsewhere | Cinematic" theme (built outside this repo) for the hero postcard.
Upload assets/ and snippets/ as-is; sections/cinematic-hero.liquid renders `hero-postcard`.
Images and font live in designs/web/ (postcard-photo.jpg, postcard-stamp.jpg, caveat-600.woff2).

Front/back gallery (theme "Many Worlds | Front-Back Gallery"): sections/main-product.liquid,
assets/theme.js and assets/mw-gallery.css. Product photos labeled "<Title> in <Color>, <front|back> print"
are grouped by color; the product page shows only the selected color's photos with arrows and swipe.
Products without labeled photos show all photos in one scrolling row.

Collections as filters: sections/main-collection.liquid wraps the page in [data-collection-view]; theme.js
(initCollectionSwap) loads links to other collections (tabs, header dropdowns, filter chips, sort, pagination)
in place and swaps only that block, keeping browser back/forward working.
