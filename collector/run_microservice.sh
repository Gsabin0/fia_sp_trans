#!/bin/bash
set -euo pipefail

LAST_GET_API_TOKEN_STATUS=0

get_api_token() {
    if [[ -n "${SPTRANS_API_TOKEN_COMMAND:-}" ]]; then
        local token status

        set +e
        token=$(bash -c "$SPTRANS_API_TOKEN_COMMAND")
        status=$?
        set -e

        if (( status != 0 )); then
            LAST_GET_API_TOKEN_STATUS=$status
            echo "Falha ao obter token da API (código ${status})." >&2
            return $status
        fi

        token=${token%%$'\r'*}
        token=${token%%$'\n'*}

        if [[ -z "$token" ]]; then
            LAST_GET_API_TOKEN_STATUS=1
            echo "Comando SPTRANS_API_TOKEN_COMMAND retornou vazio." >&2
            return 1
        fi

        export SPTRANS_API_TOKEN="$token"
    elif [[ -z "${SPTRANS_API_TOKEN:-}" ]]; then
        LAST_GET_API_TOKEN_STATUS=1
        echo "Configure SPTRANS_API_TOKEN ou SPTRANS_API_TOKEN_COMMAND para obter o token." >&2
        return 1
    fi

    LAST_GET_API_TOKEN_STATUS=0
    return 0
}

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

    if ! get_api_token; then
        status=${LAST_GET_API_TOKEN_STATUS:-1}
        echo "Não foi possível obter o token da API (código $status). Aguardando antes de tentar novamente." >&2
        echo "----------------------------------------------------"
        sleep "$INTERVALO_CICLO_SEGUNDOS"
        continue
    fi

    if python3 main.py "${ARGS[@]}"; then
        echo "Ciclo finalizado com sucesso. Próxima execução em $INTERVALO_CICLO_SEGUNDOS segundos."
    else
        status=$?
        echo "Ciclo finalizado com erro (código $status). Tentando novamente em $INTERVALO_CICLO_SEGUNDOS segundos."
    fi

    echo "----------------------------------------------------"
    sleep "$INTERVALO_CICLO_SEGUNDOS"
done
