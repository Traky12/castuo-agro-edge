import os
from pathlib import Path

BASE_DIR = Path(os.getenv("CASTUO_GATEWAY_DIR", "/opt/castuo-edge"))
DATA_DIR = Path(os.getenv("CASTUO_DATA_DIR", str(BASE_DIR / "data")))
DB_PATH = Path(os.getenv("CASTUO_DB_PATH", str(DATA_DIR / "buffer.db")))

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "demo-client-001")
MQTT_TOPIC_SUB = os.getenv("MQTT_TOPIC_SUB", "castuo/+/sensors")
MQTT_TOPIC_STATUS = os.getenv("MQTT_TOPIC_STATUS", "castuo/gateway/status")
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "30"))

BACKEND_URL = os.getenv("BACKEND_URL", "")
API_KEY = os.getenv("API_KEY", "")
DEVICE_ID = os.getenv("DEVICE_ID", "demo-device-001")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))
SYNC_BATCH = int(os.getenv("SYNC_BATCH", "100"))

CASTUO_ENV = os.getenv("CASTUO_ENV", "")
PRODUCTION_ENVS = {"production", "prod"}
DEMO_PREFIX = "demo-"


class DemoIdentityInProductionError(RuntimeError):
    """Raised when production would start with demo-* identities."""


def ensure_real_identity():
    """Refuse to run in production with demo identities (set them in the env file)."""
    if CASTUO_ENV.strip().lower() not in PRODUCTION_ENVS:
        return
    demo = [name for name, value in (("MQTT_CLIENT_ID", MQTT_CLIENT_ID), ("DEVICE_ID", DEVICE_ID))
            if value.startswith(DEMO_PREFIX)]
    if demo:
        raise DemoIdentityInProductionError(
            f"CASTUO_ENV={CASTUO_ENV}: set real values for {', '.join(demo)} (demo-* not allowed in production)"
        )
