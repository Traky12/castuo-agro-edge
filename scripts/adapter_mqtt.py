import json
import uuid
from datetime import datetime
import subprocess

def get_commit_sha():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except:
        return "UNKNOWN"

def create_canonical_event():
    event = {
        "canonical_event_id": f"EVT-EDGE-{uuid.uuid4().hex[:8]}",
        "repository_id": "CASTUO-EDGE-001",
        "source_event_id": "MQTT-SENSOR-001",
        "event_type": "TELEMETRY_INGESTION",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "actor": "edge-gateway-01",
        "commit_sha": get_commit_sha(),
        "capability_id": "CAP-EDGE-MQTT-001",
        "validation_state": "EXECUTED"
    }
    return event

if __name__ == "__main__":
    event = create_canonical_event()
    print(json.dumps(event, indent=2))
    with open("evidence/last_event.json", "w") as f:
        json.dump(event, f, indent=2)
