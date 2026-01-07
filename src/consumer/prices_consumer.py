import json
import logging
import time
from typing import Any

import psycopg2
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from config.settings import settings
from shared.models import PriceEvent

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

def get_db_connection():
    logger.info("Conectando a la DB -> %s", settings.db_dsn)
    conn = psycopg2.connect(settings.db_dsn)
    conn.autocommit = True
    return conn

def insert_price_event(conn, event: PriceEvent) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw_prices (symbol, price, volume, ts_event, source)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                event.symbol,
                event.price,
                event.volume,
                event.ts_event,
                event.source,
            ),
        )

def create_consumer(max_retries: int = 10, delay_seconds: int = 3) -> KafkaConsumer:
    attempt = 1
    while True:
        try:
            logger.info("Intentando conectar con Kafka %s, intento %s/%s", settings.kafka_bootstrap_servers,attempt,max_retries,)
            consumer = KafkaConsumer(
                settings.kafka_prices_topic,
                bootstrap_servers = settings.kafka_bootstrap_servers,
                value_deserializer =lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset = "earliest",
                enable_auto_commit = True,
                group_id = "prices-consumer-group",
            )
            logger.info("Consumer conectado a Kafka")
            return consumer
        except NoBrokersAvailable as exc:
            logger.warning("Kafka off: %s", exc)
            if attempt >= max_retries:
                "No se puedo conectar con Kafka"
                raise
            attempt =+ 1
            time.sleep(delay_seconds)

def main() -> None:
    conn = get_db_connection()

    consumer = create_consumer()
    logger.info("Escuchando mensajes en el topic %s", settings.kafka_prices_topic,)

    for msg in consumer:
        try:
            logger.info("Mensaje recibido: %s",msg.value)
            event = PriceEvent.model_validate(msg.value)
            insert_price_event(conn, event)
        except Exception as exc:
            logger.exception("Error en el mensaje %s: %s", msg.value,exc)



if __name__ == "__main__":
    main()
