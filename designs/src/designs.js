// Print artwork for the Elsewhere Supply Co. launch products.
// Each design is plain HTML/SVG rendered to a transparent PNG by render.js.
// `width` is the CSS width of the artwork; `scale` multiplies it to the final pixel width.

const WHITE = '#FFFFFF';
const BLACK = '#111111';

// Deterministic "barcode" so the label looks the same on every render.
function barcode(count) {
  let seed = 67;
  const bars = [];
  for (let i = 0; i < count; i++) {
    seed = (seed * 9301 + 49297) % 233280;
    const w = 2 + Math.floor((seed / 233280) * 7);
    const gap = 2 + (i % 3) * 2;
    bars.push(`<span style="width:${w}px;margin-right:${gap}px"></span>`);
  }
  return bars.join('');
}

// One meander (Greek key) band, `units` wide.
function greekKey(units, ink) {
  const u = 50;
  let d = '';
  for (let i = 0; i < units; i++) {
    const x = i * u;
    d += `M${x + 5},46 V8 H${x + 40} V38 H${x + 16} V18 H${x + 30} V28 `;
  }
  return `<svg viewBox="0 0 ${units * u} 54" width="100%" style="display:block">
    <path d="M0,2 H${units * u} M0,52 H${units * u}" stroke="${ink}" stroke-width="4" fill="none"/>
    <path d="${d}" stroke="${ink}" stroke-width="4" fill="none" stroke-linejoin="miter"/>
  </svg>`;
}

// Black-figure style ship on waves (original line art).
function ship(ink) {
  const waves = Array.from({ length: 9 }, (_, i) => {
    const x = 20 + i * 70;
    return `M${x},300 c12,-18 35,-18 47,0 c-14,-6 -26,2 -26,12`;
  }).join(' ');
  const oars = Array.from({ length: 7 }, (_, i) => {
    const x = 210 + i * 42;
    return `M${x},228 L${x - 40},292`;
  }).join(' ');
  return `<svg viewBox="0 0 680 330" width="100%" style="display:block">
    <g fill="none" stroke="${ink}" stroke-linecap="round" stroke-linejoin="round">
      <path d="${waves}" stroke-width="7"/>
      <path d="${oars}" stroke-width="6"/>
      <path d="M340,212 V40" stroke-width="9"/>
      <path d="M250,62 H430" stroke-width="8"/>
      <path d="M200,140 L240,160 M480,140 L440,160" stroke-width="5"/>
    </g>
    <path d="M255,66 H425 L418,190 Q340,176 262,190 Z" fill="${ink}"/>
    <path d="M120,212 C170,250 500,250 560,212 L590,160 C600,140 625,138 630,158
             C634,176 614,186 604,172 L575,236 C520,262 180,262 135,240 L95,205
             C80,195 90,180 105,190 Z" fill="${ink}"/>
  </svg>`;
}

const designs = [
  // 1. Currently Elsewhere Hoodie — left chest
  ...[['white', WHITE], ['black', BLACK]].map(([name, ink]) => ({
    file: `01-currently-elsewhere-chest-${name}.png`,
    width: 360,
    scale: 4,
    html: `
      <div style="color:${ink};text-align:center;font-family:'Archivo Black';line-height:0.95">
        <div style="font-size:44px;letter-spacing:0.05em">CURRENTLY</div>
        <div style="font-size:44px;letter-spacing:0.05em">ELSEWHERE</div>
        <div style="font-family:'Space Mono';font-size:17px;margin-top:14px;letter-spacing:0.02em">
          Will respond upon return.
        </div>
      </div>`,
  })),

  // 2. Ships in 6–7 Business Days Tee — front, black ink for light shirts
  {
    file: '02-ships-6-7-business-days-black.png',
    width: 1000,
    scale: 3,
    html: `
      <style>
        .label{border:10px solid ${BLACK};color:${BLACK};font-family:'Space Mono';padding:34px 40px}
        .row{display:flex;justify-content:space-between;align-items:flex-start}
        .stamp{border:6px solid ${BLACK};padding:8px 18px;font-family:'Archivo Black';font-size:30px;
               transform:rotate(-6deg);margin-top:6px}
        .big{font-family:'Anton';line-height:0.92;margin:26px 0 22px;letter-spacing:0.01em}
        .rule{border-top:6px solid ${BLACK};margin:0 -40px}
        .bars{display:flex;height:150px;margin:28px 0 10px}
        .bars span{background:${BLACK};display:block;height:100%}
      </style>
      <div class="label">
        <div class="row">
          <div style="font-size:24px;line-height:1.35">
            <b>FROM:</b> ELSEWHERE SUPPLY CO.<br>
            <b>TO:</b> WHOEVER KEEPS ASKING
          </div>
          <div class="stamp">PRIORITY: LOW</div>
        </div>
        <div class="big">
          <div style="font-size:150px">SHIPS IN</div>
          <div style="font-size:262px">6–7</div>
          <div style="font-size:126px">BUSINESS DAYS</div>
        </div>
        <div class="rule"></div>
        <div class="bars">${barcode(105)}</div>
        <div class="row" style="font-size:26px">
          <div><b>TRACKING #</b> 67-67-67-67</div>
          <div><b>EST. ARRIVAL:</b> EVENTUALLY</div>
        </div>
      </div>`,
  },

  // 3. Not AI. Just Tired. Tee — front
  ...[['white', WHITE], ['black', BLACK]].map(([name, ink]) => ({
    file: `03-not-ai-just-tired-${name}.png`,
    width: 1000,
    scale: 3.6,
    html: `
      <div style="color:${ink};text-align:center">
        <div style="font-family:'Anton';font-size:212px;line-height:1.02;letter-spacing:0.01em">NOT AI.</div>
        <div style="font-family:'Anton';font-size:212px;line-height:1.02;letter-spacing:0.01em;white-space:nowrap">JUST TIRED.</div>
        <div style="font-family:'Space Mono';font-size:38px;margin-top:26px">
          [ verified human — low battery ]
        </div>
      </div>`,
  })),

  // 3b. Back-neck care label
  ...[['white', WHITE], ['black', BLACK]].map(([name, ink]) => ({
    file: `03b-human-made-neck-label-${name}.png`,
    width: 320,
    scale: 3,
    html: `
      <div style="border:5px solid ${ink};color:${ink};text-align:center;padding:16px 12px;
                  font-family:'Space Mono';font-weight:700;line-height:1.25">
        <div style="font-size:30px">100% HUMAN</div>
        <div style="font-size:30px">MADE</div>
        <div style="font-size:20px;font-weight:400;margin-top:4px">(PROBABLY)</div>
        <div style="font-size:14px;font-weight:400;margin-top:10px">WASH COLD · DO NOT PROMPT</div>
      </div>`,
  })),

  // 4. Odysseus Layover Tee — front
  ...[['black', BLACK], ['white', WHITE]].map(([name, ink]) => ({
    file: `04-odysseus-layover-${name}.png`,
    width: 1000,
    scale: 3.3,
    html: `
      <div style="color:${ink};text-align:center;font-family:'Cinzel';font-weight:700">
        <svg viewBox="0 0 1000 230" width="100%" style="display:block">
          <path id="arc" d="M10,225 Q500,-5 990,225" fill="none"/>
          <text font-family="Cinzel" font-weight="700" font-size="44" fill="${ink}" letter-spacing="1"
                text-anchor="middle">
            <textPath href="#arc" startOffset="50%">ODYSSEUS TOOK 10 YEARS TO GET HOME.</textPath>
          </text>
        </svg>
        <div style="width:78%;margin:0 auto">${ship(ink)}</div>
        <div style="margin:18px 0 26px">${greekKey(20, ink)}</div>
        <div style="font-size:88px;line-height:1;letter-spacing:0.03em;white-space:nowrap">I HAVE A LAYOVER.</div>
      </div>`,
  })),

  // 5. Seasonal Depression World Tour Hoodie — front chest + back
  {
    file: '05-seasonal-depression-chest-white.png',
    width: 380,
    scale: 4,
    html: `
      <div style="color:${WHITE};text-align:center;font-family:'Anton';line-height:1">
        <div style="font-size:44px;letter-spacing:0.03em">SEASONAL DEPRESSION</div>
        <div style="font-family:'Oswald';font-weight:500;font-size:27px;letter-spacing:0.32em;margin-top:8px">
          WORLD TOUR 2026
        </div>
      </div>`,
  },
  {
    file: '05-seasonal-depression-tour-back-white.png',
    width: 1000,
    scale: 3.6,
    html: `
      <style>
        .d{display:flex;align-items:baseline;font-family:'Oswald';font-weight:500;font-size:46px;
           letter-spacing:0.04em;line-height:1.55}
        .d .date{width:180px;text-align:left}
        .d .dots{flex:1;border-bottom:5px dotted ${WHITE};margin:0 18px;transform:translateY(-12px)}
      </style>
      <div style="color:${WHITE};text-align:center">
        <div style="font-family:'Anton';font-size:128px;line-height:1;letter-spacing:0.01em">SEASONAL</div>
        <div style="font-family:'Anton';font-size:128px;line-height:1;letter-spacing:0.01em">DEPRESSION</div>
        <div style="font-family:'Oswald';font-weight:600;font-size:56px;letter-spacing:0.42em;margin:18px 0 44px">
          — WORLD TOUR —
        </div>
        ${[
          ['NOV 01', 'MY COUCH', 'SOLD OUT'],
          ['NOV 14', 'UNDER A BLANKET', 'SOLD OUT'],
          ['NOV 27', 'THANKSGIVING TABLE', 'SOLD OUT'],
          ['DEC 08', 'CANCELED PLANS', 'SOLD OUT'],
          ['DEC 21', 'SHORTEST DAY', 'HEADLINER'],
          ['JAN 02', 'BED (ENCORE)', 'EXTENDED'],
          ['FEB 14', 'ALONE (ACOUSTIC)', 'SOLD OUT'],
          ['MAR 20', 'SPRING', 'RESCHEDULED'],
        ].map(([date, venue, status]) => `
          <div class="d"><span class="date">${date}</span><span>${venue}</span>
            <span class="dots"></span><span>${status}</span></div>`).join('')}
        <div style="font-family:'Space Mono';font-size:26px;margin-top:40px;letter-spacing:0.06em">
          NO REFUNDS · NO OPENING ACT · NO SUNLIGHT
        </div>
      </div>`,
  },

  // 6. Do Not Perceive Me Beanie — embroidered cuff
  ...[['white', WHITE], ['black', BLACK]].map(([name, ink]) => ({
    file: `06-do-not-perceive-me-beanie-${name}.png`,
    width: 560,
    scale: 3,
    html: `
      <div style="color:${ink};font-family:'Archivo Black';font-size:38px;letter-spacing:0.04em;
                  white-space:nowrap;text-align:center;padding:6px 0">DO NOT PERCEIVE ME</div>`,
  })),
];

module.exports = { designs };
