#!/bin/bash
set -euo pipefail

INTERVALO_CICLO_SEGUNDOS=${INTERVALO_CICLO_SEGUNDOS:-300}

LINHA_TERMO=${LINHA_TERMO:?Informe a variável de ambiente LINHA_TERMO com o termo de busca das linhas}
PREVISAO_PARADA=${PREVISAO_PARADA:?Informe a variável de ambiente PREVISAO_PARADA com o código da parada}
PREVISAO_LINHA=${PREVISAO_LINHA-}
TOPIC_POSICAO=${TOPIC_POSICAO:-sptrans.posicao}
TOPIC_PREVISAO=${TOPIC_PREVISAO:-sptrans.previsao}
TOPIC_LINHAS=${TOPIC_LINHAS:-sptrans.linhas}

while true; do
    echo "----------------------------------------------------"
    echo "Iniciando ciclo de coleta: $(date)"
    echo "----------------------------------------------------"

    ARGS=(
        --linha-termo "$LINHA_TERMO"
        --previsao-parada "$PREVISAO_PARADA"
        --topic-posicao "$TOPIC_POSICAO"
        --topic-previsao "$TOPIC_PREVISAO"
        --topic-linhas "$TOPIC_LINHAS"
    )

    if [[ -n "$PREVISAO_LINHA" ]]; then
        ARGS+=(--previsao-linha "$PREVISAO_LINHA")
    fi

    python3 main.py "${ARGS[@]}"

    echo "Ciclo finalizado. Próxima execução em $INTERVALO_CICLO_SEGUNDOS segundos."
    echo "----------------------------------------------------"
    sleep "$INTERVALO_CICLO_SEGUNDOS"
done
