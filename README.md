# Bairros de São Paulo

Polígonos dos **1.854 bairros dos Correios** da cidade de São Paulo, traçados a partir dos **5,7 milhões de endereços** do Cadastro Nacional de Endereços para Fins Estatísticos (CNEFE) do Censo 2022.

A capital não tem bairros com limite oficial. A Prefeitura define só subprefeituras e os 96 distritos (Lei 11.220/1992), e a Malha de Bairros 2022 do IBGE não inclui o município. Apps de imóveis como QuintoAndar e Zap usam a divisão por bairro dos Correios, a mesma reconstruída aqui.

Mapa interativo: [`docs/index.html`](docs/index.html). Abra o arquivo no navegador ou ative o GitHub Pages na pasta `docs/`.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `dados/bairros_sp.geojson` | 1.854 polígonos (WGS84) com `bairro`, `distrito`, `area_km2`, `enderecos` e `partes` |
| `dados/distritos_sp.geojson` | Os 96 distritos oficiais (do OpenStreetMap, simplificados) |
| `dados/osm_bairros_e_distritos.geojson` | Extração do OpenStreetMap: distritos, polígonos e pontos de bairro |
| `kml/bairros_sp.kml` | Os bairros em KML, para o Google My Maps e o Google Earth |
| `docs/index.html` | Mapa com busca, zoom e lista dos bairros por distrito |
| `dados_brutos/` | Entradas originais: CNEFE 2022 da capital (`3550308_SAO_PAULO.zip`, 186 MB, dividido em `.part00` e `.part01`), CEPs da capital (`cep_sp.csv`) e `SHA256SUMS` |
| `scripts/` | Etapas de 01 a 06 para reproduzir tudo |

## No Google Maps

1. Abra o [Google My Maps](https://www.google.com/mymaps) e crie um mapa.
2. Na camada sem título, clique em **Importar** e envie `kml/bairros_sp.kml`.
3. Em **Estilo uniforme**, troque para **Estilo individual** se as cores não aparecerem.

O mapa fica salvo no Google Drive e abre no app Google Maps do celular, em **Você → Mapas**. No Google Earth web, use **Projetos → Abrir → Importar arquivo KML**.

## Método

1. **Endereços:** todos os endereços da capital no CNEFE 2022 com coordenada de qualidade 1 a 3 (`NV_GEO_COORD`).
2. **Bairro:** cada endereço recebe o bairro dos Correios do seu CEP. A base usada é a de CEPs de 2018 (Mendeley Data), e 99,5% dos endereços casaram.
3. **Faces de quadra:** os endereços são agrupados por face de quadra (setor + quadra + face), o que dá 244 mil faces. Cada face fica com o bairro da maioria dos seus endereços e é representada pela posição mediana deles.
4. **Suavização:** uma face com até 15 endereços cujo bairro difere de pelo menos 6 das 8 faces vizinhas passa a ter o bairro dos vizinhos.
5. **Traçado:** cada face recebe a área mais próxima dela (diagrama de Voronoi), recortada pelo limite do município. As áreas de mesmo bairro são então juntadas.
6. **Limpeza:** pedaços soltos de um bairro, menores que 25% do seu pedaço principal e que 0,3 km², passam para o vizinho com quem fazem a maior fronteira. No fim, 1.607 bairros ficam com um polígono único.

## Conferência

- **Pontos de bairro do OpenStreetMap:** 453 pontos têm nome que também existe nos Correios. Desses, 67% caem dentro do bairro de mesmo nome, e 88% ficam a até 500 m dele. A maior parte das divergências são rótulos de distrito, que os Correios dividem em bairros menores, ou nomes repetidos em lugares diferentes da cidade.
- **Nome anotado pelo recenseador no CNEFE (`DSC_LOCALIDADE`):** coincide com o bairro postal em 64% dos endereços. O recenseador costuma anotar o nome do loteamento, e em 52% dos endereços anotou só o nome do distrito.

## Limitações

- **Divisão postal:** os limites são os dos Correios. Nomes usados só no mercado, como Chácara Klabin, Panamby e Pompeia (que nos Correios é "Vila Pompéia"), não aparecem como bairro próprio.
- **CEPs novos:** a base de CEPs é de 2018, então CEPs criados depois ficam sem bairro (0,5% dos endereços).
- **Precisão do traçado:** o limite é preciso no nível da face de quadra. Em áreas com poucos endereços, como parques, represas e a zona rural de Parelheiros e Marsilac, a linha é só uma interpolação.
- **Distritos:** os bairros postais podem atravessar os limites de distrito. O campo `distrito` traz o distrito com maior sobreposição.

## Como reproduzir

```bash
pip install -r requirements.txt
bash scripts/01_baixar_dados.sh   # remonta o zip do CNEFE e confere o SHA-256
python scripts/02_carregar_cnefe.py
python scripts/03_juntar_cep.py
python scripts/04_tracar_bairros.py
python scripts/05_limpar_fragmentos.py
python scripts/06_conferir.py
```

O processo usa cerca de 4 GB de RAM e leva uns 10 minutos.

Para remontar o arquivo do CNEFE à mão: `cat dados_brutos/3550308_SAO_PAULO.zip.part* > dados_brutos/3550308_SAO_PAULO.zip`. No Windows: `copy /b 3550308_SAO_PAULO.zip.part00+3550308_SAO_PAULO.zip.part01 3550308_SAO_PAULO.zip`.

## Fontes e licenças

- IBGE, [CNEFE – Censo Demográfico 2022](https://www.ibge.gov.br/estatisticas/sociais/populacao/38734-cadastro-nacional-de-enderecos-para-fins-estatisticos.html).
- Zimmermann, I. (2019). [Códigos de CEP do Brasil por UF, cidade, bairro e logradouro](https://data.mendeley.com/datasets/g97jb8fp57), Mendeley Data, v1, doi:10.17632/g97jb8fp57.1. Licença CC BY 4.0.
- © colaboradores do [OpenStreetMap](https://www.openstreetmap.org/copyright), licença ODbL.

Os dados em `dados/` usam limites do OpenStreetMap e por isso são distribuídos sob a **Open Database License (ODbL)**. O código em `scripts/` e `docs/` é distribuído sob a licença MIT.
