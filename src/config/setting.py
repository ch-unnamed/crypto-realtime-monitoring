#Importo las librerías necesarias para centralizar los configs
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #Postgres
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    #Kafka
    kafka_bootstrap_servers: str
    kafka_prices_topic: str =  "prices"

    #API
    api_port: int = 8000

    #Binance
    binance_base_url: AnyHttpUrl
    binance_symbol: str = "BTCUSDT"
    binance_poll_seconds: int = 1

    class Config:
        env_file = ".env"
        env_file_coding = "utf-8"
        case_sensitive = False

settings = Settings()

