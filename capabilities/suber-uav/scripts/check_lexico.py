#!/usr/bin/env python3
"""Comprueba que ningún documento publicable contiene una formulación prohibida.

El léxico controlado vive en `docs/POSICIONAMIENTO_SUBER.md`, apartado 3. Una norma de
redacción escrita en un documento la respeta quien la ha leído y se acuerda; esta prueba la
respeta cualquiera que ejecute la batería. Ver ADR-029.

Uso:
    python3 scripts/check_lexico.py [raíz]      -> código 0 si limpio, 1 si hay hallazgos
    python3 scripts/check_lexico.py --json

Para citar una formulación prohibida —hay que citarla para prohibirla— se envuelve el bloque
entre marcadores de comentario Markdown, que no se renderizan:

    <!-- lexico:off -->
    ...texto que cita la formulación...
    <!-- lexico:on -->

El marcador es deliberadamente incómodo de escribir: exime la cita, no la costumbre.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

OFF = "<!-- lexico:off -->"
ON = "<!-- lexico:on -->"

#: (identificador, patrón, por qué está prohibido)
PROHIBIDAS: list[tuple[str, str, str]] = [
    ("LEX-01", r"detecta\w*\s+(?:las\s+)?enfermedades",
     "un sensor aéreo no diagnostica: registra reflectancia, de la que se derivan indicadores"),
    ("LEX-02", r"determina\w*\s+(?:autom[áa]ticamente\s+)?(?:la\s+)?calidad",
     "la clase de calidad la asigna el técnico por metodología de campo y laboratorio"),
    ("LEX-03", r"clasifica\w*\s+(?:el\s+)?corcho",
     "el sistema registra la clase asignada; no la produce"),
    ("LEX-04", r"sustitu\w*\s+(?:a\s+)?la\s+cala",
     "el sistema complementa y digitaliza la cala; no la sustituye"),
    ("LEX-05", r"sin\s+intervenci[óo]n\s+humana",
     "toda salida del modelo pasa por revisión técnica"),
    ("LEX-06", r"precisi[óo]n\s+del\s+\d",
     "no hay ninguna medida de precisión; procede [POR MEDIR]"),
    ("LEX-07", r"\d+\s*%\s+de\s+(?:precisi[óo]n|acierto|exactitud|ahorro)",
     "ninguna cifra de desempeño está medida"),
    ("LEX-08", r"(?:validado|respaldado|avalado)\s+por\s+(?:CICYTEX|PTEcor|FUNDECYT|Hidrocork|ASECOR)",
     "no existe acuerdo ni respaldo de ninguna organización"),
    ("LEX-09", r"(?:garantiza\w*\s+la\s+soberan|soberan[íi]a\s+\w*\s*garantizada)",
     "la soberanía del dato es hoy decisión de diseño, no propiedad auditada"),
    ("LEX-10", r"(?:cumple|conforme|conformidad)\s+(?:con\s+)?(?:el\s+)?(?:RGPD|GDPR)",
     "no hay revisión jurídica cerrada; owner_ref y titularidad siguen abiertos"),
    ("LEX-11", r"(?:certificad|homologad|acreditad)\w*\s+por\s+(?!una\s+autoridad)",
     "ninguna parte del sistema está certificada ni homologada por nadie"),
    ("LEX-12", r"m[óo]dulo\s+(?:de|del)\s+CAST[ÚU]O-SYSTEM",
     "SUBER UAV es fase externa a la arquitectura, no un módulo de los 36 (ADR-031)"),
    ("LEX-13", r"(?:inexpugnable|infalible|invulnerable|blindaje\s+total|garant[íi]a\s+total|"
               r"absolutamente\s+seguro|imposible\s+de\s+alterar|escudo\s+legal|"
               r"prueba\s+matem[áa]tica\s+de\s+integridad)",
     "retórica absoluta: se dice 'evidencia verificable' o 'resistencia a alteración silenciosa'"),
]

EXTENSIONES = {".md", ".html", ".txt"}
EXCLUIDOS = {"LICENSE"}
DIRS_IGNORADOS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache"}

COMPILADAS = [(cod, re.compile(pat, re.IGNORECASE), motivo) for cod, pat, motivo in PROHIBIDAS]


def archivos(raiz: pathlib.Path) -> list[pathlib.Path]:
    salida = []
    for ruta in sorted(raiz.rglob("*")):
        if not ruta.is_file() or ruta.suffix.lower() not in EXTENSIONES:
            continue
        if ruta.name in EXCLUIDOS:
            continue
        if DIRS_IGNORADOS & set(ruta.relative_to(raiz).parts):
            continue
        salida.append(ruta)
    return salida


def revisar(ruta: pathlib.Path, raiz: pathlib.Path) -> list[dict]:
    hallazgos: list[dict] = []
    eximido = False
    for numero, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), start=1):
        marca = linea.strip()
        if marca == OFF:
            eximido = True
            continue
        if marca == ON:
            eximido = False
            continue
        if eximido:
            continue
        for codigo, patron, motivo in COMPILADAS:
            encontrado = patron.search(linea)
            if encontrado:
                hallazgos.append({
                    "archivo": str(ruta.relative_to(raiz)),
                    "linea": numero,
                    "codigo": codigo,
                    "texto": encontrado.group(0).strip(),
                    "motivo": motivo,
                })
    if eximido:
        hallazgos.append({
            "archivo": str(ruta.relative_to(raiz)),
            "linea": 0,
            "codigo": "LEX-00",
            "texto": OFF,
            "motivo": "bloque eximido sin cerrar: falta el marcador lexico:on",
        })
    return hallazgos


def main(argv: list[str]) -> int:
    como_json = "--json" in argv
    posicionales = [a for a in argv if not a.startswith("--")]
    raiz = pathlib.Path(posicionales[0]) if posicionales else pathlib.Path(__file__).resolve().parents[1]
    raiz = raiz.resolve()

    hallazgos: list[dict] = []
    revisados = archivos(raiz)
    for ruta in revisados:
        hallazgos.extend(revisar(ruta, raiz))

    if como_json:
        print(json.dumps({"raiz": str(raiz), "archivos": len(revisados),
                          "hallazgos": hallazgos}, ensure_ascii=False, indent=2))
    else:
        print(f"Léxico controlado — {len(revisados)} archivos revisados bajo {raiz}")
        if not hallazgos:
            print("Sin formulaciones prohibidas.")
        for h in hallazgos:
            print(f"  {h['archivo']}:{h['linea']}  [{h['codigo']}]  «{h['texto']}»")
            print(f"      {h['motivo']}")
        if hallazgos:
            print(f"\n{len(hallazgos)} hallazgo(s). Ver docs/POSICIONAMIENTO_SUBER.md, apartado 3.")
    return 1 if hallazgos else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
