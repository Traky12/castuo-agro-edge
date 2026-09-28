"""Production must never start with demo identities.

CASTUO_ENV=production + any demo-* identifier -> explicit configuration
error, so a real gateway cannot silently operate as demo-device-001.
Development (CASTUO_ENV unset or non-production) keeps the demo defaults.
"""

import importlib

import pytest
from pydantic import ValidationError

IDS = ("DEVICE_ID", "MQTT_CLIENT_ID", "SITE_ID")


@pytest.fixture
def mqtt_cfg(monkeypatch):
    for key in (*IDS, "CASTUO_ENV"):
        monkeypatch.delenv(key, raising=False)

    def load(**env):
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        import gateway.mqtt.config as cfg

        return importlib.reload(cfg)

    return load


def test_mqtt_production_with_demo_ids_fails(mqtt_cfg):
    cfg = mqtt_cfg(CASTUO_ENV="production")
    with pytest.raises(cfg.DemoIdentityInProductionError) as exc:
        cfg.ensure_real_identity()
    assert "DEVICE_ID" in str(exc.value) and "MQTT_CLIENT_ID" in str(exc.value)


def test_mqtt_production_with_explicit_ids_passes(mqtt_cfg):
    cfg = mqtt_cfg(CASTUO_ENV="production", DEVICE_ID="rpi-zone-7", MQTT_CLIENT_ID="gw-zone-7")
    cfg.ensure_real_identity()


@pytest.mark.parametrize("env", [None, "development", "staging"])
def test_mqtt_non_production_allows_demo_defaults(mqtt_cfg, env):
    cfg = mqtt_cfg(**({"CASTUO_ENV": env} if env else {}))
    cfg.ensure_real_identity()


def test_edge_settings_production_with_demo_site_fails(monkeypatch):
    monkeypatch.delenv("SITE_ID", raising=False)
    monkeypatch.setenv("CASTUO_ENV", "production")
    from gateway.config import EdgeSettings

    with pytest.raises(ValidationError, match="SITE_ID"):
        EdgeSettings(_env_file=None)


def test_edge_settings_production_with_explicit_site_passes(monkeypatch):
    monkeypatch.setenv("CASTUO_ENV", "production")
    monkeypatch.setenv("SITE_ID", "finca-norte")
    from gateway.config import EdgeSettings

    assert EdgeSettings(_env_file=None).site_id == "finca-norte"


def test_edge_settings_development_allows_demo_site(monkeypatch):
    monkeypatch.delenv("CASTUO_ENV", raising=False)
    monkeypatch.delenv("SITE_ID", raising=False)
    from gateway.config import EdgeSettings

    assert EdgeSettings(_env_file=None).site_id == "demo-site-001"
