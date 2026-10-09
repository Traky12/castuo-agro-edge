# Security Policy

## Scope

`castuo-agro-edge` is an edge/IoT gateway (FastAPI, MQTT client, local
buffering, upstream sync) plus ESP32 firmware and deployment files. It
publishes no versioned releases. This policy covers the code, firmware and
workflows in this repository.

## Supported versions

| Version | Supported |
|---|---|
| `main` branch (latest commit) | :white_check_mark: |
| Any other branch or fork | :x: |

## Reporting a vulnerability

Do **not** open a public issue.

Report privately through GitHub: **Security → Report a vulnerability** on
this repository.

Relevant findings include authentication or authorisation flaws in the
gateway API, MQTT handling that accepts untrusted input unsafely, secrets in
the repository or its history, or firmware issues.

This is a single-maintainer project; the times below are targets, not
contractual SLAs:

- Acknowledgement: within 7 days.
- Initial assessment (accepted / declined, with reasoning): within 30 days.

## Secrets

Real credentials never belong in this repository. The example files
(`.env.example`, `gateway/mqtt/.env.example`,
`firmware/credentials.h.example`) are templates: secret fields must stay
empty or use obvious placeholders.

## Contributions and license

External contributions are not accepted until a contributor licence agreement
(CLA) or contribution policy is defined. No license is currently granted
(license pending IP review).
