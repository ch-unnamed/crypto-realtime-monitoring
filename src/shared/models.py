from pydantic import BaseModel
from datetime import datetime

class PriceEvent(BaseModel):
    symbol: str
    price: float
    volume: float | None = None
    ts_event: datetime
    source: str = "binance"
