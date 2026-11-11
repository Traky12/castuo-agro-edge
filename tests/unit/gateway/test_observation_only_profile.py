"""Pilot profile: observation only.

No actuator, local rule or physical command is subscribed to, accepted or executed by
the pilot gateway. Three independent mechanical checks, so that one cannot hide a
regression in another:

  1. the handler refuses command topics (fail-closed),
  2. the default subscription cannot match any command topic,
  3. no gateway or evidence-bridge source mentions actuator hardware.

What this does NOT prove: that a deployment's broker ACLs block publishers, or that
firmware cannot actuate. Those are broker and device concerns outside this repository's
unit tests.
"""
import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]

COMMAND_TOPICS = [
    "castuo/zona1/commands/riego/set",
    "castuo/commands/zona1/riego",
    "castuo/actuators/zona1/riego/on",
    "castuo/invernadero/zona1/actuators/riego/off",
    "castuo/zona1/riego/set",
]


def mqtt_topic_matches(topic_filter: str, topic: str) -> bool:
    """MQTT 3.1.1 wildcard matching: '+' is one level, '#' is the rest (last level only)."""
    f_parts, t_parts = topic_filter.split("/"), topic.split("/")
    for i, f in enumerate(f_parts):
        if f == "#":
            return i == len(f_parts) - 1
        if i >= len(t_parts):
            return False
        if f != "+" and f != t_parts[i]:
            return False
    return len(f_parts) == len(t_parts)


def test_the_topic_matcher_itself_is_sound():
    assert mqtt_topic_matches("castuo/+/sensors", "castuo/zona1/sensors")
    assert not mqtt_topic_matches("castuo/+/sensors", "castuo/zona1/sensors/extra")
    assert not mqtt_topic_matches("castuo/+/sensors", "castuo/a/b/sensors")
    assert mqtt_topic_matches("castuo/#", "castuo/zona1/commands/riego/set")
    assert mqtt_topic_matches("#", "anything/at/all")
    assert not mqtt_topic_matches("castuo/zona1", "castuo/zona1/sensors")


def test_default_subscription_matches_no_command_topic(monkeypatch):
    monkeypatch.delenv("MQTT_TOPIC_SUB", raising=False)
    import gateway.mqtt.config as cfg

    cfg = importlib.reload(cfg)
    assert "#" not in cfg.MQTT_TOPIC_SUB, "a wildcard subscription would receive command topics"
    assert mqtt_topic_matches(cfg.MQTT_TOPIC_SUB, "castuo/zona1/sensors"), "the matcher must see real sensor traffic"
    for topic in COMMAND_TOPICS:
        assert not mqtt_topic_matches(cfg.MQTT_TOPIC_SUB, topic), topic


FORBIDDEN = re.compile(r"gpio|relay|valve|pump", re.IGNORECASE)


@pytest.mark.parametrize("package", ["gateway", "evidence_bridge"])
def test_no_actuator_hardware_is_referenced_by_pilot_code(package):
    offenders = []
    files = sorted((ROOT / package).rglob("*.py"))
    assert files, f"no python files found under {package}"
    for path in files:
        for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if FORBIDDEN.search(line):
                offenders.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
    assert offenders == []


def test_offline_mode_doc_declares_the_observation_only_profile():
    text = (ROOT / "docs" / "offline-mode" / "OVERVIEW.md").read_text(encoding="utf-8-sig")
    assert "observation only" in text.lower()
    assert "still execute" not in text.lower()


def test_local_rules_are_declared_out_of_scope_for_the_pilot():
    text = (ROOT / "edge_ai" / "local_rules" / "README.md").read_text(encoding="utf-8-sig")
    assert "OUT_OF_SCOPE" in text


WIRING_PROBE = """
import json, sys, types
sys.path.insert(0, sys.argv[1])
import main

def msg(topic, payload):
    return types.SimpleNamespace(topic=topic, payload=payload.encode("utf-8"))

good = json.dumps({"device_id": "sensor-temp-01", "metric": "temperature", "value": 21.4,
                   "unit": "degC", "occurred_at": "2026-11-11T07:55:00+00:00"})
main.on_message(None, None, msg("castuo/zona1/sensors", good))
main.on_message(None, None, msg("castuo/zona1/sensors", good))
main.on_message(None, None, msg("castuo/zona1/commands/riego/set", good))
main.on_message(None, None, msg("castuo/zona1/sensors", "not json"))
print(json.dumps({"db": main.buffer_db.stats(), "rejected": dict(main.rejections)}))
"""


def test_the_daemon_routes_every_message_through_the_handler(tmp_path):
    """The real main.on_message (not a copy) buffers valid readings and counts every rejection."""
    env = {**os.environ, "CASTUO_GATEWAY_DIR": str(tmp_path / "edge"), "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        [sys.executable, "-c", WIRING_PROBE, str(ROOT / "gateway" / "mqtt")],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stderr
    probe = json.loads(result.stdout.strip().splitlines()[-1])
    assert probe["db"] == {"pending": 1, "total": 1}
    assert probe["rejected"] == {"duplicate_source_key": 1, "actuation_topic_rejected": 1, "malformed_json": 1}
