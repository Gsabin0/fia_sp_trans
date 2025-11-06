import logging
from typing import Any, List

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json


def _on_send_success(record_metadata):
    logging.debug(
        "Msg OK -> Tópico: %s [Partição %s]", record_metadata.topic, record_metadata.partition
    )


def _on_send_error(excp):
    logging.error("Falha ao enviar msg para o Kafka", exc_info=excp)


class KafkaMessenger:
    def __init__(self, kafka_servers: str, topic: str):
        self.producer = None
        self.kafka_servers = kafka_servers
        self.topic = topic

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=5,
                linger_ms=20,
            )
            logging.info("KafkaProducer conectado com sucesso.")
        except KafkaError as exc:
            logging.fatal("Não foi possível conectar ao Kafka: %s", exc)
            raise

    def _normalize_messages(self, messages: Any) -> List[Any]:
        if messages is None:
            return []
        if isinstance(messages, list):
            return messages
        return [messages]

    def send_message(self, messages: Any) -> None:
        """Send messages to Kafka Broker."""
        if not self.producer:
            logging.error("Producer não inicializado. Mensagens não enviadas.")
            return

        normalized = self._normalize_messages(messages)
        if not normalized:
            logging.warning("Nenhuma mensagem para enviar ao tópico %s.", self.topic)
            return

        logging.info("Enviando %s mensagem(ns) para o tópico: %s", len(normalized), self.topic)
        try:
            for msg in normalized:
                self.producer.send(self.topic, value=msg).add_callback(_on_send_success).add_errback(
                    _on_send_error
                )
        except KafkaError as exc:
            logging.error("Erro ao enviar mensagens para %s: %s", self.topic, exc)

    def flush(self) -> None:
        """Força o envio de todas as mensagens no buffer."""
        if self.producer:
            logging.info("Forçando envio de mensagens (flush)...")
            self.producer.flush()
            logging.info("Flush concluído.")

    def close(self) -> None:
        """Close the Kafka Producer"""
        if self.producer:
            self.producer.close()
