const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
const D=__dirname;
const css=`@font-face{font-family:Anton;src:url(anton.woff2)}@font-face{font-family:Mono;src:url(plex-mono-600.woff2);font-weight:600}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;background:transparent;overflow:hidden}
.t{position:absolute;left:0;right:0;text-align:center;color:#F1E5D1;font-family:Anton;text-transform:uppercase;letter-spacing:.01em;line-height:.95;text-shadow:0 4px 30px rgba(0,0,0,.85),0 2px 6px rgba(0,0,0,.9)}
.m{font-family:Mono;font-weight:600;text-transform:uppercase;letter-spacing:.18em;font-size:30px;color:#D6A674;text-shadow:0 2px 12px rgba(0,0,0,.9)}`;
const pages={
 hook:`<div class="t" style="top:330px;font-size:132px">Some legends<br><span style="color:#E0483A">refuse to die.</span></div>`,
 masterless:`<div class="t" style="top:1380px;font-size:150px">Masterless</div><div class="t m" style="top:1545px">No lord. No rush.</div>`,
 crowns:`<div class="t" style="top:300px;font-size:128px">Crowns<br><span style="color:#E0483A">don't retire.</span></div>`,
 rise:`<div class="t" style="top:250px;font-size:96px">Down bad.<br><span style="color:#E0483A">Getting up anyway.</span></div>`,
};
const imgs=fs.readdirSync(path.join(D,'grid')).sort().filter(f=>!/born-ready|sleep-paralysis/.test(f)).map(f=>`<img src="grid/${f}">`).join('');
const end=`<html><head><style>${css}
body{background:#0C0B0E}
.g{position:absolute;top:150px;left:60px;right:60px;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;left:225px;right:225px}
.g img{width:100%;aspect-ratio:3/5.05;object-fit:contain;object-position:bottom;background:#0C0B0E;border:1px solid #2E2428}
.logo{display:flex;align-items:center;justify-content:center;border:1px solid #B83128;color:#F1E5D1;font-family:Anton;font-size:40px;text-align:center;line-height:1}
.glow{position:absolute;inset:0;background:radial-gradient(ellipse 80% 40% at 50% 30%,rgba(184,49,40,.25),transparent 70%)}
</style></head><body><div class="glow"></div>
<div class="m" style="position:absolute;top:70px;left:0;right:0;text-align:center">Elsewhere Apparel Co.</div>
<div class="g">${imgs}</div>
<div class="t" style="top:1290px;font-size:112px">The Immortalized<br>Collection</div>
<div class="t m" style="top:1540px;font-size:34px;color:#F1E5D1">11 legends · Tees $27 · Hoodies $37</div>
<div class="t m" style="top:1610px">Old stories that refuse to die.</div>
<div class="t" style="top:1720px;font-size:64px;color:#E0483A">Link in bio</div>
</body></html>`;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const [n,h] of Object.entries(pages)){fs.writeFileSync(path.join(D,`_${n}.html`),`<html><head><style>${css}</style></head><body>${h}</body></html>`);
 await p.goto('file://'+path.join(D,`_${n}.html`));await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:path.join(D,`ov-${n}.png`),omitBackground:true});}
fs.writeFileSync(path.join(D,'_end.html'),end);await p.goto('file://'+path.join(D,'_end.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:path.join(D,'endcard.png')});await b.close();})();
