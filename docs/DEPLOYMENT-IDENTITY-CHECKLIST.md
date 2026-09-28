# Deployment identity checklist (before merging the demo-defaults change)

Since this change, the code defaults for gateway identity are demo values:
`MQTT_CLIENT_ID=demo-client-001`, `DEVICE_ID=demo-device-001`,
`SITE_ID=demo-site-001`. A deployment that relied on the old defaults instead
of setting these variables would start reporting demo identities.

## Policy

| Environment | `MQTT_CLIENT_ID` / `DEVICE_ID` / `SITE_ID` |
|---|---|
| Development | Demo defaults allowed |
| Staging | Explicit values recommended |
| Production | **Mandatory.** With `CASTUO_ENV=production`, the gateway refuses to start if any of them is `demo-*` |

The guard is `ensure_real_identity()` (`gateway/mqtt/config.py`, called at
the start of `gateway/mqtt/main.py:main()`) and a validator on
`EdgeSettings` (`gateway/config.py`). Covered by
`tests/unit/test_production_identity_guard.py`.

## Where each deployment reads its identity

| Deployment path | Reads identity from | Affected by this change? |
|---|---|---|
| systemd `deployment/systemd/castuo-edge.service` | `EnvironmentFile=/opt/castuo-agro-edge/.env` | Yes, if that file does not set the variables |
| systemd `gateway/mqtt/castuo-mqtt-gateway.service` | `EnvironmentFile=/opt/castuo-edge/.env` | Yes, if that file does not set the variables |
| `docker-compose.yml` | `env_file` / `environment:` | Yes, if not set there |
| Raspberry Pi bootstrap script in the private `Castuo-system` repo | Its own embedded gateway (does not use this repository's code) | **No** |

## Owner confirmation (fill in before merge)

| Environment / gateway | `MQTT_CLIENT_ID` set | `DEVICE_ID` set | `SITE_ID` set | `CASTUO_ENV` | Confirmed by / date |
|---|---|---|---|---|---|
| Development (local) | demo allowed | demo allowed | demo allowed | unset | — |
| Staging | ☐ | ☐ | ☐ | ☐ `staging` | |
| Each physical gateway (list) | ☐ | ☐ | ☐ | ☐ `production` | |
| Docker Compose deployments | ☐ | ☐ | ☐ | ☐ | |
| systemd deployments | ☐ | ☐ | ☐ | ☐ | |

If no gateway running this code exists yet, record "none deployed" with the
date. As of 2026-09-28 no real field data has been produced.
