"""MQTT subscriber stub — connect on gateway startup in v0.1."""

from gateway.config import settings


def broker_url() -> str:
    return f"{settings.mqtt_broker_host}:{settings.mqtt_broker_port}"


def subscribe_topics() -> list[str]:
    prefix = settings.mqtt_topic_prefix.rstrip("/")
    return [f"{prefix}/+/telemetry", f"{prefix}/+/status"]
