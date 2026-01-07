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
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def db_dsn(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()

