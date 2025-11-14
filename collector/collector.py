"""Utilities to interact with the SPTrans Olho Vivo API."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

from kafka_messenger_utils import KafkaMessenger
from kafka_topic_utils import KafkaAdm


class SpTransAPI:
    """Simple client responsible for authenticating and requesting data."""

    def __init__(self, api_token: str, base_url: str) -> None:
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self._session: Optional[requests.Session] = None

    def authenticate(self) -> bool:
        """Authenticate against the SPTrans API and keep the session alive."""
        auth_url = urljoin(f"{self.base_url}/", f"Login/Autenticar?token={self.api_token}")
        session = requests.Session()

        try:
            response = session.post(auth_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            logging.error("Erro de conexão durante a autenticação: %s", exc)
            return False

        if response.text.strip().lower() == "true":
            logging.info("Autenticação bem-sucedida na API da SPTrans.")
            self._session = session
            return True

        logging.error("Falha na autenticação. Resposta da API: %s", response.text)
        return False

    def get(self, resource_path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Perform a GET request using the authenticated session."""
        if not self._session:
            raise RuntimeError("Sessão não autenticada. Execute 'authenticate' antes de coletar dados.")

        url = urljoin(f"{self.base_url}/", resource_path.lstrip("/"))

        try:
            response = self._session.get(url, params=params)
            response.raise_for_status()
            if not response.text:
                logging.warning("Resposta vazia da API para %s", resource_path)
                return None
            return response.json()
        except requests.exceptions.RequestException as exc:
            logging.error("Erro ao acessar %s: %s", url, exc)
        except json.JSONDecodeError:
            logging.error("Não foi possível converter a resposta da API em JSON.")

        return None


def publish_to_kafka(kafka_servers: str, topic: str, payload: Any) -> None:
    """Create (if necessary) the Kafka topic and publish the payload."""
    if payload is None:
        logging.warning("Nenhum dado para enviar ao tópico %s.", topic)
        return

    kafka_topic = KafkaAdm(kafka_servers, topic)
    kafka_topic.criar_topico()

    messenger = KafkaMessenger(kafka_servers, topic)
    try:
        messenger.send_message(payload)
        messenger.flush()
    finally:
        messenger.close()
