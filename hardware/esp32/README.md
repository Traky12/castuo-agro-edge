# ESP32 telemetry templates

Publish JSON to `castuo/edge/{device_id}/telemetry`:

```json
{"device_id":"esp32-01","readings":{"ph":6.2,"ec":1.8,"temperatura":24.5}}
```

Templates and `.ino` sketches land in v0.1 roadmap. Align pin maps with `hardware/wiring/`.

<!-- CASTUO:README-SCOPE:START -->
## CASTÚO-SYSTEM documentation scope

This document is a component-level README. Its statements describe documentation, design, prototype status or bounded implementation context only; they do not independently establish production operation, certification, legal compliance, customer traction, revenue, continuous operation, autonomous authority or federation.

The component remains governed by the CASTÚO-SYSTEM evidence boundary: `DOCUMENTED → IMPLEMENTED → TESTED → VALIDATED → OPERATIONAL → REPEATABLE → FEDERATED`. A capability label is a definition unless a linked, reproducible artifact and attributable review establish the corresponding state.

Canonical context: [Castuo-system](https://github.com/Traky12/Castuo-system), [castuo-evolution control plane](https://github.com/Traky12/castuo-evolution), and [Traky12 public profile](https://github.com/Traky12/Traky12). Current public ecosystem state: `GREEN-STAGING-CANDIDATE · EVIDENCE-SCOPED · PROMOTION-BLOCKED`.
<!-- CASTUO:README-SCOPE:END -->
