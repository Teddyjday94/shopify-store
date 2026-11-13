# Print files

Transparent PNGs in `print/`, ready to upload to Printify. `preview.png` shows them all.
Use the **white** file on dark shirt colors and the **black** file on light ones.

| Product | Front | Extra |
|---|---|---|
| Currently Elsewhere Hoodie | `01-currently-elsewhere-chest-*.png` (left chest, ~3.5" wide) | — |
| Ships in 6–7 Business Days Tee | `02-ships-6-7-business-days-black.png` (front, ~10" wide, light shirts only) | — |
| Not AI. Just Tired. Tee | `03-not-ai-just-tired-*.png` (front, ~11" wide) | `03b-human-made-neck-label-*.png` (back neck, ~3" wide) |
| Odysseus Layover Tee | `04-odysseus-layover-*.png` (front, ~11" wide) | — |
| Seasonal Depression World Tour Hoodie | `05-seasonal-depression-chest-white.png` (left chest, ~3.5" wide) | `05-seasonal-depression-tour-back-white.png` (back, ~12" wide). Dark hoodies only. |
| Do Not Perceive Me Beanie | `06-do-not-perceive-me-beanie-*.png` (embroidered cuff, ~4" wide) | — |

To change wording or sizing, edit `src/designs.js` and run `node designs/src/render.js`.
Fonts (Anton, Archivo Black, Cinzel, Oswald, Space Mono) are from Google Fonts under the
SIL Open Font License, which allows commercial use on merchandise.

## All artwork (`all-artwork/`)

Every print file currently on a Printify product (194 files, downloaded 2026-11-13), one copy per design,
named `<collection>__<original upload name>`. `INDEX.tsv` lists each file's pixel size and the products using it.
Collections use the new names (Inner Monologue, Female Lead, Legends Never Die incl. Old Gods, Naughty List,
Creature Feature, Side Quest, Here Be Dragons, Tired But Here); anything else is `elsewhere-core`.
21 files are JPGs because that is how they were uploaded (mostly mug, phone case and desk mat art).
Retired designs are not included. The bookish reader tees' lettering is Printify text, so it has no file.
`printify/export_all_artwork_list.py` lists the products and their image URLs to rebuild this folder.
