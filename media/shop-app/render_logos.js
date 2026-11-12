const { chromium } = require('playwright'); const fs=require('fs');
const f = p => 'data:font/woff2;base64,'+fs.readFileSync(p).toString('base64');
const css = `@font-face{font-family:A;src:url(${f('/home/user/shopify-store/theme/assets/anton.woff2')})}
@font-face{font-family:M;src:url(${f('/home/user/shopify-store/theme-cinematic/assets/plex-mono-500.woff2')});font-weight:500}
html,body{margin:0;background:transparent}`;
const wide = (ink, sub) => `<html><head><style>${css}
#a{display:inline-block;padding:24px 36px;text-align:center}
.w{font-family:A;font-size:220px;line-height:1;letter-spacing:.035em;color:${ink};white-space:nowrap}
.t{font:500 46px M;letter-spacing:.5em;margin-right:-.5em;color:${sub};margin-top:22px;text-transform:uppercase}
</style></head><body><div id=a><div class=w>ELSEWHERE APPAREL CO.</div><div class=t>Apparel for other realities</div></div></body></html>`;
const square = `<html><head><style>${css}
#a{width:1024px;height:1024px;background:#0C0B0E;display:flex;flex-direction:column;align-items:center;justify-content:center;box-sizing:border-box}
.w{font-family:A;color:#F1E5D1;text-align:center;line-height:.92;letter-spacing:.03em}
.w1{font-size:196px}.w2{font-size:122px;color:#E7B681;margin-top:14px;letter-spacing:.08em}
.r{width:300px;height:5px;background:#A23127;margin:34px 0 0}
</style></head><body><div id=a><div class="w w1">ELSEWHERE</div><div class="w w2">APPAREL CO.</div><div class=r></div></div></body></html>`;
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({deviceScaleFactor:1, viewport:{width:4000,height:1200}})).newPage();
  for (const [name, html, bg] of [['elsewhere-logo-light.png', wide('#F1E5D1','#E7B681'), true], ['elsewhere-logo-dark.png', wide('#0C0B0E','#8A5A2B'), true], ['elsewhere-square-logo-1024.png', square, false]]) {
    await p.setContent(html); await p.evaluate(async()=>{await document.fonts.load('40px A'); await document.fonts.load('500 20px M');});
    await p.locator('#a').screenshot({path:name, omitBackground: bg});
    console.log(name);
  }
  await b.close();
})();
