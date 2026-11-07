const fs=require('fs'),path=require('path');const {chromium}=require('playwright');
const S=process.argv[2], N=S+'/fonts/node_modules', T='/home/user/shopify-store/theme/assets';
const u=(f,t='woff2')=>`url(data:font/${t};base64,${fs.readFileSync(f).toString('base64')})`;
const css=`
@font-face{font-family:Anton;src:${u(T+'/anton.woff2')}}
@font-face{font-family:'Space Mono';src:${u(T+'/space-mono-400.woff2')}}
@font-face{font-family:'Space Mono';font-weight:700;src:${u(T+'/space-mono-700.woff2')}}
@font-face{font-family:'Archivo Black';src:${u(T+'/archivo-black.woff2')}}
@font-face{font-family:'Instrument Serif';src:${u(N+'/@fontsource/instrument-serif/files/instrument-serif-latin-400-normal.woff2')}}
@font-face{font-family:'Instrument Serif';font-style:italic;src:${u(N+'/@fontsource/instrument-serif/files/instrument-serif-latin-400-italic.woff2')}}
@font-face{font-family:'Inter Tight';font-weight:100 900;src:${u(N+'/@fontsource-variable/inter-tight/files/inter-tight-latin-wght-normal.woff2')}}
@font-face{font-family:'Plex Mono';font-weight:500;src:${u(N+'/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2')}}
@font-face{font-family:'Archivo V';font-weight:100 900;font-stretch:62% 125%;src:${u(N+'/@fontsource-variable/archivo/files/archivo-latin-wdth-normal.woff2')}}
@font-face{font-family:'JB Mono';font-weight:100 800;src:${u(N+'/@fontsource-variable/jetbrains-mono/files/jetbrains-mono-latin-wght-normal.woff2')}}
@font-face{font-family:'Bricolage';font-weight:200 800;font-stretch:75% 100%;src:${u(N+'/@fontsource-variable/bricolage-grotesque/files/bricolage-grotesque-latin-wdth-normal.woff2')}}
@font-face{font-family:'Inter V';font-weight:100 900;src:${u(N+'/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2')}}
body{margin:0;background:#fff;font-family:sans-serif}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:14px;width:1400px}
.p{background:#0C0B0E;color:#F1E5D1;padding:34px 36px;border-radius:6px;min-height:520px;box-sizing:border-box}
.tag{display:inline-block;background:#F1E5D1;color:#0C0B0E;font:700 13px Arial;padding:4px 10px;margin-bottom:22px;letter-spacing:.06em}
.k{color:#D6A674}.h{margin:10px 0 16px}.b{max-width:52ch;opacity:.85;margin:0 0 22px}
.row{display:flex;gap:22px;align-items:flex-end}.card{width:190px}.ph{height:150px;background:linear-gradient(135deg,#3a1c1c,#171416);margin-bottom:10px}
.btn{display:inline-block;background:#B83128;color:#fff;padding:12px 20px}
/* current */
.cur .k{font:600 10px Arial;letter-spacing:.3em}.cur .h{font-family:Anton;font-size:76px;line-height:.9;text-transform:uppercase}
.cur .b{font:400 14px/1.7 'Space Mono'}.cur .t{font-family:'Archivo Black';font-size:15px;text-transform:uppercase}.cur .pr,.cur .btn{font:700 13px 'Space Mono';text-transform:uppercase;letter-spacing:.1em}
.cur .q{font:italic 22px Georgia;color:#D6A674;margin:0 0 18px}
/* A */
.a .k{font:500 11px 'Plex Mono';letter-spacing:.22em;text-transform:uppercase}.a .h{font-family:'Instrument Serif';font-size:92px;line-height:.92;font-weight:400;letter-spacing:-.01em}
.a .h i{color:#D6A674}.a .b{font:400 16px/1.6 'Inter Tight'}.a .t{font:600 15px/1.25 'Inter Tight'}.a .pr{font:500 12px 'Plex Mono';margin-top:4px}
.a .btn{font:600 14px 'Inter Tight';letter-spacing:.02em}.a .q{font:italic 26px 'Instrument Serif';color:#D6A674;margin:0 0 18px}
/* B */
.bb .k{font:500 11px 'JB Mono';letter-spacing:.2em;text-transform:uppercase}.bb .h{font-family:'Archivo V';font-stretch:62%;font-weight:900;font-size:96px;line-height:.86;text-transform:uppercase}
.bb .b{font:400 16px/1.6 'Archivo V';font-stretch:100%}.bb .t{font-family:'Archivo V';font-stretch:75%;font-weight:800;font-size:18px;text-transform:uppercase}.bb .pr{font:500 12px 'JB Mono'}
.bb .btn{font-family:'Archivo V';font-stretch:87%;font-weight:800;font-size:14px;text-transform:uppercase;letter-spacing:.06em}.bb .q{font-family:'Archivo V';font-stretch:100%;font-style:italic;font-size:22px;color:#D6A674;margin:0 0 18px}
/* C */
.c .k{font:600 11px 'Inter V';letter-spacing:.2em;text-transform:uppercase}.c .h{font-family:'Bricolage';font-weight:800;font-stretch:80%;font-size:88px;line-height:.9;letter-spacing:-.03em}
.c .b{font:400 16px/1.6 'Inter V'}.c .t{font:700 16px 'Bricolage';font-stretch:90%}.c .pr{font:500 13px 'Inter V'}
.c .btn{font:600 14px 'Inter V'}.c .q{font-family:'Bricolage';font-weight:500;font-size:22px;color:#D6A674;margin:0 0 18px}
`;
const panel=(cls,name,h)=>`<div class="p ${cls}"><div class="tag">${name}</div>
<div class="k">Now entering / The Immortalized Collection</div><div class="h">${h}</div>
<p class="q">Made elsewhere. Worn right here.</p>
<p class="b">Printed to order and shipped in 6–7 business days. Heavyweight fleece, big back prints, and art you won't see on anyone else at the grocery store.</p>
<div class="row"><div class="card"><div class="ph"></div><div class="t">Lead the Charge Hoodie</div><div class="pr">$45.00 · 6 colors</div></div><span class="btn">Shop the drop →</span></div></div>`;
const html=`<html><head><style>${css}</style></head><body><div class="grid">
${panel('cur','NOW: Anton + Space Mono + Georgia/Arial','Currently<br>Elsewhere.')}
${panel('a','A · CINEMATIC EDITORIAL: Instrument Serif + Inter Tight + IBM Plex Mono','Currently <i>Elsewhere.</i>')}
${panel('bb','B · STREETWEAR BOLD: Archivo (condensed → normal) + JetBrains Mono','Currently<br>Elsewhere.')}
${panel('c','C · MODERN CHARACTER: Bricolage Grotesque + Inter','Currently<br>Elsewhere.')}
</div></body></html>`;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1428,height:900},deviceScaleFactor:2});
await p.setContent(html);await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:S+'/font-options.png',fullPage:true});await b.close();})();
