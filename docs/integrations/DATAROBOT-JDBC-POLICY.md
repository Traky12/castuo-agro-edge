# Política de uso — DataRobot JDBC

**Estado:** Propuesta · **Fecha:** 2026-11-18 · **Ámbito:** este repositorio
**Decisión canónica:** ADR-006 en `Traky12/Castuo-system` (`docs/adr/ADR-006-datarobot-jdbc-gated-read-only.md`)

Este repositorio **no** contiene ni ejecuta el conector DataRobot JDBC. La única implementación autorizada
vive en `Castuo-system` (`apps/api/integrations/datarobot_jdbc.py`), desactivada por defecto.
Este documento fija las reglas para que ningún componente de este repositorio lo use de otra forma.

## Por qué hay restricciones

DataRobot abre la conexión JDBC desde su propia red y procesa las filas en su plataforma. Usarlo sin
control supondría exponer bases de datos a internet y transferir datos fuera de la infraestructura UE,
en contra de los principios de CASTÚO-SYSTEM: Zero Trust, residencia de datos en la UE (Hetzner +
Mistral AI EU), mínimo privilegio y "Evidence First".

## Reglas

| # | Regla |
|---|---|
| 1 | No añadir aquí clientes, scripts ni workflows que llamen a DataRobot. Cualquier consulta pasa por el adaptador de `Castuo-system`. |
| 2 | Solo lectura. La ruta de escritura de DataRobot (DML/DDL) está prohibida en todo el ecosistema. |
| 3 | Solo endpoints de región UE por HTTPS. |
| 4 | Nunca contra la PostgreSQL de producción: únicamente una réplica de analítica sin datos personales, con lista blanca de host. |
| 5 | Credenciales solo en variables de entorno o secretos; nunca en el código, en la URL JDBC ni en commits. |
| 6 | Ningún resultado se presenta como métrica validada sin evidencia registrada (Evidence First). |

## Estado

`Listo para integrar` en `Castuo-system`, **no operativo**. Quedan pendientes: caso de uso, EIPD/DPIA,
contrato de encargo de tratamiento (Art. 28 RGPD) y primera consulta con evidencia. Hasta entonces no se
puede declarar este conector como *Operativo* ni *Verificado* en ningún documento de este repositorio.
