# Troubleshooting

| Symptom | Check |
|---------|--------|
| Gateway unhealthy | `curl localhost:8080/health` |
| No MQTT messages | `mosquitto_sub -h localhost -t 'castuo/edge/#' -v` |
| Buffer not growing | `BUFFER_SQLITE_PATH` writable, `gateway.buffering.store.init_buffer()` |
| Sync idle | `CASTUO_API_URL` and `CASTUO_API_KEY` set |
| ESP32 silent | Serial monitor, Wi‑Fi creds in `hardware/esp32/` template |

<!-- CASTUO:README-SCOPE:START -->
## CASTÚO-SYSTEM documentation scope

This document is a component-level README. Its statements describe documentation, design, prototype status or bounded implementation context only; they do not independently establish production operation, certification, legal compliance, customer traction, revenue, continuous operation, autonomous authority or federation.

The component remains governed by the CASTÚO-SYSTEM evidence boundary: `DOCUMENTED → IMPLEMENTED → TESTED → VALIDATED → OPERATIONAL → REPEATABLE → FEDERATED`. A capability label is a definition unless a linked, reproducible artifact and attributable review establish the corresponding state.

Canonical context: [Castuo-system](https://github.com/Traky12/Castuo-system), [castuo-evolution control plane](https://github.com/Traky12/castuo-evolution), and [Traky12 public profile](https://github.com/Traky12/Traky12). Current public ecosystem state: `GREEN-STAGING-CANDIDATE · EVIDENCE-SCOPED · PROMOTION-BLOCKED`.
<!-- CASTUO:README-SCOPE:END -->
