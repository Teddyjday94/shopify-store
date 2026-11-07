# Artlist prompts — Elsewhere Apparel Co.

Ready-to-paste prompts for flyer and ad images, product videos, and mockup videos of people
wearing the clothes. Codes like `[F1]` match the content calendar.

## Read this first: the 4 rules

1. **Always start from your real product photo or art file.** Use **image-to-image** /
   **image-to-video**, never text-only, for anything that shows a product. Text-only
   prompts *invent* a shirt, and the printed words come out garbled.
   - Product photos: `marketing/flyers/assets/products/` (or download them from Shopify admin)
   - Full-color Christmas art: `designs/print-xmas/*-back.png`
   - Chest/front print files: `designs/print*/`
2. **Check the print before posting.** Zoom in on every generated image and video frame. If
   any letter is wrong, regenerate or don't use it. A misspelled slogan is the fastest way
   to look like a scam shop.
3. **Keep motion small** on anything with a print. Slow camera push, light breeze,
   a small head turn. No spinning, folding, crossed arms or hands in front of the print.
   The more the fabric moves, the more the text warps.
4. **Label it.** Turn on the AI-generated label on TikTok/Instagram for realistic AI content.
   Use real photos/video for paid ads whenever you can, and never use AI mockups to show a
   print that differs from what customers receive.

## Recommended models (Artlist display names)

| Job | Use | Why |
|---|---|---|
| Put a product into a new scene / onto a person (keep the print) | **Nano Banana 2 (I2I)** or **GPT Image 2.6 Edit (High)** | Best at keeping existing text and graphics intact |
| Backgrounds with no product | **Seedream 5.0** or **Flux 3** | Good-looking scenes, cheap |
| Image → video | **Kling v3 Pro (I2V)** or **Veo 3.1 (I2V)**; **Seedance 2.5** as a backup | Most stable fabric and faces |
| Voiceover | Artlist voiceover, a dry, deadpan, young adult voice | Matches the brand tone |

## Brand style kit (set up once)

Create an Artlist style kit called **Elsewhere** so every generation matches:
- **Palette:** near-black `#0C0B0E`, cream `#F1E5D1`, blood red `#B83128`, tan `#D6A674`, dark plum `#2E2428`
- **Style guidelines (paste in):** *Cinematic, moody, quietly funny. Low-key lighting, deep
  shadows, warm practical lights (lamps, string lights, neon), film grain, shallow depth of
  field. Feels like a still from an indie film. Muted colors with one red accent. Real,
  slightly messy spaces: never glossy, never stock-photo cheerful. Subjects look tired,
  unbothered or mildly elsewhere: never posing, never smiling at the camera.*
- **References:** upload the flyer PNGs in `marketing/flyers/out/` and 2–3 product photos.

---

## A. Flyer & ad backgrounds (no product, text-to-image)

These leave empty space where text goes. Put your products and type on top (in Canva or our
flyer generator). Vertical 9:16 for TikTok/Reels/Stories, 4:5 for IG feed, 8.5×11 (≈3:4) for flyers.

**[F1] Bedroom do-not-disturb**
> Dimly lit bedroom at night, unmade bed with a heavy dark blanket, phone face-down glowing
> faintly, warm bedside lamp, rain on the window, deep shadows, cinematic film still, 35mm film
> grain, muted colors with a single red accent, large empty dark area in the upper third for text,
> no people, no text

**[F2] Office burnout**
> Cluttered desk late at night, laptop screen glow, three empty coffee cups, sticky notes,
> tangled cables, a single desk lamp, everyone else has gone home, moody cinematic lighting,
> film grain, muted palette, empty wall space at top for text, no people, no readable text on screens

**[F3] Airport delay**
> Empty airport gate at night, rows of seats, huge window with a parked plane in blue
> darkness, a departures board glowing red and amber with blurry unreadable text, lonely and
> quietly funny mood, cinematic wide shot, film grain, space at top for headline, no people

**[F4] Family dinner**
> Holiday dinner table from a low angle, half-eaten food, candles, crumpled napkins, wine
> glasses, warm string lights blurred in the background, chairs pushed back, the feeling right
> after an awkward question, cinematic, shallow depth of field, film grain, no people

**[F5] Cream studio (for carousels/flyers)**
> Seamless warm cream paper backdrop, soft directional window light from the left, gentle
> shadow gradient, subtle paper texture, minimal, editorial fashion catalog, completely empty

**[F6] Christmas, dark & gold (holiday ads)**
> Dark moody Christmas scene, black background, blurry warm gold string lights bokeh,
> scattered pine branches, red velvet ribbon and small gold ornaments at the bottom edge,
> luxurious and slightly mischievous, large empty dark center for a product, cinematic, no text

**[F7] Snowy street, red neon**
> Quiet city street at night in light snowfall, a red neon sign glowing on a brick wall (no
> readable letters), wet pavement reflections, a single streetlight, cinematic 35mm film still,
> lonely but cozy, empty sidewalk in foreground, no people

---

## B. Product lifestyle stills (image-to-image, upload the product photo)

Put this sentence at the end of **every** prompt in this section and in section D:
> **Keep the garment and its printed graphic and text exactly as in the reference image: same
> words, same font, same layout, same colors. Do not redraw, translate or change any lettering.**

**[P1] Hoodie on a chair**: upload *currently-elsewhere-hoodie.jpg*
> Place this exact hoodie draped over a worn leather armchair in a dim living room, warm lamp
> light, a mug and a closed book on a side table, cozy evening mood, cinematic, film grain. [keep-print sentence]

**[P2] Flat lay**: upload 3 product photos (a tee, the beanie, a mug)
> Arrange these exact products as a neat flat lay on a cream linen sheet, overhead shot, soft
> daylight, a pair of headphones, house keys and a crumpled receipt as props, editorial
> catalog style. [keep-print sentence]

**[P3] Mug on desk**: upload a Christmas mug photo
> Place this exact mug on a dark wooden desk next to a laptop and a small bourbon glass,
> steam rising, string lights blurred in the background, late evening, cozy, cinematic. [keep-print sentence]

**[P4] Ornament on tree**: upload an ornament photo
> Hang this exact round ornament on a dark green Christmas tree branch, warm gold lights
> blurred behind, close-up, shallow depth of field, cinematic holiday mood. [keep-print sentence]

**[P5] Beanie on a shelf**: upload *do-not-perceive-me-beanie.jpg*
> This exact beanie on a shelf by the front door next to headphones and a phone at 1%,
> early morning blue light, minimal, slightly melancholy, cinematic. [keep-print sentence]

**[P6] Christmas art as a poster scene**: upload the Christmas art PNG
> Show this exact illustration as the back print on a black hoodie hanging on a wooden
> hanger against a dark wall with gold string lights, front-facing, fabric flat and smooth,
> studio product photo, moody. [keep-print sentence]

---

## C. Product videos (image-to-video, 5–8 s, 9:16)

Upload the image named, then use the prompt. Keep "camera" and "motion" small.

**[V1] Dear Santa, Bring Bourbon (art)**: upload *03-dear-santa-bring-bourbon-back.png* on a black background
> Subtle animation of this illustration: ice cubes gently shift in the bourbon glass with
> a soft clink, warm light glints on the crystal, the pompom on the Santa hat sways slightly,
> tiny gold sparkles drift, slow camera push-in. The lettering stays perfectly still and unchanged.

**[V2] The Gift Is Me (art)**: upload *04-the-gift-is-me-back.png*
> Subtle animation: the big red bow tightens and settles with a little bounce, gold glitter
> sparkles across the ribbon, the ornaments sway gently, slow push-in. The lettering stays
> perfectly still and unchanged.

**[V3] Holly Jolly Chaos (art)**: upload *05-holly-jolly-chaos-back.png*
> Subtle animation: light snow falls, a glint of light slides across the snowman's
> sunglasses, his scarf flutters slightly, the dripping red letters stay still, slow push-in.
> The lettering stays perfectly still and unchanged.

**[V4] Suck It Up Buttercup (art)**: upload *02-suck-it-up-buttercup-back.png*
> Subtle animation: cigar smoke curls upward, snowflakes drift, the bells on the belt
> jingle slightly, Santa's eyes narrow very slightly, slow push-in. The lettering stays
> perfectly still and unchanged.

**[V5] Mug steam**: upload the result of [P3]
> Steam rises slowly from the mug, string lights twinkle softly in the background, very slow
> camera push-in, everything else still. The mug's print does not move or change.

**[V6] Ornament sway**: upload the result of [P4]
> The ornament sways very gently on its branch, lights twinkle in the bokeh, slow focus pull. The print does not change.

**[V7] Generic product push-in**: upload any product photo or [P] still
> Very slow cinematic push-in, soft light shifts across the fabric, dust motes float in the
> light, nothing else moves. The print stays sharp and unchanged.

**[V8] Hoodie on hanger**: upload [P6] result
> The hoodie sways very slightly on its hanger as if from a draft, string lights flicker
> warmly, slow push-in. The back print stays flat, sharp and unchanged.

---

## D. Mockup videos of people wearing the clothes (2 steps)

**Step 1: make the still (image-to-image).** Upload the product photo. Use these prompts
plus the keep-print sentence from section B. Generate 3–4 options and keep the one where
the print is perfect.
**Step 2: animate it (image-to-video).** Upload the step 1 still and use the matching motion
prompt. Keep it to 5 seconds.

Front-print designs → person faces the camera. Christmas designs (big back print) → person
faces away or turns their back to the camera.

**[W1] Currently Elsewhere Hoodie**
- *Still:* A person in their mid-20s wearing this exact hoodie, sitting on a couch in a dim
  living room, knees up, staring blankly out of frame, phone lighting their face from below,
  warm lamp behind them, chest print fully visible and facing the camera, cinematic film still.
- *Motion:* The person blinks slowly and lets out a tired sigh, the phone screen flickers,
  the camera slowly pushes in. Their body and the hoodie stay still; the print does not change.

**[W2] Not AI. Just Tired. Tee**
- *Still:* A person in their late 20s wearing this exact t-shirt, slumped in an office chair
  at a desk at night, laptop glow on their face, messy hair, dead-eyed expression looking at the
  camera, shirt print fully visible and flat, cinematic, film grain.
- *Motion:* The person slowly turns their head to look straight into the camera with a
  deadpan stare, very slow push-in. The torso stays still; the print does not change.

**[W3] Ships in 6–7 Business Days Tee**
- *Still:* A person wearing this exact white t-shirt standing in front of a stack of
  cardboard shipping boxes, arms relaxed at their sides, neutral unimpressed expression, bright
  warehouse light, shirt print fully visible and flat.
- *Motion:* The person raises one eyebrow and shrugs very slightly, the camera holds still.
  The print does not change.

**[W4] Do Not Perceive Me Beanie**
- *Still:* A person wearing this exact beanie with the cuff text facing the camera, collar of a
  dark jacket pulled up, standing in a grocery store aisle, harsh fluorescent light, avoiding
  eye contact, cinematic film still.
- *Motion:* The person glances at the camera, then slowly pulls the beanie slightly lower
  and looks away. The cuff text stays readable and unchanged.

**[W5] Christmas back print (any of the 5)**
- *Still:* A person seen from behind wearing this exact black hoodie with the full back print
  centered and flat, standing in a doorway looking into a warm living room full of Christmas
  lights and family blurred in the background, cinematic.
- *Motion:* Very slow camera push-in toward the back print, Christmas lights twinkle, the
  person stands still. The back print does not change.

**[W6] The Gift Is Me: party entrance**
- *Still:* A person from behind wearing this exact hoodie, back print fully visible, standing
  at a front door holding nothing, a wreath on the door, a snowy porch, evening.
- *Motion:* The door opens and warm light spills out over the person, they stay still.
  The back print does not change.

**[W7] Dear Santa, Bring Bourbon: bar**
- *Still:* An adult in their 30s seen from behind wearing this exact hoodie, back print fully
  visible, sitting at a dim wooden bar, a glass of bourbon on the rocks beside them, warm bar
  lights, cinematic.
- *Motion:* They lift the glass slowly, the ice catches the light, slow push-in. The back print
  does not change.

**If the print breaks in the video:** cut to the original product photo or still for the
print part. A 1-second cut to the real image is invisible to viewers and keeps the
words correct.

---

## E. Music (search Artlist's catalog, don't generate)

| Mood | Search terms | Use for |
|---|---|---|
| Deadpan / awkward | "awkward comedic pizzicato", "quirky minimal" | Not AI, Ships 6–7, family-dinner posts |
| Introvert cozy | "lo-fi chill beat", "bedroom pop mellow" | Currently Elsewhere, Do Not Perceive Me |
| Holiday, a little naughty | "lo-fi jazzy christmas", "sassy christmas swing" | Bourbon, Gift Is Me |
| Chaos | "chaotic christmas comedy", "frantic jingle bells" | Holly Jolly Chaos |
| Big reveal | "dramatic orchestral comedic", "epic choir" | Odysseus, back-print reveals |
| Black Friday | "suspense build hip hop", "countdown tension" | Teaser posts |

Sound effects: "message notification," "ice clink glass," "sleigh bells short," "record scratch."

## F. Voiceover lines (Artlist voiceover, deadpan young adult voice)

- "Physically present. Mentally elsewhere. Will respond upon return."
- "Not AI. Just tired. Thank you for asking."
- "Dear Santa. Bourbon. That's the list."
- "This Christmas, I'm the gift. You're welcome."
- "Elsewhere Apparel Co. Clothes for people who showed up, but didn't fully arrive."
