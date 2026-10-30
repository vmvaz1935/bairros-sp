#!/usr/bin/env bash
# Baixa os dados brutos (não versionados) para dados_brutos/
set -euo pipefail
mkdir -p dados_brutos
UA="bairros-sp/1.0"
# CNEFE 2022 – endereços do município de São Paulo (IBGE), ~186 MB
curl -fL -C - -A "$UA" -o dados_brutos/3550308_SAO_PAULO.zip \
  https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE/CSV/Municipio/35_SP/3550308_SAO_PAULO.zip
# Base de CEPs do Brasil 2018 (Mendeley Data, CC BY 4.0), filtrada para a capital
curl -fL -A "$UA" "https://data.mendeley.com/public-files/datasets/g97jb8fp57/files/6f58dc4b-7edc-41cd-bee0-1d1be8b366a2/file_downloaded" \
  | grep -a ';SP;São Paulo;' > dados_brutos/cep_sp.csv
# Distritos e pontos de bairro do OpenStreetMap: já versionados em dados/osm_bairros_e_distritos.geojson
