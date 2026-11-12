# Gobernanza

## Método y reglas de trabajo (resumen)

> Estado: **PROPUESTA v1.0** (2026-11-09). Fuente canónica: [Traky12/Castuo-system/docs/governance/METODO-Y-REGLAS.md](https://github.com/Traky12/Castuo-system/blob/main/docs/governance/METODO-Y-REGLAS.md) (repositorio privado; acceso del owner). Este resumen puede **añadir** reglas propias, nunca relajar las canónicas.
> Taxonomía de este repo: `field/edge`.

- **Evidence-first:** toda afirmación importante se enlaza a un test, hash, log, SEV o gate; distinguir *verificado / inferido / propuesto*.
- **Human-in-the-loop:** ningún modelo de IA decide un gate, fusiona un PR ni publica por su cuenta.
- **GO bloqueado** mientras falten dato real de extremo a extremo y CI operativo. *CI en verde ≠ Operativo.*
- **Madurez N0–N6 sin saltos.** N0 = sin implementación, sin acuerdo firmado y sin artefacto verificable. Lo `PLANNED` no se presenta como existente.
- **PR mínimos y separados;** sin fusión en bloque, sin `--admin`, sin saltar la protección de rama. Sin CI disponible → borrador.
- **Seguridad:** ni credenciales ni tokens en el repo (un valor que estuvo en git se rota); *fail-closed* por defecto; TLS nunca desactivado por defecto.
- **Terceros:** nada se envía ni publica sin revisión humana; lo no respaldado se marca **[CONFIRMAR]**.
- **Hashes de evidencia sobre LF:** en Windows usar `core.autocrlf=false` al validar.
- **Este repo:** Repo de campo/edge: capacidades EDGE-001/EDGE-002 (registro en Castuo-system). No afirmar sincronización firmada ni Ed25519 hasta que FIELD-001 tenga un SEV verificable en `Castuo-system`.
