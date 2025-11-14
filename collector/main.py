import argparse
import logging
import os
import sys
from typing import Dict, Optional

from dotenv import load_dotenv

from collector import SpTransAPI, publish_to_kafka


DEFAULT_TOPIC_POSICAO = "sptrans.posicao"
DEFAULT_TOPIC_PREVISAO = "sptrans.previsao"
DEFAULT_TOPIC_LINHAS = "sptrans.linhas"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Coleta dados da API Olho Vivo da SPTrans e publica em tópicos Kafka."
    )
    parser.add_argument(
        "--linha-termo",
        dest="linha_termo",
        required=True,
        help="Termo utilizado na busca de linhas (endpoint Linha/Buscar).",
    )
    parser.add_argument(
        "--previsao-parada",
        dest="previsao_parada",
        required=True,
        help="Código da parada utilizado no endpoint Previsao.",
    )
    parser.add_argument(
        "--previsao-linha",
        dest="previsao_linha",
        default=None,
        help="Código da linha utilizado no endpoint Previsao (opcional).",
    )
    parser.add_argument(
        "--topic-posicao",
        dest="topic_posicao",
        default=DEFAULT_TOPIC_POSICAO,
        help="Nome do tópico Kafka para posição dos veículos.",
    )
    parser.add_argument(
        "--topic-previsao",
        dest="topic_previsao",
        default=DEFAULT_TOPIC_PREVISAO,
        help="Nome do tópico Kafka para previsão de chegada.",
    )
    parser.add_argument(
        "--topic-linhas",
        dest="topic_linhas",
        default=DEFAULT_TOPIC_LINHAS,
        help="Nome do tópico Kafka para dados das linhas.",
    )
    return parser.parse_args()


def _collect_and_publish(
    client: SpTransAPI,
    kafka_bootstrap: str,
    topic: str,
    resource_path: str,
    params: Optional[Dict[str, str]] = None,
) -> bool:
    data = client.get(resource_path, params=params)
    if data is None:
        logging.error("Nenhum dado retornado para %s.", resource_path)
        return False

    publish_to_kafka(kafka_bootstrap, topic, data)
    logging.info("Dados publicados no tópico %s.", topic)
    return True


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()

    args = parse_args()

    api_token = os.getenv("SPTRANS_API_TOKEN")
    base_url = os.getenv("OLHO_VIVO_URL", "http://api.olhovivo.sptrans.com.br/v2.1")
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    if not api_token:
        logging.error("Variável de ambiente SPTRANS_API_TOKEN não configurada.")
        return 1

    client = SpTransAPI(api_token, base_url)
    if not client.authenticate():
        return 1

    success = True

    success &= _collect_and_publish(client, kafka_bootstrap, args.topic_posicao, "Posicao")

    previsao_params = {"codigoParada": args.previsao_parada}
    if args.previsao_linha:
        previsao_params["codigoLinha"] = args.previsao_linha
    success &= _collect_and_publish(client, kafka_bootstrap, args.topic_previsao, "Previsao", previsao_params)

    linha_params = {"termosBusca": args.linha_termo}
    success &= _collect_and_publish(client, kafka_bootstrap, args.topic_linhas, "Linha/Buscar", linha_params)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
