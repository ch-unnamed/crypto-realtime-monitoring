import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

import requests
from kafka import KafkaProducer
from kafka.errors import BrokerNotAvailableError

from config.settings import settings
from shared.models import PriceEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_binance_price(symbol: str) ->PriceEvent:
    url = f"{settings.binance_base_url}/api/v3/ticker/price"
    params = {"symbol": symbol.upper()}

    resp = requests.get(url,params=params, timeout=5)
    resp.raise_for_status()
    data: dict[str,Any] = resp.json()

    price = float(data["price"])
    return PriceEvent(
        symbol=data["symbol"],
        price=price,
        volume=None,
        ts_event=datetime.now(timezone.utc),
        source="binance-rest",
    )

def create_producer(max_retries: int = 10, delay_seconds: int = 3)-> KafkaProducer:
    attempt = 1
    while True:
        try:
            logger.info("Intento [%s] de [%s] para conectar a Kafka %s",attempt,max_retries,settings.kafka_bootstrap_servers)
            producer = KafkaProducer(bootstrap_servers = settings.kafka_bootstrap_servers, value_serializer= lambda v: json.dumps(v, default=str).encode("utf-8"),)
            logger.info("Conectado a Kafka %s", settings.kafka_bootstrap_servers)
            return producer
        except BrokerNotAvailableError as exc:
            logger.warning("Error al conectar con Kafka: %s", exc)
            if attempt >= max_retries:
                logger.error("No se pudo conectar, máximos intentos alcanzados")
                raise
            attempt=+1
            time.sleep(delay_seconds)

def main() -> None:
    producer = create_producer()
    logger.info("Producer Binance->Enviando precios de %s al topic %s",settings.binance_symbol,settings.kafka_prices_topic,)

    while True:
        try:
            event = fetch_binance_price(settings.binance_symbol)
            producer.send(settings.kafka_prices_topic, value=event.model_dump())
            logger.info("Evento enviado: %s", event.model_dump())
        except Exception as exc:
            logger.exception("Error en el envío/recepción de precios de Binance: %s", exc)
        time.sleep(settings.binance_poll_seconds)

if __name__ == "__main__":
    main()