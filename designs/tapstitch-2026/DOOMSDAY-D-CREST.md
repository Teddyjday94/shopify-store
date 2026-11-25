# Doomsday Drop: the D Crest

On 2026-11-25 the owner changed the drop's crest from an **L** to a **big D**, across every product.

## Files

Art lives in `designs/tapstitch-2026/doomsday/` on the owner's drive (art folders are kept out of git).

| File | Size | Use |
| --- | --- | --- |
| `d-crest-v2.png` | 1111 x 1415, transparent | Master artwork |
| `d-crest-front.png` | 2222 x 2830 (2x) | Varsity chest crest, about 4 in tall |
| `d-crest-back-hd.png` | 4444 x 5660 (4x) | Large prints: varsity back, tee front, hoodie back. Also in Shopify Files as `d-crest-print.png` |
| `d-crest-v2-preview-*.jpg` | | Previews on black and on varsity green |

The art was made in Kittl (GPT Image 2.5 Flare-HQ edit of the original L crest, two passes to enlarge the D). Kittl filled the
shield with white, so the white was flood-filled back to transparent. The enlargements are Lanczos, which is a little soft up close
but prints at 330-350 DPI at full size.

The original L art is `C:\Users\teddy\Downloads\doomsday-promo\doomsday-promo\1-designs-transparent\l-crest.png` (not in the repo).

## Products

| Product | Maker | Print | Price | Shopify handle |
| --- | --- | --- | --- | --- |
| D Crest Tee | Printify, Bella+Canvas 3001 | Front, 13.4 x 17 in | $27 | `d-crest-tee` (redirect from `l-crest-tee`) |
| D Crest Hoodie | Printify, Gildan 18500 | Back, 12.6 x 16 in | $37 | `d-crest-hoodie` (redirect from `l-crest-hoodie`) |
| D Crest Varsity Jacket | Tapstitch RQ0001, Green with White | Right chest (as you look at it) + back | $47 | `d-crest-varsity-jacket` |

All three are tagged `doomsday drop`, so they appear in the Doomsday Drop collection (ends December 18).

## Homepage

`theme-cinematic/sections/crest-feature.liquid` is the "Crest feature" band at the top of the live homepage: the crest beside
the three products, with a button to the Doomsday Drop. It hides itself after its "Hide after" date (2026-12-18).
