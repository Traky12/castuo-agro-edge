"""Code defaults must be unambiguous demo values, never real identifiers.

Real deployments set these through environment variables. A default that
names a real device, site or client would leak infrastructure identifiers
into a public repository.
"""

import importlib

import pytest

DEMO_DEFAULTS = {
    "DEVICE_ID": "demo-device-001",
    "MQTT_CLIENT_ID": "demo-client-001",
}


@pytest.fixture
def clean_env(monkeypatch):
    for key in (*DEMO_DEFAULTS, "SITE_ID", "TENANT_ID"):
        monkeypatch.delenv(key, raising=False)


def test_mqtt_gateway_defaults_are_demo_values(clean_env):
    import gateway.mqtt.config as cfg

    cfg = importlib.reload(cfg)
    for name, expected in DEMO_DEFAULTS.items():
        assert getattr(cfg, name) == expected


def test_edge_settings_site_default_is_demo_value(clean_env):
    from gateway.config import EdgeSettings

    settings = EdgeSettings(_env_file=None)
    assert settings.site_id == "demo-site-001"
    assert settings.tenant_id == "default"


def test_env_still_overrides_defaults(monkeypatch):
    monkeypatch.setenv("DEVICE_ID", "custom-device")
    import gateway.mqtt.config as cfg

    cfg = importlib.reload(cfg)
    assert cfg.DEVICE_ID == "custom-device"
