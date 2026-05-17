import json
import logging
import signal
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from config import *
from db import BufferDB
from sync import SyncWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("castuo-mqtt-gateway")

for p in (DATA_DIR, DB_PATH.parent):
    p.mkdir(parents=True, exist_ok=True)

buffer_db = BufferDB(DB_PATH)
syncer = SyncWorker(buffer_db, BACKEND_URL, API_KEY, DEVICE_ID, batch_size=SYNC_BATCH)
stop_event = threading.Event()

def publish_status(client, online: bool):
    payload = {
        "device_id": DEVICE_ID,
        "online": online,
        "db": buffer_db.stats(),
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    client.publish(MQTT_TOPIC_STATUS, json.dumps(payload, ensure_ascii=False), qos=1, retain=False)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log.info("MQTT connected")
        client.subscribe(MQTT_TOPIC_SUB, qos=1)
        publish_status(client, True)
    else:
        log.error("MQTT connect failed rc=%s", rc)

def on_disconnect(client, userdata, rc):
    log.warning("MQTT disconnected rc=%s", rc)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8", errors="ignore"))
    except Exception:
        payload = {"raw": msg.payload.decode("utf-8", errors="ignore")}
    buffer_db.enqueue(msg.topic, payload)
    log.info("Buffered topic=%s pending=%s", msg.topic, buffer_db.stats()["pending"])

def sync_loop():
    while not stop_event.is_set():
        syncer.run_once()
        time.sleep(POLL_INTERVAL)

def handle_stop(*_):
    stop_event.set()

def main():
    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    sync_thread = threading.Thread(target=sync_loop, daemon=True)
    sync_thread.start()

    client.connect(MQTT_HOST, MQTT_PORT, keepalive=MQTT_KEEPALIVE)
    client.loop_start()

    try:
        while not stop_event.is_set():
            publish_status(client, True)
            time.sleep(max(5, POLL_INTERVAL))
    finally:
        publish_status(client, False)
        client.loop_stop()
        client.disconnect()
        buffer_db.close()

if __name__ == "__main__":
    main()
