from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PRODUCTION_ENVS = {"production", "prod"}
DEMO_PREFIX = "demo-"


class EdgeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    edge_host: str = "0.0.0.0"
    edge_port: int = 8080
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_topic_prefix: str = "castuo/edge"
    buffer_backend: str = "sqlite"
    buffer_sqlite_path: str = "./data/edge_buffer.db"
    site_id: str = "demo-site-001"
    tenant_id: str = "default"
    castuo_api_url: str = ""
    sync_batch_size: int = 100
    sync_interval_seconds: int = 60
    castuo_env: str = ""

    @model_validator(mode="after")
    def _no_demo_identity_in_production(self):
        if self.castuo_env.strip().lower() in PRODUCTION_ENVS and self.site_id.startswith(DEMO_PREFIX):
            raise ValueError(
                f"CASTUO_ENV={self.castuo_env}: set a real SITE_ID (demo-* not allowed in production)"
            )
        return self


settings = EdgeSettings()
