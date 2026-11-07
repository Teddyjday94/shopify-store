# Artlist prompts — Elsewhere Apparel Co.

Ready-to-paste prompts for flyer and ad backgrounds, product stills, product videos and
mockups of people wearing the clothes. Codes like `[V3]` match the content calendar.

**Upload files are ready in `marketing/artlist-inputs/`:**
- `art-*-9x16.jpg`: each Christmas design centered on the brand black with a soft red glow, already vertical (1080×1920) for video
- `product-*-hoodie-back.jpg`: the 5 Christmas hoodies showing the full back print
- `product-*.jpg`: core-line product photos (Currently Elsewhere, Not AI, Ships 6–7, Odysseus, Seasonal Depression, beanie, mug, ornament)

---

## The 5 rules that make or break AI product content

1. **Products always come from an uploaded file.** Use image-to-image / image-to-video. Never
   text-only for anything showing your clothes. Text-only invents a shirt and scrambles the slogan.
2. **Every prompt that shows a product ends with the LOCK line:**
   > *Keep the product, its printed graphic and every letter exactly as in the reference
   > image: same words, spelling, font, layout and colors. Do not redraw, add or remove any text.*
3. **Small motion only near the print.** Slow push-ins, breeze, a head turn, a blink. No spinning,
   arm-crossing, folding or hands in front of the print. The more the fabric moves, the more the text warps.
4. **Draft cheap, then finish.** Test the idea on a fast/low-resolution model, then redo the
   winner on the best model. Artlist bills per generation, so this saves most of your credits.
5. **Check it like a customer.** Before posting: pause on every frame where the print shows
   and read every letter. One misspelled slogan makes the whole shop look fake. Turn on the
   platform's AI label for any realistic AI people or scenes.

## Prompt structure (use this order for anything new)

`Subject` → `Setting` → `Camera` (shot size, angle, lens) → `Light` → `Mood/style` → `Motion` (video) → `Constraints` (LOCK line, "no extra text, no logos, no watermarks")

## Models (Artlist display names)

| Job | Draft with | Final with |
|---|---|---|
| Put the real product into a scene or on a person | Nano Banana 2 (I2I) 1K | **Nano Banana 2 (I2I) 2K** or **GPT Image 2.6 Edit High** |
| Backgrounds with no product | Seedream 5.0 Flash | **Seedream 5.0** / **Flux 3** |
| Animate a still | Seedance 2.0 Mini (720) | **Kling v3 Pro (I2V)** or **Veo 3.1 (I2V)** |
| Voiceover | — | Artlist voiceover, deadpan young adult voice |

**Settings for every video:** 9:16, 5 seconds (8 max), no generated audio (add Artlist music in
CapCut instead, so you control the volume and licensing).

---

## Brand style kit (set up once)

Create an Artlist style kit called **Elsewhere**:
- **Palette:** near-black `#0C0B0E`, cream `#F1E5D1`, blood red `#B83128`, tan `#D6A674`, plum `#2E2428`
- **Guidelines:** *Cinematic, moody, quietly funny. Low-key lighting, deep shadows, warm practical
  lights (lamps, string lights, neon), 35mm film grain, shallow depth of field. Looks like a still
  from an indie film. Muted colors with one red accent. Real, slightly messy spaces: never
  glossy, never stock-photo cheerful. People look tired, unbothered or mildly elsewhere: never
  posing, never grinning at the camera.*
- **References:** `marketing/flyers/out/elsewhere-brand-flyer.png`, `elsewhere-holiday-flyer.png`

## Recurring cast (set up once, reuse everywhere)

Using the same 1–2 "people" across all mockups turns the posts into a recognizable series.
Generate each portrait once (text-to-image), pick the best, and save it as an Artlist
**character reference**. Then add that reference to every `[W]` prompt.

**Character A, "Sam"**
> Portrait of a person in their mid-20s with messy dark shoulder-length hair, tired eyes with faint
> dark circles, a thin silver ring, natural skin texture, plain black t-shirt, neutral deadpan
> expression, looking slightly past the camera, soft window light, plain dark background, 35mm film
> still, realistic, no makeup look

**Character B, "Dee"**
> Portrait of a person in their early 30s with short curly hair and a well-groomed short beard,
> heavy-lidded unimpressed expression, one eyebrow slightly raised, natural skin texture, plain gray
> t-shirt, warm lamp light from the side, plain dark background, 35mm film still, realistic

---

## A. Backgrounds (no product, text-to-image, leave room for text)

Aspect ratio: **9:16** for videos/Stories, **4:5** for IG feed, **3:4** for flyers. Every prompt
ends with: *no people, no text, no logos, no watermarks.*

**[F1] Bedroom do-not-disturb**
> Dimly lit bedroom at night, unmade bed with a heavy dark blanket, a phone face-down glowing faintly,
> warm bedside lamp, rain on the window, wide shot at eye level, deep shadows, muted colors with one
> red accent, large empty dark area in the upper third, cinematic 35mm film still, film grain

**[F2] Office burnout**
> Cluttered desk late at night, laptop screen glow, three empty coffee cups, sticky notes, tangled
> cables, single desk lamp, everyone else has gone home, slightly high angle, moody cinematic light,
> empty wall space in the upper third, film grain, screens show no readable text

**[F3] Airport delay**
> Empty airport gate at night, rows of seats, huge window with a parked plane in blue darkness, a
> departures board glowing red and amber with blurry unreadable text, wide shot, lonely and quietly
> funny, cinematic, film grain, open space at the top

**[F4] Holiday dinner, after the awkward question**
> Holiday dinner table at a low angle, half-eaten food, candles, crumpled napkins, wine glasses,
> warm string lights blurred behind, chairs pushed back, shallow depth of field, cinematic, film grain

**[F5] Cream studio (carousels, flyers)**
> Seamless warm cream paper backdrop, soft directional window light from the left, gentle shadow
> gradient, subtle paper texture, minimal editorial catalog style, completely empty

**[F6] Dark & gold Christmas (holiday ads)**
> Black background, blurry warm gold string-light bokeh, pine branches, red velvet ribbon and small
> gold ornaments along the bottom edge, large empty dark center, luxurious and slightly mischievous,
> cinematic product-ad lighting

**[F7] Snowy street, red neon**
> Quiet city street at night in light snowfall, a red neon glow on a brick wall with no letters,
> wet pavement reflections, single streetlight, empty sidewalk in the foreground, cinematic 35mm film
> still, lonely but cozy

---

## B. Product stills (image-to-image; upload the file, end with the LOCK line)

**[P1] Hoodie on a chair**: `product-currently-elsewhere-hoodie.jpg` · 4:5
> This exact hoodie draped over a worn leather armchair in a dim living room, the chest print facing
> the camera and flat, warm lamp light, a mug and a closed book on a side table, eye-level medium
> shot, cozy evening mood, cinematic, film grain. [LOCK]

**[P2] Flat lay**: upload `product-not-ai-just-tired-tee.jpg`, `product-do-not-perceive-me-beanie.jpg`, `product-bourbon-mug.jpg` · 4:5
> These exact three products as a neat flat lay on a cream linen sheet, overhead shot, all prints
> facing up and fully visible, soft daylight, props: headphones, house keys, a crumpled receipt,
> editorial catalog style. [LOCK]

**[P3] Mug on desk**: `product-bourbon-mug.jpg` · 9:16
> This exact mug on a dark wooden desk, design facing the camera, next to a laptop and a small
> bourbon glass, steam rising, string lights blurred behind, close-up, late evening, cinematic. [LOCK]

**[P4] Ornament on tree**: `product-naughty-ornament.jpg` (or any ornament photo from the store) · 9:16
> This exact round ornament hanging on a dark green Christmas tree branch, design facing the camera,
> warm gold lights blurred behind, macro close-up, shallow depth of field, cinematic holiday mood. [LOCK]

**[P5] Beanie by the door**: `product-do-not-perceive-me-beanie.jpg` · 4:5
> This exact beanie on a shelf by the front door, cuff text facing the camera, next to headphones
> and a phone at 1% battery, early-morning blue light, minimal, slightly melancholy, cinematic. [LOCK]

**[P6] Christmas hoodie on a hanger**: `product-<design>-hoodie-back.jpg` · 9:16
> This exact black hoodie hanging on a wooden hanger against a dark wall, the back print facing the
> camera, centered, fabric flat and smooth, warm gold string lights around it, straight-on medium
> shot, moody product photo. [LOCK]

---

## C. Product videos (image-to-video · 9:16 · 5 s)

**For the art animations, upload `art-<design>-9x16.jpg`.** They're already framed for vertical video.
End every art prompt with: *The lettering stays perfectly still, sharp and unchanged. No new text.*

**[V1] Dear Santa, Bring Bourbon**: `art-dear-santa-bring-bourbon-9x16.jpg`
> The ice cubes in the bourbon glass shift slightly and catch the light, warm glints move across
> the crystal, the white pompom on the Santa hat sways gently, tiny gold sparkles drift upward,
> very slow camera push-in, black background stays still.

**[V2] The Gift Is Me**: `art-the-gift-is-me-9x16.jpg`
> The big red bow settles with a small soft bounce, gold glitter sparkles travel along the ribbon,
> the hanging ornaments sway gently, very slow camera push-in, black background stays still.

**[V3] Holly Jolly Chaos**: `art-holly-jolly-chaos-9x16.jpg`
> Light snow falls in front of the illustration, a glint of light slides across the snowman's
> sunglasses, the scarf flutters slightly, very slow camera push-in, black background stays still.

**[V4] Suck It Up Buttercup** (organic only): `art-suck-it-up-buttercup-9x16.jpg`
> Cigar smoke curls slowly upward, snowflakes drift, the bells on the belt jingle slightly, very
> slow camera push-in, black background stays still.

*(No video for On the Naughty List Again. Animating the pin-up figure risks platform nudity filters.)*

**[V5] Mug steam**: upload your best `[P3]` result
> Steam rises slowly from the mug, string lights twinkle in the background, very slow push-in,
> the mug does not move or rotate. [LOCK]

**[V6] Ornament sway**: upload your best `[P4]` result
> The ornament sways very gently on its branch and stays facing the camera, lights twinkle in the
> bokeh, slow focus pull. [LOCK]

**[V7] Product push-in (any product photo or still)**
> Very slow cinematic push-in, soft light moves across the fabric, a few dust motes float in the
> light, nothing else moves. [LOCK]

**[V8] Christmas hoodie on a hanger**: upload your best `[P6]` result
> The hoodie sways very slightly on its hanger as if from a draft, string lights flicker warmly,
> slow push-in, the back print stays flat. [LOCK]

---

## D. Mockups of people wearing the clothes (2 steps)

**Step 1, still (image-to-image):** upload **the product photo + your Sam or Dee reference**.
Generate 3–4 options. Keep only one where every letter is right.
**Step 2, video (image-to-video):** upload that still and use the motion prompt. 5 seconds.

Front-print products → person faces the camera. Christmas designs → person seen from behind.

**[W1] Currently Elsewhere Hoodie** + Sam
- *Still:* Sam wearing this exact hoodie, sitting on a couch in a dim living room, knees up, staring
  blankly past the camera, phone lighting their face from below, warm lamp behind, medium shot,
  chest print facing the camera, flat and fully visible, cinematic film still. [LOCK]
- *Motion:* Sam blinks slowly and lets out a tired breath, the phone screen flickers, very slow
  push-in. Body and hoodie stay still. [LOCK]

**[W2] Not AI. Just Tired. Tee** + Dee
- *Still:* Dee wearing this exact t-shirt, slumped in an office chair at a desk at night, laptop glow
  on their face, medium shot from slightly below, print facing the camera, flat and fully visible,
  dead-eyed stare, film grain. [LOCK]
- *Motion:* Dee slowly turns their head to look straight into the camera, deadpan, very slow
  push-in. Torso stays still. [LOCK]

**[W3] Ships in 6–7 Business Days Tee** + Sam
- *Still:* Sam wearing this exact white t-shirt, standing in front of stacked cardboard shipping
  boxes, arms relaxed at their sides, unimpressed expression, bright warehouse light, medium shot,
  print fully visible and flat. [LOCK]
- *Motion:* Sam raises one eyebrow and gives a tiny shrug, the camera holds still. [LOCK]

**[W4] Do Not Perceive Me Beanie** + Dee
- *Still:* Dee wearing this exact beanie, cuff text facing the camera, dark jacket collar up,
  standing in a grocery store aisle under harsh fluorescent light, avoiding eye contact, medium
  close-up, cinematic. [LOCK]
- *Motion:* Dee glances at the camera, then slowly looks away. The beanie stays still. [LOCK]

**[W5] Any Christmas hoodie from behind** + Sam or Dee (upload `product-<design>-hoodie-back.jpg`)
- *Still:* Seen from behind, the person wearing this exact black hoodie, hood down, back print
  centered, flat and fully visible, standing in a doorway looking into a warm living room with
  Christmas lights and a blurred family behind them, medium shot, cinematic. [LOCK]
- *Motion:* Very slow push-in toward the back print, the lights twinkle, the person stays still. [LOCK]

**[W6] The Gift Is Me: arriving empty-handed** (`product-the-gift-is-me-hoodie-back.jpg`)
- *Still:* Seen from behind, the person wearing this exact hoodie, back print fully visible,
  standing at a front door with a wreath, hands empty, snowy porch, evening. [LOCK]
- *Motion:* The door opens and warm light spills over them, they stay still. [LOCK]

**[W7] Dear Santa, Bring Bourbon at a bar** (organic only, `product-dear-santa-bring-bourbon-hoodie-back.jpg`)
- *Still:* Seen from behind, an adult in their 30s wearing this exact hoodie, back print fully
  visible, sitting at a dim wooden bar, a bourbon glass on the bar beside them (not in hand), warm
  bar lights, cinematic. [LOCK]
- *Motion:* Slow push-in, the ice catches the light, the person stays still. [LOCK]

**If the print breaks during the motion:** use the AI video for the setup beats only, then
cut to the real product photo (or `[V7]`) for the reveal. A 1-second cut to the real print
looks natural, and the words stay correct.

---

## E. Before you post: 30-second check

- [ ] Every letter of the print is correct, in every frame where it shows
- [ ] No extra text, logos or watermarks the AI added anywhere in the scene
- [ ] Hands have 5 fingers, faces don't warp during motion
- [ ] Product color matches what's actually sold (black hoodie = black, not charcoal)
- [ ] AI label turned on if there's a realistic AI person or scene
- [ ] Bourbon / Buttercup / Naughty content is **not** being boosted as an ad

---

## F. Music (search Artlist's catalog)

| Mood | Search | Use for |
|---|---|---|
| Deadpan / awkward | "awkward comedic pizzicato", "quirky minimal" | Not AI, Ships 6–7 |
| Introvert cozy | "lo-fi chill beat", "bedroom pop mellow" | Currently Elsewhere, Do Not Perceive Me |
| Holiday with attitude | "sassy christmas swing", "lo-fi jazzy christmas" | Gift Is Me, Bourbon |
| Chaos | "chaotic christmas comedy", "frantic jingle bells" | Holly Jolly Chaos |
| Big reveal | "dramatic orchestral comedic", "epic choir" | Odysseus, back-print reveals |
| Winter blues anthem | "melancholy indie rock anthem" | Seasonal Depression World Tour |

Sound effects: "message notification," "ice clink glass," "sleigh bells short," "record scratch."

## G. Voiceover lines (deadpan young adult voice)

- "Physically present. Mentally elsewhere. Will respond upon return."
- "Not AI. Just tired. Thank you for asking."
- "Dear Santa. Bourbon. That's the list."
- "This Christmas, I'm the gift. You're welcome."
- "Elsewhere Apparel Co. Clothes for people who showed up, but didn't fully arrive."
