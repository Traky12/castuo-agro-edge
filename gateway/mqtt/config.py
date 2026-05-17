import os
from pathlib import Path

BASE_DIR = Path(os.getenv("CASTUO_GATEWAY_DIR", "/opt/castuo-edge"))
DATA_DIR = Path(os.getenv("CASTUO_DATA_DIR", str(BASE_DIR / "data")))
DB_PATH = Path(os.getenv("CASTUO_DB_PATH", str(DATA_DIR / "buffer.db")))

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "castuo-mqtt-gateway")
MQTT_TOPIC_SUB = os.getenv("MQTT_TOPIC_SUB", "castuo/+/sensors")
MQTT_TOPIC_STATUS = os.getenv("MQTT_TOPIC_STATUS", "castuo/gateway/status")
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "30"))

BACKEND_URL = os.getenv("BACKEND_URL", "")
API_KEY = os.getenv("API_KEY", "")
DEVICE_ID = os.getenv("DEVICE_ID", "RPI-GW-001")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))
SYNC_BATCH = int(os.getenv("SYNC_BATCH", "100"))
