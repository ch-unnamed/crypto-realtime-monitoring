from typing import Any
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config.settings import settings


class PriceResponse(BaseModel):
    symbol: str
    price: float
    ts_event: datetime
    source: str


app = FastAPI(
    title="Crypto Realtime Monitor",
    version="1.0.0",
)


def get_db_connection():
    conn = psycopg2.connect(settings.db_dsn, cursor_factory=RealDictCursor)
    conn.autocommit = True
    return conn


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/prices/latest", response_model=PriceResponse)
def get_latest_price(symbol: str = "BTCUSDT") -> PriceResponse:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT symbol, price, ts_event, source
                FROM raw_prices
                WHERE symbol = %s
                ORDER BY ts_event DESC
                LIMIT 1
                """,
                (symbol,),
            )
            row = cur.fetchone() 

        if row is None:
            raise HTTPException(status_code=404, detail="No hay datos para ese símbolo")

        return PriceResponse(
            symbol=row["symbol"],
            price=float(row["price"]),
            ts_event=row["ts_event"],
            source=row["source"],
        )
    finally:
        conn.close()
