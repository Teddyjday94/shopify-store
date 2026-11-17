import re,sys,json,time,requests,glob
exp={}
for f in glob.glob('vm2/vm_*.graphql'):
    s=open(f).read()
    for pid,body in re.findall(r'Product/(\d+)", variants:\[(.*?)\]\)',s):
        for v,m in re.findall(r'ProductVariant/(\d+)",mediaId:"gid://shopify/MediaImage/(\d+)',body):
            exp[int(v)]=(int(pid),int(m))
prods={}
for v,(p,m) in exp.items(): prods.setdefault(p,{})[v]=m
only=set(sys.argv[1:])
handles={}
page=1
while True:
    d=requests.get(f'https://elsewhereapparelco.com/products.json?limit=250&page={page}&nc={time.time()}').json()['products']
    for p in d: handles[p['id']]=p['handle']
    if len(d)<250: break
    page+=1
bad=[];ok=0
for p,vs in prods.items():
    if only and str(p) not in only: continue
    j=requests.get(f'https://elsewhereapparelco.com/products/{handles[p]}.js?nc={time.time()}').json()
    have={v['id']:(v.get('featured_media') or {}).get('id') for v in j['variants']}
    for v,m in vs.items():
        if have.get(v)==m: ok+=1
        else: bad.append((p,v,m,have.get(v)))
print('ok',ok,'bad',len(bad))
for b in bad[:40]: print(b)
