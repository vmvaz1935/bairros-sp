import json,re,unicodedata,pandas as pd,numpy as np,shapely
from shapely.geometry import shape
from shapely.strtree import STRtree
def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().upper()
    s=re.sub(r'\(.*?\)','',s)
    for a,b in [(r'\bJD\b','JARDIM'),(r'\bVL\b','VILA'),(r'\bPQ\b','PARQUE'),(r'\bCH\b','CHACARA'),(r'\bSTA\b','SANTA'),(r'\bSTO\b','SANTO'),(r'\bCJ\b|\bCONJ\b','CONJUNTO'),(r'\bRES\b','RESIDENCIAL'),(r'\bCID\b','CIDADE')]: s=re.sub(a,b,s)
    return re.sub(r'\s+',' ',s).strip()
B=json.load(open('dados/bairros_sp.geojson'))['features']
G=[shape(f['geometry']) for f in B]; names=[f['properties']['bairro'] for f in B]; nn=[norm(n) for n in names]
st=STRtree(G)
def where(pt):
    r=st.query(pt,predicate='within'); return r[0] if len(r) else None
# 1 OSM points
O=json.load(open('dados/osm_bairros_e_distritos.geojson'))['features']
dn={norm(x['properties']['name']) for x in O if x['properties']['layer']=='distrito'}
pts=[(x['properties']['name'],shape(x['geometry'])) for x in O if x['properties']['layer']=='bairro_ponto' and x['properties']['name'] and x['properties']['name']!='?']
ok=tot=0; known=0; miss=[]
nnset=set(nn)
for n,p in pts:
    k=norm(n)
    if k not in nnset: continue
    known+=1; i=where(p)
    if i is None: continue
    tot+=1
    # aceita se dentro do poligono com mesmo nome ou a <300m dele
    j=nn.index(k)
    d=shapely.distance(shapely.Point(p.x,p.y),G[j])*111000*0.92
    if nn[i]==k: ok+=1
    elif d<0.0: pass
    else: miss.append((n,names[i],round(d)))
print(f'OSM: {len(pts)} pontos, {known} com nome existente nos Correios; dentro do poligono de mesmo nome: {ok}/{tot} = {100*ok/tot:.1f}%')
md=np.array([m[2] for m in miss]); print('  dos que caem fora: distancia ate o poligono certo  mediana',np.median(md),'m; <500m:',(md<500).sum(),'de',len(md))
print('  exemplos fora >1km:',[m for m in miss if m[2]>1000][:15])
# 2 CNEFE localidade especifica (diferente de distrito)
F=pd.read_pickle('faces.pkl')
m=pd.read_pickle('cnefe_cep.pkl')
m=m[m.BAIRRO.notna()]
m['L']=m.DSC_LOCALIDADE.map(norm); m['Bn']=m.BAIRRO.map(norm)
spec=m[~m.L.isin(dn|{'SAO PAULO'}) & m.L.isin(set(m.Bn))]
print(f'CNEFE: {len(spec)} enderecos com localidade especifica que tambem e nome Correios; concordancia endereco a endereco: {100*(spec.L==spec.Bn).mean():.1f}%')
# 3 bairros conhecidos
for q in ['Vila Nova Conceição','Brooklin Paulista','Jardim Paulista','Vila Madalena','Higienópolis','Chácara Klabin','Itaim Bibi','Moema','Jardim Europa','Jardim América','Cerqueira César','Paraíso','Vila Olímpia','Pinheiros','Bela Vista','Consolação','Panamby','Vila Mariana','Tatuapé','Sumarezinho','Perdizes','Pompeia']:
    hit=[f['properties'] for f in B if norm(f['properties']['bairro'])==norm(q)]
    print(' ',q,'->',[(h['bairro'],h['area_km2'],h['partes']) for h in hit] or 'NAO ENCONTRADO')
a=np.array([f['properties']['area_km2'] for f in B]); print('area km2: mediana',np.median(a),'p10',np.percentile(a,10),'p90',np.percentile(a,90))
p=np.array([f['properties']['partes'] for f in B]); print('partes: 1=',(p==1).sum(),' 2-3=',((p>1)&(p<4)).sum(),' >=4=',(p>=4).sum())
print('mais fragmentados',sorted([(f['properties']['partes'],f['properties']['bairro']) for f in B])[-10:])
