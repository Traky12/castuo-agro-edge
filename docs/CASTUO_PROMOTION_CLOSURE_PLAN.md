# CASTÚO Sovereign Resilience — Plan de cierre de promoción

**Estado de partida:** `PROMOTION = BLOCKED` · `LOCAL_READOUT / NO_CLAIM`  
**Objetivo:** cerrar el primer vertical slice verificable y convertir el bloqueo en un claim delimitado, reproducible y revisable.

## 1. Decisión de alcance

Se congela la expansión horizontal de módulos y se prioriza **S-001A: conectividad perdida → decisión de policy → operación degradada/offline → evento de evidencia → recuperación → replay → verificación externa**. El alcance se limita a una capability, un contrato, un conjunto de dependencias y un claim boundary. Todo resultado local mantiene `VALIDATED_LOCAL` o `LOCAL_RESULT_NO_CLAIM` hasta que exista revisión independiente.

## 2. Gaps específicos

| ID | Gap | Estado | Evidencia necesaria | Gate que bloquea |
|---|---|---|---|---|
| G-01 | No existe un contrato ejecutable completo para S-001A. | `EVIDENCE_REQUIRED` | Scenario YAML versionado con fault, expected/observed, recovery, replay y review. | Capability / resilience |
| G-02 | No hay Capability, Sovereignty, Evidence y Trust Passports completos. | `PARTIAL` | Passports con owner, scope, dependencia, autoridad y claim boundary. | Capability / sovereignty |
| G-03 | El inventario D0–D5 y el grafo de dependencias no están cerrados. | `BLOCKED` | Matriz con identity, keys, storage, time, AI, build, observability y exit path. | Sovereignty |
| G-04 | La continuidad offline está descrita, pero no demostrada. | `EVIDENCE_REQUIRED` | Fault injection de conectividad, identidad degradada, policy cache, buffer, dedupe, conflicto y rollback. | Resilience |
| G-05 | No existe evidence envelope portable verificable fuera de CASTÚO. | `EVIDENCE_REQUIRED` | semantic record, binary vector, manifest, hashes, firma, replay-result y gate-result. | Evidence / replay |
| G-06 | No se ha demostrado `decode(evidence.bin) == canonical(semantic.json)`. | `BLOCKED` | Test de canonicalización y caso negativo `SCHEMA_MISMATCH`. | Evidence |
| G-07 | Falta un foreign verifier autónomo. | `BLOCKED` | Verificador sin dashboard, DB, cloud, proveedor o modelo original. | Independent review |
| G-08 | La salida de proveedores no se ha ejercitado. | `EVIDENCE_REQUIRED` | Export → proveedor B → import → hash verify → replay → continued operation. | Sovereignty / exit |
| G-09 | La frontera de autoridad de IA no está probada adversarialmente. | `EVIDENCE_REQUIRED` | Agent passport, negative tests, approval, kill switch, budget, time limit y audit. | Security / AI exit |
| G-10 | Rollback, conflicto y recuperación no tienen invariantes observadas. | `PARTIAL` | Runbook, restore test, lineage y pérdida medida de datos/evidencia. | Recovery / rollback |
| G-11 | No hay revisión humana firmada y scope-bound. | `PENDING` | Review record con owner, fecha, alcance, limitaciones y decisión. | Review |
| G-12 | Las métricas internas pueden confundirse con claims comerciales. | `PENDING` | Etiquetado explícito OII/Evidence Yield como readout no comercial. | Claim governance |

## 3. Riesgos P0

| Riesgo | Consecuencia | Señal de activación | Mitigación inmediata |
|---|---|---|---|
| **P0-R1: claim sin evidencia independiente** | Falsa confianza sobre resiliencia, soberanía o portabilidad. | README, dashboard o presentación usa `verified`, `production`, `independent` o `vendor-independent` sin envelope/replay/review. | Política fail-closed; mantener `NO_CLAIM`; escaneo de claims antes de merge. |
| **P0-R2: dependencia D4/D5 sin salida y recuperación probadas** | Bloqueo operacional o pérdida de autoridad/evidencia ante caída de proveedor. | Dependencia crítica sin owner, jurisdicción, export, reemplazo, tiempo de salida o último test. | Congelar promoción; completar matriz D0–D5 y ejecutar vendor-exit drill. |
| **P0-R3: evidencia no verificable fuera del proveedor** | No se puede auditar, migrar ni defender el estado ante un tercero. | Falta foreign verifier, firma, hashes, scope temporal o replay determinista. | Emitir envelope portable y ejecutar verificación en entorno externo. |
| **P0-R4: autoridad de IA fuera de límites** | Acción irreversible, ampliación de privilegios o bypass de aprobación. | Agente sin owner, scope, acciones prohibidas, kill switch o negative tests. | `SECURITY_HOLD`; deshabilitar acciones irreversibles y probar `DETECT → ... → EVIDENCE`. |

## 4. Secuencia priorizada de cierre

| Fase | Trabajo | Owner recomendado | Artefacto de salida | Criterio binario |
|---|---|---|---|---|
| 0 | Congelar claims y alcance | Governance / product owner | Claim boundary + baseline | No hay claim no soportado. |
| 1 | Formalizar S-001A y passports | Architecture + assurance | Scenario + 4 passports | Contratos válidos y owners asignados. |
| 2 | Inventariar dependencias | Platform + security | Dependency exit matrix | Todas las D4/D5 tienen exit/recovery/evidence. |
| 3 | Implementar y ejecutar offline slice | Field + core engineering | Test logs + observed behavior | Invariantes offline y rollback pasan. |
| 4 | Generar evidence envelope | Assurance engineering | Portable evidence pack | Hash, firma, scope y canonical decode pasan. |
| 5 | Ejecutar replay externo | Independent reviewer | Foreign verifier result | Replay y semántica equivalente. |
| 6 | Probar vendor exit | Platform + operations | Exit drill report | Provider B continúa la operación dentro del scope. |
| 7 | Revisar y decidir | Human reviewer | Signed gate record | Todos los predicados obligatorios son `1V` o `1R`. |

## 5. Kernel de promoción

```text
PROMOTE = capability ∧ evidence ∧ replay ∧ security ∧ sovereignty ∧ resilience ∧ review ∧ rollback
```

Cualquier `0`, `?`, `BLOCKED`, `EVIDENCE_REQUIRED` o `SECURITY_HOLD` mantiene `PROMOTION = 0`. El primer objetivo no es una puntuación media, sino cerrar el conjunto mínimo obligatorio y emitir una decisión `PROMOTE`, `BLOCK`, `REVIEW` o `ROLLBACK`.

## 6. Primer paquete de evidencia

El paquete mínimo debe contener `semantic.json`, `evidence.yaml`, `evidence.bin`, `manifest.json`, `hashes.txt`, `signature`, `replay-result` y `gate-result`. Debe registrar commit, entorno, runtime, comandos, timestamps, scope, hashes de entrada/salida/evidencia, limitaciones y claim boundary. Un foreign verifier debe comprobar schema, hash, firma, timeline, policy y replay sin confiar en el dashboard o proveedor original.

## 7. Claims después del cierre

El claim permitido debe estar delimitado por capability, versión, escenario, entorno y fecha; por ejemplo: **“S-001A fue reproducido de forma independiente para la operación offline definida, con continuidad, preservación de evidencia y recuperación verificadas dentro del scope declarado.”** No autoriza claims universales de producción, superioridad, certificación o independencia abstracta.

## 8. Checklist de salida

| Control | Estado de partida |
|---|---:|
| Capability contract | `EVIDENCE_REQUIRED` |
| Evidence envelope | `EVIDENCE_REQUIRED` |
| Replay | `EVIDENCE_REQUIRED` |
| Security / AI authority | `SECURITY_HOLD` si falta negative test |
| Sovereignty / vendor exit | `BLOCKED` |
| Resilience / recovery | `EVIDENCE_REQUIRED` |
| Human review | `PENDING` |
| Rollback | `EVIDENCE_REQUIRED` |
| **PROMOTION** | **`BLOCK`** |

**Regla de gobierno:** hasta que el checklist cierre, publicar sólo estados `LOCAL_RESULT_NO_CLAIM`, `EVIDENCE_REQUIRED`, `BLOCKED` o `HUMAN_REVIEW_PENDING`.
