import re,json,glob
parts=[]
for f in sorted(glob.glob('vm2/vm_*.graphql')):
    if f.endswith('vm_8.graphql'): continue
    s=open(f).read()
    for pid,body in re.findall(r'Product/(\d+)", variants:\[(.*?)\]\)',s):
        parts.append((pid,[[v,m] for v,m in re.findall(r'ProductVariant/(\d+)",mediaId:"gid://shopify/MediaImage/(\d+)',body)]))
batches=[[]];size=0
for p in parts:
    n=len(json.dumps(p))
    if batches[-1] and size+n>12000: batches.append([]);size=0
    batches[-1].append(p);size+=n
for i,b in enumerate(batches):
    q='mutation('+','.join(f'$p{k}:ID!,$v{k}:[ProductVariantsBulkInput!]!' for k in range(len(b)))+'){'+' '.join(f'a{k}:productVariantsBulkUpdate(productId:$p{k},variants:$v{k}){{userErrors{{message}}}}' for k in range(len(b)))+'}'
    var={}
    for k,(pid,vs) in enumerate(b):
        var[f'p{k}']=f'gid://shopify/Product/{pid}'
        var[f'v{k}']=[{'id':f'gid://shopify/ProductVariant/{v}','mediaId':f'gid://shopify/MediaImage/{m}'} for v,m in vs]
    open(f'vv_{i}.json','w').write(json.dumps({'q':q,'v':var},separators=(',',':')))
print(len(parts),'products',sum(len(v) for _,v in parts),'variants',len(batches),'batches')
