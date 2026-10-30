# Atribui a cada endereço do CNEFE o bairro dos Correios do seu CEP
import pandas as pd
c=pd.read_csv('dados_brutos/cep_sp.csv',sep=';',header=None,dtype=str,names=['CEP','UF','CIDADE','BAIRRO','LOG','COMP'],usecols=range(6),on_bad_lines='skip')
c=c[c.CIDADE=='São Paulo'].drop_duplicates('CEP')
df=pd.read_pickle('cnefe_slim.pkl')
m=df.merge(c[['CEP','BAIRRO']],on='CEP',how='left')
print('enderecos com bairro:',round(100*m.BAIRRO.notna().mean(),1),'%')
m.to_pickle('cnefe_cep.pkl')
