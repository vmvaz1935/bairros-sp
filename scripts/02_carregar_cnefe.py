# Lê o CNEFE da capital e guarda as colunas usadas
import pandas as pd, zipfile
z=zipfile.ZipFile('dados_brutos/3550308_SAO_PAULO.zip')
cols=['COD_DISTRITO','COD_SETOR','NUM_QUADRA','NUM_FACE','CEP','DSC_LOCALIDADE','LATITUDE','LONGITUDE','NV_GEO_COORD','COD_ESPECIE']
parts=[]; n=0
for ch in pd.read_csv(z.open('3550308_SAO_PAULO.csv'),sep=';',usecols=cols,dtype=str,chunksize=1_000_000,encoding='utf-8'):
    n+=len(ch); parts.append(ch)
df=pd.concat(parts); print('linhas',n)
df['LATITUDE']=df.LATITUDE.astype(float); df['LONGITUDE']=df.LONGITUDE.astype(float)
print(df.NV_GEO_COORD.value_counts())
print('localidade vazia',df.DSC_LOCALIDADE.isna().sum(),'distintas',df.DSC_LOCALIDADE.nunique())
df.to_pickle('cnefe_slim.pkl')
print(df.DSC_LOCALIDADE.value_counts().head(30))
