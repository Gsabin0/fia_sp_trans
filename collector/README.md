# Coletor SPTrans

Ferramentas para coletar dados da API Olho Vivo e enviar as informações para tópicos Kafka.

## Variáveis de ambiente necessárias

Crie um arquivo `.env` (ou exporte as variáveis no shell) com os valores abaixo:

```
SPTRANS_API_TOKEN="<token da API Olho Vivo>"
# ou defina SPTRANS_API_TOKEN_COMMAND com um comando que retorne o token
# SPTRANS_API_TOKEN_COMMAND="aws secretsmanager get-secret-value ..."
OLHO_VIVO_URL="http://api.olhovivo.sptrans.com.br/v2.1"  # opcional
KAFKA_BOOTSTRAP_SERVERS="localhost:9092"                  # opcional
```

Caso `SPTRANS_API_TOKEN_COMMAND` esteja configurado, o `run_microservice.sh` executará o comando em cada ciclo e exportará o valor retornado para `SPTRANS_API_TOKEN` antes de chamar o coletor.

## Executando manualmente

O script `main.py` realiza as três coletas necessárias:

- **Posição dos veículos** (`/Posicao`)
- **Previsão de chegada** (`/Previsao`)
- **Linhas** (`/Linha/Buscar`)

Exemplo de execução:

```
python3 main.py \
  --linha-termo "8000" \
  --previsao-parada "123456" \
  --previsao-linha "8000" \
  --topic-posicao "sptrans.posicao" \
  --topic-previsao "sptrans.previsao" \
  --topic-linhas "sptrans.linhas"
```

Os parâmetros `--topic-*` são opcionais e permitem customizar os tópicos criados no Kafka. O parâmetro `--previsao-linha` também é opcional (a API retorna todas as linhas da parada quando omitido).

## Execução contínua

O script `run_microservice.sh` automatiza a coleta em ciclos. Configure as variáveis abaixo e execute o shell script:

```
export LINHA_TERMO="8000"
export PREVISAO_PARADA="123456"
export PREVISAO_LINHA="8000"      # opcional
export TOPIC_POSICAO="sptrans.posicao"  # opcional
export TOPIC_PREVISAO="sptrans.previsao" # opcional
export TOPIC_LINHAS="sptrans.linhas"     # opcional
export INTERVALO_CICLO_SEGUNDOS=300       # opcional
# ou exporte SPTRANS_API_TOKEN_COMMAND para buscar o token dinamicamente
# export SPTRANS_API_TOKEN_COMMAND="aws secretsmanager get-secret-value --query 'SecretString' --output text"

./run_microservice.sh
```

Cada ciclo executa `main.py` com os parâmetros definidos, cria os tópicos se necessário e publica os dados retornados pela API.
