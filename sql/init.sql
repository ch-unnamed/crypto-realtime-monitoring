CREATE TABLE IF NOT EXISTS raw_prices (
    id        BIGSERIAL PRIMARY KEY,
    symbol    VARCHAR(20) NOT NULL,
    price     NUMERIC(18,8) NOT NULL,
    volume    NUMERIC(18,8),
    ts_event  TIMESTAMPTZ,
    source    VARCHAR(50) NOT NULL
);
