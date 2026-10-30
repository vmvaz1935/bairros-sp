import json,shapely,shapely.ops,numpy as np
from shapely.geometry import shape,mapping
from shapely.strtree import STRtree
from pyproj import Transformer
fwd=Transformer.from_crs(4326,31983,always_xy=True).transform; inv=Transformer.from_crs(31983,4326,always_xy=True).transform
B=json.load(open('bairros_bruto.geojson'))['features']
items=[]
for f in B:
    g=shapely.ops.transform(fwd,shape(f['geometry'])).buffer(0)
    for p in shapely.get_parts(g): items.append([f['properties']['bairro'],p,f['properties']])
for rnd in range(3):
    maxa={}
    for b,p,_ in items: maxa[b]=max(maxa.get(b,0),p.area)
    small=[i for i,(b,p,_) in enumerate(items) if p.area<maxa[b] and p.area<0.25*maxa[b] and p.area<300000]
    st=STRtree([p for _,p,_ in items]); moved=0
    for i in sorted(small,key=lambda i:items[i][1].area):
        b,p,_=items[i]; pb=p.buffer(2); best=None;bl=0
        for j in st.query(pb):
            if j==i or items[j][0]==b: continue
            l=pb.intersection(items[j][1]).area
            if l>bl: bl=l;best=j
        if best is not None: items[i][0]=items[best][0]; items[i][2]=items[best][2]; moved+=1
    print('rodada',rnd,'fragmentos movidos',moved)
agg={}
for b,p,pr in items: agg.setdefault(b,[[],pr])[0].append(p)
out=[]
for b,(ps,pr) in agg.items():
    g=shapely.union_all(ps).buffer(1).buffer(-1)
    pr=dict(pr); pr['area_km2']=round(g.area/1e6,3); pr['partes']=len(shapely.get_parts(g))
    out.append({'type':'Feature','properties':pr,'geometry':mapping(shapely.ops.transform(inv,g).simplify(0.00004,preserve_topology=True))})
json.dump({'type':'FeatureCollection','features':out},open('dados/bairros_sp.geojson','w'),ensure_ascii=False)
p=np.array([o['properties']['partes'] for o in out]);print('bairros',len(out),'partes: 1=',(p==1).sum(),'2-3=',((p>1)&(p<4)).sum(),'>=4=',(p>=4).sum(),'area',round(sum(o['properties']['area_km2'] for o in out),1))
