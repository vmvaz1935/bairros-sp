#!/usr/bin/env bash
# Prepara os dados brutos em dados_brutos/.
# O CNEFE (186 MB) está no repositório dividido em duas partes (limite de 100 MB por arquivo do GitHub);
# este script remonta o .zip e confere o SHA-256. Se as partes não estiverem presentes, baixa do IBGE.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dados_brutos
cd dados_brutos
if ls 3550308_SAO_PAULO.zip.part* >/dev/null 2>&1; then
  cat 3550308_SAO_PAULO.zip.part* > 3550308_SAO_PAULO.zip
else
  curl -fL -C - -A "bairros-sp/1.0" -o 3550308_SAO_PAULO.zip \
    https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE/CSV/Municipio/35_SP/3550308_SAO_PAULO.zip
fi
if [ ! -f cep_sp.csv ]; then
  curl -fL -A "bairros-sp/1.0" "https://data.mendeley.com/public-files/datasets/g97jb8fp57/files/6f58dc4b-7edc-41cd-bee0-1d1be8b366a2/file_downloaded" \
    | grep -a ';SP;São Paulo;' > cep_sp.csv
fi
sha256sum -c SHA256SUMS
