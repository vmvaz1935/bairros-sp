import pandas as pd, numpy as np, json, time
import shapely
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform
from pyproj import Transformer
from scipy.spatial import cKDTree
t0=time.time()
fwd=Transformer.from_crs(4326,31983,always_xy=True); inv=Transformer.from_crs(31983,4326,always_xy=True)
m=pd.read_pickle('cnefe_cep.pkl')
m=m[m.BAIRRO.notna() & (m.NV_GEO_COORD.astype(int)<=3)]
m['x'],m['y']=fwd.transform(m.LONGITUDE.values,m.LATITUDE.values)
key=['COD_SETOR','NUM_QUADRA','NUM_FACE']
cnt=m.groupby(key+['BAIRRO']).size().rename('n').reset_index()
tot=cnt.groupby(key).n.transform('sum')
cnt['share']=cnt.n/tot
top=cnt.sort_values('n',ascending=False).drop_duplicates(key)
xy=m.groupby(key)[['x','y']].median().reset_index()
F=top.merge(xy,on=key)
print('faces',len(F),'pureza media (enderecos no bairro majoritario da face):',round((F.n.sum()/cnt.n.sum())*100,1),'%')
# suavizacao: face com poucos enderecos e bairro diferente de >=6 dos 8 vizinhos -> adota vizinho
P=F[['x','y']].values; tree=cKDTree(P); _,nb=tree.query(P,k=9)
lab=F.BAIRRO.values.copy(); changed=0
for it in range(2):
    new=lab.copy()
    for i in range(len(P)):
        v=pd.Series(lab[nb[i,1:]]).value_counts()
        if v.index[0]!=lab[i] and v.iloc[0]>=6 and F.n.values[i]<=15:
            new[i]=v.index[0]
    changed+= (new!=lab).sum(); lab=new
F['B']=lab; print('faces reatribuidas na suavizacao:',changed)
# limite do municipio
f=json.load(open('dados/osm_bairros_e_distritos.geojson'))['features']
dist=[(x['properties']['name'],transform(fwd.transform,shape(x['geometry']).buffer(0))) for x in f if x['properties']['layer']=='distrito']
mun=unary_union([g for _,g in dist])
# voronoi (pontos duplicados: jitter minimo)
P=P+np.random.default_rng(0).normal(0,0.01,P.shape)
vd=shapely.voronoi_polygons(shapely.multipoints(P),extend_to=mun.envelope.buffer(2000),ordered=True)
cells=shapely.get_parts(vd)
print('celulas',len(cells),time.time()-t0)
cells=shapely.intersection(cells,mun)
df=pd.DataFrame({'B':F.B.values,'g':cells})
polys={}
for b,grp in df.groupby('B'):
    polys[b]=shapely.union_all(grp.g.values).buffer(0)
print('dissolvidos',len(polys),time.time()-t0)
# fragmentos: partes < 30% da maior parte e < 0.05 km2 -> vizinho com maior fronteira
items=[]
for b,g in polys.items():
    for p in shapely.get_parts(g): items.append([b,p])
areas=np.array([p.area for _,p in items])
maxa={}
for (b,p),a in zip(items,areas): maxa[b]=max(maxa.get(b,0),a)
small=[i for i,((b,p),a) in enumerate(zip(items,areas)) if a<maxa[b] and a<50000]
print('fragmentos pequenos',len(small))
from shapely.strtree import STRtree
geoms=[p for _,p in items]; st=STRtree(geoms)
for i in sorted(small,key=lambda i:areas[i]):
    b,p=items[i]; best=None;bl=0
    for j in st.query(p.buffer(1)):
        if j==i or items[j][0]==b: continue
        l=p.buffer(1).intersection(items[j][1]).area
        if l>bl: bl=l;best=j
    if best is not None: items[i][0]=items[best][0]
final={}
for b,p in items: final.setdefault(b,[]).append(p)
final={b:shapely.union_all(ps).buffer(0.5).buffer(-0.5) for b,ps in final.items()}
# distrito majoritario
out=[]
for b,g in final.items():
    best=max(dist,key=lambda d:d[1].intersection(g).area)[0] if True else ''
    nparts=len(shapely.get_parts(g))
    gw=transform(inv.transform,g).simplify(0.00005,preserve_topology=True)
    out.append({'type':'Feature','properties':{'bairro':b,'distrito':best,'area_km2':round(g.area/1e6,3),'partes':nparts,
       'enderecos':int(cnt[cnt.BAIRRO==b].n.sum())},'geometry':mapping(gw)})
json.dump({'type':'FeatureCollection','features':out},open('bairros_bruto.geojson','w'),ensure_ascii=False)
F.to_pickle('faces.pkl')
print('final',len(out),'area total km2',round(sum(o['properties']['area_km2'] for o in out),1),'multi-partes',sum(o['properties']['partes']>1 for o in out),time.time()-t0)
