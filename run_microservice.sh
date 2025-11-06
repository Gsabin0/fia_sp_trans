#!/bin/bash

# --- Configurações ---
ARQUIVO_DE_ENDPOINTS="endpoints.txt"
SCRIPT_PYTHON="main.py"
INTERVALO_CICLO_SEGUNDOS=300
ESPERA_ENTRE_CHAMADAS_SEGUNDOS=5

# --- Loop Infinito (Ciclo Externo) ---
while true
do
    echo "----------------------------------------------------"
    echo "INICIANDO NOVO CICLO COMPLETO DE COLETA"
    echo "Data/Hora: $(date)"
    echo "Lendo parâmetros de: $ARQUIVO_DE_ENDPOINTS"
    echo "----------------------------------------------------"

    # --- Loop Interno (Lê o arquivo linha por linha) ---
    
    # ***** INÍCIO DA MUDANÇA *****
    # Usamos 'tr -d '\r'' para deletar o caractere Carriage Return (CR)
    # antes que o 'while' leia a linha. Isso "limpa" a entrada.
    tr -d '\r' < "$ARQUIVO_DE_ENDPOINTS" | while read -r parametro
    # ***** FIM DA MUDANÇA *****
    
    do
        # Ignora linhas em branco ou comentários (linhas que começam com #)
        if [[ -n "$parametro" && ! "$parametro" =~ ^# ]]; then
            echo ""
            echo "[$(date +%T)] Executando coleta para: '$parametro'"
            
            # Agora '$parametro' estará limpo (ex: "posicao" e não "posicao\r")
            python3 "$SCRIPT_PYTHON" --get "$parametro"
            
            echo "[$(date +%T)] Coleta de '$parametro' concluída."
            
            echo "Aguardando $ESPERA_ENTRE_CHAMADAS_SEGUNDOS segundos..."
            sleep $ESPERA_ENTRE_CHAMADAS_SEGUNDOS
        fi
    
    # A linha 'done < "$ARQUIVO_DE_ENDPOINTS"' foi movida para cima,
    # para dentro do pipe 'tr'.
    done

    echo "----------------------------------------------------"
    echo "CICLO COMPLETO CONCLUÍDO."
    echo "Aguardando $INTERVALO_CICLO_SEGUNDOS segundos para recomeçar."
    echo "----------------------------------------------------"
    
    sleep $INTERVALO_CICLO_SEGUNDOS

done