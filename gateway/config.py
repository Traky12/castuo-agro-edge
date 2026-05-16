from pydantic_settings import BaseSettings, SettingsConfigDict


class EdgeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    edge_host: str = "0.0.0.0"
    edge_port: int = 8080
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_topic_prefix: str = "castuo/edge"
    buffer_backend: str = "sqlite"
    buffer_sqlite_path: str = "./data/edge_buffer.db"
    site_id: str = "site-01"
    tenant_id: str = "default"
    castuo_api_url: str = ""
    sync_batch_size: int = 100
    sync_interval_seconds: int = 60


settings = EdgeSettings()
