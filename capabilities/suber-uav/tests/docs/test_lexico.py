"""El léxico controlado se comprueba, no se recuerda.

Una norma de redacción en un documento la respeta quien la ha leído. Estas pruebas la
convierten en una propiedad del repositorio. Ver ADR-029 y `docs/POSICIONAMIENTO_SUBER.md`,
apartado 3.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
GUION = RAIZ / "scripts" / "check_lexico.py"


def _cargar():
    spec = importlib.util.spec_from_file_location("check_lexico", GUION)
    modulo = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(modulo)
    return modulo


lexico = _cargar()


def test_el_repositorio_esta_limpio():
    hallazgos = []
    for ruta in lexico.archivos(RAIZ):
        hallazgos.extend(lexico.revisar(ruta, RAIZ))
    assert hallazgos == [], "\n".join(
        f"{h['archivo']}:{h['linea']} [{h['codigo']}] {h['texto']}" for h in hallazgos
    )


@pytest.mark.parametrize(
    "codigo, frase",
    [
        ("LEX-01", "El dron detecta enfermedades en el arbolado."),
        ("LEX-02", "El sistema determina automáticamente la calidad del producto."),
        ("LEX-03", "El modelo clasifica el corcho por categorías."),
        ("LEX-04", "La herramienta sustituye la cala tradicional."),
        ("LEX-05", "Funciona sin intervención humana."),
        ("LEX-06", "Alcanza una precisión del 92 en campo."),
        ("LEX-07", "Ofrece un 95 % de acierto."),
        ("LEX-08", "Sistema validado por CICYTEX."),
        ("LEX-09", "La plataforma garantiza la soberanía del dato."),
        ("LEX-10", "El sistema cumple el RGPD en todas sus capas."),
        ("LEX-11", "Procedimiento certificado por un organismo notificado."),
        ("LEX-12", "SUBER UAV es un módulo de CASTÚO-SYSTEM."),
        ("LEX-13", "El registro es un activo de auditoría inexpugnable."),
    ],
)
def test_cada_formulacion_prohibida_se_detecta(tmp_path, codigo, frase):
    doc = tmp_path / "memoria.md"
    doc.write_text(frase + "\n", encoding="utf-8")
    hallazgos = lexico.revisar(doc, tmp_path)
    assert [h["codigo"] for h in hallazgos] == [codigo]


def test_la_formulacion_aprobada_no_se_marca(tmp_path):
    doc = tmp_path / "memoria.md"
    doc.write_text(
        "El sistema identifica indicadores de riesgo sanitario y estima variables de "
        "interés productivo mediante datos UAV y observaciones de campo, con revisión "
        "técnica y trazabilidad de la evidencia.\n",
        encoding="utf-8",
    )
    assert lexico.revisar(doc, tmp_path) == []


def test_el_bloque_eximido_permite_citar_lo_prohibido(tmp_path):
    doc = tmp_path / "memoria.md"
    doc.write_text(
        f"{lexico.OFF}\n> El dron detecta enfermedades.\n{lexico.ON}\n",
        encoding="utf-8",
    )
    assert lexico.revisar(doc, tmp_path) == []


def test_un_bloque_eximido_sin_cerrar_es_un_hallazgo(tmp_path):
    doc = tmp_path / "memoria.md"
    doc.write_text(f"{lexico.OFF}\ntexto cualquiera\n", encoding="utf-8")
    hallazgos = lexico.revisar(doc, tmp_path)
    assert [h["codigo"] for h in hallazgos] == ["LEX-00"]


def test_la_exencion_no_se_arrastra_entre_archivos(tmp_path):
    (tmp_path / "a.md").write_text(f"{lexico.OFF}\ndetecta enfermedades\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("El dron detecta enfermedades.\n", encoding="utf-8")
    hallazgos = [h for r in lexico.archivos(tmp_path) for h in lexico.revisar(r, tmp_path)]
    codigos = {(h["archivo"], h["codigo"]) for h in hallazgos}
    assert ("b.md", "LEX-01") in codigos

def test_la_soberania_desglosada_no_se_marca(tmp_path):
    """S-1…S-6 con su estado individual es la forma admitida de hablar de soberanía."""
    doc = tmp_path / "soberania.md"
    doc.write_text(
        "De las seis propiedades, tres son hechos probados, dos son decisiones de diseño sin "
        "auditar y una está a medias. La residencia europea está elegida, no auditada.\n",
        encoding="utf-8",
    )
    assert lexico.revisar(doc, tmp_path) == []


def test_el_sello_por_autoridad_de_tiempo_no_es_una_certificacion(tmp_path):
    """LEX-11 persigue certificaciones inexistentes, no el vocabulario del sello RFC 3161."""
    doc = tmp_path / "sello.md"
    doc.write_text(
        "El token lo emite una autoridad de tiempo; el sello certificado por una autoridad "
        "RFC 3161 se ancla aparte.\n",
        encoding="utf-8",
    )
    assert lexico.revisar(doc, tmp_path) == []


def test_todos_los_patrones_tienen_prueba():
    """Un patrón sin prueba es un patrón del que nadie sabe si funciona."""
    fuente = pathlib.Path(__file__).read_text(encoding="utf-8")
    ejercitados = set(re.findall(r'\("(LEX-\d+)",\s*"', fuente))
    declarados = {codigo for codigo, _, _ in lexico.PROHIBIDAS}
    assert declarados <= ejercitados, sorted(declarados - ejercitados)


def test_la_formulacion_sobria_de_integridad_no_se_marca(tmp_path):
    """LEX-13 persigue la retórica absoluta, no el vocabulario técnico correcto."""
    doc = tmp_path / "protocolo.md"
    doc.write_text(
        "El modelo append-only ofrece resistencia a la alteración silenciosa y produce "
        "evidencia verificable por un tercero; no ofrece una garantía frente a un "
        "administrador con acceso al motor.\n",
        encoding="utf-8",
    )
    assert lexico.revisar(doc, tmp_path) == []
