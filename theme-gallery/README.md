# Elsewhere Gallery theme

A marketplace-style theme for Elsewhere Apparel Co., inspired by the layout of art-tee marketplaces such as
Threadless (layout ideas only; no code, art or branding copied). White page, soft image tiles, bold Inter Tight
type, pill buttons, one accent color (theme settings > Colors).

What's in it
- Header: rotating announcement bar (messages can have start/end dates), logo + wide search bar + account/cart,
  category row from the main menu. Dropdowns open a mega panel: collection links with images show as image
  tiles (the Collections menu), the rest as a link list beside a featured collection. Phones get a menu drawer.
- Home (templates/index.json): hero carousel (overlay or split layout per slide), "Shop by product" round tiles,
  tabbed product grids, promises row, collection spotlight (a collection shown like an artist shop),
  collection tiles, promo cards.
- Product cards: design on a soft tile, hover photo, "from <collection>" under the title (like an artist
  name; which collections count is theme settings > Product cards), sale % badge. Hoodies preview the back print.
- Collection page: banner from the collection image, sibling category pills, sticky filter sidebar (a drawer on
  phones), sort, active-filter chips, 4-column grid.
- Product page: gallery grouped by color (photos labeled "<Title> in <Color>, ..."), "Available on" style
  picker (same design on other products, by handle <design>-<style>, see snippets/design-key.liquid), color
  swatches (snippets/swatch-color.liquid maps Printify color names), size chips + size guide, koozie deal table,
  promises, accordions, "More from <collection>", recommendations, sticky add bar on phones.
- Cart drawer with free-shipping progress bar (theme settings > Cart; match the automatic discount).

Package for upload: `cd theme-gallery && zip -qr ../dist/elsewhere-gallery-theme.zip assets config layout locales sections snippets templates`
