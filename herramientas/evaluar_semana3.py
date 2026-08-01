#!/usr/bin/env python3
"""
Evalúa el estado del proyecto contra los criterios de aceptación de la Semana 3.

Produce un informe en Markdown con un diagrama Mermaid coloreado según el
resultado de cada verificación, pensado para responder la pregunta de la semana
sin leer el código:

    ¿Qué evidencia tenemos de que este cambio hizo lo que tenía que hacer?

Uso:
    python herramientas/evaluar_semana3.py
    python herramientas/evaluar_semana3.py --base HEAD~1     # además, alcance del cambio
    python herramientas/evaluar_semana3.py --salida informe.md

Este archivo es instrumento de medición: no debe ser modificado por el agente
(ver CA-000 en docs/contrato/criterios_de_aceptacion.md).
"""

from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
APP = RAIZ / "app"

OK, FALLA, NA = "ok", "falla", "na"

SIMBOLO = {OK: "✅", FALLA: "❌", NA: "➖"}


@dataclass
class Resultado:
    id: str
    nivel: str
    titulo: str
    estado: str
    detalle: str = ""


RESULTADOS: list[Resultado] = []


def registrar(id_: str, nivel: str, titulo: str, estado: str, detalle: str = ""):
    RESULTADOS.append(Resultado(id_, nivel, titulo, estado, detalle))


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------


def correr(cmd: list[str], cwd: Path = RAIZ, env_extra: dict | None = None):
    entorno = dict(os.environ)
    if env_extra:
        entorno.update(env_extra)
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, env=entorno, timeout=600
    )


def _base_sqlite_temporal() -> dict:
    ruta = Path(tempfile.gettempdir()) / "evaluacion_semana3.db"
    if ruta.exists():
        ruta.unlink()
    return {"DATABASE_URL": f"sqlite:///{ruta}"}


def imports_de(archivo: Path) -> list[str]:
    """Módulos importados por un archivo, sin ejecutarlo."""
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    modulos: list[str] = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.append(nodo.module)
        elif isinstance(nodo, ast.Import):
            modulos.extend(alias.name for alias in nodo.names)
    return modulos


def coincide(modulo: str, prefijo: str) -> bool:
    return modulo == prefijo or modulo.startswith(prefijo + ".")


# ---------------------------------------------------------------------------
# NIVEL 1 — contexto
# ---------------------------------------------------------------------------

DOCUMENTOS_ESPERADOS = [
    "AGENTS.md",
    "docs/contrato/alcance.md",
    "docs/contrato/reglas.md",
    "docs/contrato/arquitectura.md",
    "docs/contrato/contrato_api.md",
    "docs/contrato/base_de_datos.md",
    "docs/contrato/criterios_de_aceptacion.md",
    "docs/contrato/trazabilidad.md",
    "docs/adr/ADR-003.md",
]


def verificar_contexto():
    faltan = [d for d in DOCUMENTOS_ESPERADOS if not (RAIZ / d).exists()]
    registrar(
        "CTX",
        "Contexto",
        "Documentos del contexto presentes",
        OK if not faltan else FALLA,
        "todos presentes" if not faltan else "faltan: " + ", ".join(faltan),
    )


# ---------------------------------------------------------------------------
# NIVEL 2 — verificaciones automáticas
# ---------------------------------------------------------------------------


def verificar_suite():
    r = correr([sys.executable, "-m", "pytest", "-q"], env_extra=_base_sqlite_temporal())
    ultima = [l for l in r.stdout.strip().splitlines() if l.strip()]
    registrar(
        "CA-004",
        "Verificaciones",
        "Suite completa en verde",
        OK if r.returncode == 0 else FALLA,
        ultima[-1] if ultima else "sin salida",
    )


def verificar_arbitro():
    archivo = RAIZ / "tests" / "test_garantia_ret001.py"
    if not archivo.exists():
        registrar(
            "CA-001",
            "Verificaciones",
            "Árbitro: garantía de RET-001",
            FALLA,
            "falta tests/test_garantia_ret001.py",
        )
        return
    r = correr(
        [sys.executable, "-m", "pytest", str(archivo), "-q"],
        env_extra=_base_sqlite_temporal(),
    )
    ultima = [l for l in r.stdout.strip().splitlines() if l.strip()]
    registrar(
        "CA-001",
        "Verificaciones",
        "Árbitro: garantía de RET-001",
        OK if r.returncode == 0 else FALLA,
        ultima[-1] if ultima else "sin salida",
    )


def verificar_arquitectura():
    archivo = RAIZ / "tests" / "test_arquitectura.py"
    if not archivo.exists():
        registrar("CA-009", "Verificaciones", "Restricciones ARQ vigentes", FALLA,
                  "falta tests/test_arquitectura.py")
        return
    r = correr(
        [sys.executable, "-m", "pytest", str(archivo), "-q"],
        env_extra=_base_sqlite_temporal(),
    )
    ultima = [l for l in r.stdout.strip().splitlines() if l.strip()]
    registrar(
        "CA-009",
        "Verificaciones",
        "Restricciones ARQ vigentes",
        OK if r.returncode == 0 else FALLA,
        ultima[-1] if ultima else "sin salida",
    )


PROHIBIDOS_ARQ008 = (
    "sqlalchemy",
    "psycopg",
    "psycopg2",
    "sqlite3",
    "app.infrastructure.models",
)


def verificar_arq_008():
    """ARQ-008 medido de forma independiente de las pruebas del proyecto."""
    violaciones: dict[str, list[str]] = {}
    for capa in ("application", "api"):
        for archivo in sorted((APP / capa).rglob("*.py")):
            encontrados = [
                m
                for m in imports_de(archivo)
                if any(coincide(m, p) for p in PROHIBIDOS_ARQ008)
            ]
            if encontrados:
                violaciones[archivo.relative_to(RAIZ).as_posix()] = encontrados

    registrar(
        "CA-010",
        "Verificaciones",
        "ARQ-008: la persistencia no se filtra",
        OK if not violaciones else FALLA,
        "sin violaciones"
        if not violaciones
        else "; ".join(f"{k} → {', '.join(v)}" for k, v in violaciones.items()),
    )


def verificar_diagrama():
    generador = RAIZ / "herramientas" / "generar_diagrama_estados.py"
    if not generador.exists():
        registrar("CA-013", "Verificaciones", "Documento derivado sincronizado", NA,
                  "no hay generador")
        return
    r = correr([sys.executable, str(generador), "--verificar"])
    registrar(
        "CA-013",
        "Verificaciones",
        "Documento derivado sincronizado",
        OK if r.returncode == 0 else FALLA,
        r.stdout.strip().splitlines()[0] if r.stdout.strip() else "sin salida",
    )


# ---------------------------------------------------------------------------
# NIVEL 3 — garantías del sistema
# ---------------------------------------------------------------------------


CODIGO_INSPECCION_ESQUEMA = r"""
import json, sys
from app.infrastructure.db import Base
import app.infrastructure.models  # noqa: F401

tabla = Base.metadata.tables.get("holds")
salida = {"tabla": tabla is not None, "unicos": []}
if tabla is not None:
    for idx in tabla.indexes:
        if idx.unique:
            salida["unicos"].append({
                "nombre": idx.name,
                "columnas": [c.name for c in idx.columns],
                "parcial": bool(idx.dialect_options.get("sqlite", {}).get("where") is not None
                                or idx.dialect_options.get("postgresql", {}).get("where") is not None),
            })
    for c in tabla.constraints:
        if type(c).__name__ == "UniqueConstraint":
            salida["unicos"].append({
                "nombre": c.name,
                "columnas": [col.name for col in c.columns],
                "parcial": False,
            })
print(json.dumps(salida))
"""


def verificar_restriccion_en_esquema():
    import json

    r = correr(
        [sys.executable, "-c", CODIGO_INSPECCION_ESQUEMA],
        env_extra=_base_sqlite_temporal(),
    )
    if r.returncode != 0:
        registrar("CA-005", "Garantías", "Restricción de unicidad en el esquema", FALLA,
                  (r.stderr.strip().splitlines() or ["error al inspeccionar"])[-1])
        return

    try:
        datos = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        registrar("CA-005", "Garantías", "Restricción de unicidad en el esquema", FALLA,
                  "no se pudo leer el esquema")
        return

    candidatos = [
        u
        for u in datos["unicos"]
        if {"event_id", "seat_id"} <= set(u["columnas"])
    ]
    if not candidatos:
        registrar("CA-005", "Garantías", "Restricción de unicidad en el esquema", FALLA,
                  "no hay restricción única sobre (event_id, seat_id) en holds")
        return

    parcial = any(c["parcial"] for c in candidatos)
    nombres = ", ".join(c["nombre"] or "(sin nombre)" for c in candidatos)
    registrar(
        "CA-005",
        "Garantías",
        "Restricción de unicidad en el esquema",
        OK,
        f"{nombres}"
        + (" (parcial por estado)" if parcial else
           " — ATENCIÓN: no es parcial; bloquearía también estados no ocupantes"),
    )


def verificar_create_all():
    main_py = RAIZ / "main.py"
    if not main_py.exists():
        registrar("CA-007", "Garantías", "create_all fuera del arranque", NA, "no hay main.py")
        return
    texto = main_py.read_text(encoding="utf-8")
    presente = "create_all" in texto
    registrar(
        "CA-007",
        "Garantías",
        "create_all fuera del arranque",
        FALLA if presente else OK,
        "main.py todavía llama a create_all" if presente else "no aparece en main.py",
    )


def verificar_alembic():
    ini = RAIZ / "alembic.ini"
    versiones = list(RAIZ.rglob("versions/*.py"))
    if not ini.exists():
        registrar("CA-006", "Garantías", "Migraciones Alembic", FALLA, "falta alembic.ini")
        return
    if not versiones:
        registrar("CA-006", "Garantías", "Migraciones Alembic", FALLA,
                  "alembic.ini presente pero sin migraciones")
        return
    registrar(
        "CA-006",
        "Garantías",
        "Migraciones Alembic",
        OK,
        f"{len(versiones)} migración(es): "
        + ", ".join(v.name for v in sorted(versiones)[:4]),
    )


# ---------------------------------------------------------------------------
# NIVEL 4 — contrato con el consumidor
# ---------------------------------------------------------------------------

RUTAS_CONTRATO = [
    ("get", "/health"),
    ("get", "/events"),
    ("get", "/events/{event_id}"),
    ("get", "/events/{event_id}/seats"),
    ("post", "/events/{event_id}/holds"),
    ("post", "/holds/{hold_id}/confirm"),
    ("delete", "/holds/{hold_id}"),
]

CODIGO_OPENAPI = r"""
import json
from main import app
esquema = app.openapi()
print(json.dumps({"paths": {p: list(m.keys()) for p, m in esquema.get("paths", {}).items()}}))
"""


def verificar_contrato_openapi():
    import json

    r = correr([sys.executable, "-c", CODIGO_OPENAPI], env_extra=_base_sqlite_temporal())
    if r.returncode != 0:
        registrar("CA-011", "Contrato", "Rutas del contrato en OpenAPI", FALLA,
                  (r.stderr.strip().splitlines() or ["no se pudo generar OpenAPI"])[-1])
        return

    try:
        paths = json.loads(r.stdout.strip().splitlines()[-1])["paths"]
    except Exception:
        registrar("CA-011", "Contrato", "Rutas del contrato en OpenAPI", FALLA,
                  "respuesta ilegible")
        return

    # normaliza los nombres de parámetro: {id} y {event_id} son equivalentes
    import re

    def clave(ruta: str) -> str:
        return re.sub(r"\{[^}]+\}", "{}", ruta)

    presentes = {(m.lower(), clave(p)) for p, ms in paths.items() for m in ms}
    faltan = [
        f"{m.upper()} {p}"
        for m, p in RUTAS_CONTRATO
        if (m, clave(p)) not in presentes
    ]

    registrar(
        "CA-011",
        "Contrato",
        "Rutas del contrato en OpenAPI",
        OK if not faltan else FALLA,
        "todas presentes" if not faltan else "faltan: " + ", ".join(faltan),
    )


# ---------------------------------------------------------------------------
# alcance del cambio
# ---------------------------------------------------------------------------

ALCANCE_ESPERADO = (
    "app/",
    "tests/",
    "docs/",
    "alembic/",
    "alembic.ini",
    "main.py",
    "requirements.txt",
    "TODO.md",
    "pytest.ini",
    "migrations/",
)


def verificar_alcance(base: str | None):
    if not base:
        registrar("CA-016", "Alcance", "Alcance del cambio", NA,
                  "no se indicó --base; ejecutar con --base <commit> para medirlo")
        return

    r = correr(["git", "diff", "--numstat", base])
    if r.returncode != 0:
        registrar("CA-016", "Alcance", "Alcance del cambio", NA,
                  "git no pudo comparar contra " + base)
        return

    archivos = []
    for linea in r.stdout.strip().splitlines():
        partes = linea.split("\t")
        if len(partes) == 3:
            archivos.append((partes[2], partes[0], partes[1]))

    inesperados = [
        a for a, _, _ in archivos if not a.startswith(ALCANCE_ESPERADO)
    ]

    detalle = f"{len(archivos)} archivo(s) modificado(s)"
    if inesperados:
        detalle += " — fuera del alcance previsto: " + ", ".join(inesperados)

    registrar(
        "CA-016",
        "Alcance",
        "Alcance del cambio",
        OK if not inesperados else FALLA,
        detalle,
    )


# ---------------------------------------------------------------------------
# informe
# ---------------------------------------------------------------------------

ORDEN_NIVELES = ["Contexto", "Verificaciones", "Garantías", "Contrato", "Alcance"]

DESCRIPCION_NIVEL = {
    "Contexto": "lo que el agente puede leer",
    "Verificaciones": "avisan si algo se rompió",
    "Garantías": "impiden que se rompa",
    "Contrato": "lo que promete al consumidor",
    "Alcance": "cuánto tocó",
}


def _id_nodo(id_: str) -> str:
    """Identificador seguro para Mermaid: solo ASCII, sin espacios ni guiones."""
    import unicodedata

    plano = unicodedata.normalize("NFKD", id_).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() else "_" for c in plano)


def construir_mermaid() -> str:
    lineas = ["flowchart TD"]
    for nivel in ORDEN_NIVELES:
        delnivel = [r for r in RESULTADOS if r.nivel == nivel]
        if not delnivel:
            continue
        lineas.append(f'    subgraph {_id_nodo(nivel)}["{nivel} — {DESCRIPCION_NIVEL[nivel]}"]')
        lineas.append("        direction LR")
        for r in delnivel:
            etiqueta = f"{SIMBOLO[r.estado]} {r.id}<br/>{r.titulo}"
            lineas.append(f'        {_id_nodo(r.id)}["{etiqueta}"]:::{r.estado}')
        lineas.append("    end")

    niveles_presentes = [
        n for n in ORDEN_NIVELES if any(r.nivel == n for r in RESULTADOS)
    ]
    for a, b in zip(niveles_presentes, niveles_presentes[1:]):
        lineas.append(f"    {_id_nodo(a)} --> {_id_nodo(b)}")

    lineas += [
        "    classDef ok fill:#d8f3dc,stroke:#2d6a4f,color:#1b4332;",
        "    classDef falla fill:#ffccd5,stroke:#c9184a,color:#590d22;",
        "    classDef na fill:#e9ecef,stroke:#6c757d,color:#343a40;",
    ]
    return "\n".join(lineas)


def construir_informe() -> str:
    total = len(RESULTADOS)
    ok = sum(1 for r in RESULTADOS if r.estado == OK)
    fallan = sum(1 for r in RESULTADOS if r.estado == FALLA)
    na = total - ok - fallan

    doc = [
        "# Informe de evidencia — Semana 3",
        "",
        f"**{ok} de {total} verificaciones en verde** "
        f"({fallan} en rojo, {na} sin evaluar).",
        "",
        "```mermaid",
        construir_mermaid(),
        "```",
        "",
        "## Detalle",
        "",
        "| | ID | Verificación | Resultado |",
        "|---|---|---|---|",
    ]
    for r in RESULTADOS:
        doc.append(f"| {SIMBOLO[r.estado]} | `{r.id}` | {r.titulo} | {r.detalle} |")

    doc += [
        "",
        "## Qué NO dice este informe",
        "",
        "Este informe reúne evidencia sobre propiedades concretas y verificables.",
        "No dice nada sobre la legibilidad del código, la calidad de los mensajes",
        "de error, el rendimiento, el comportamiento de la migración sobre datos",
        "preexistentes inválidos, ni sobre la existencia de otras condiciones de",
        "carrera en operaciones no cubiertas.",
        "",
        "Un tablero en verde significa que el sistema es correcto **respecto de lo",
        "que estas verificaciones comprueban**. Nada más, y nada menos.",
        "",
    ]
    return "\n".join(doc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Commit contra el cual medir el alcance del cambio.")
    parser.add_argument("--salida", default="informe_semana3.md",
                        help="Archivo de salida del informe.")
    args = parser.parse_args()

    print("Evaluando… (algunas verificaciones ejecutan la suite y pueden tardar)\n")

    verificar_contexto()
    verificar_suite()
    verificar_arbitro()
    verificar_arquitectura()
    verificar_arq_008()
    verificar_diagrama()
    verificar_restriccion_en_esquema()
    verificar_create_all()
    verificar_alembic()
    verificar_contrato_openapi()
    verificar_alcance(args.base)

    informe = construir_informe()
    destino = RAIZ / args.salida
    destino.write_text(informe, encoding="utf-8")

    for r in RESULTADOS:
        print(f"{SIMBOLO[r.estado]}  {r.id:<8} {r.titulo:<42} {r.detalle}")

    print(f"\nInforme escrito en: {destino.relative_to(RAIZ)}")
    print("Pegá el bloque mermaid en cualquier visor (VS Code, GitHub) para verlo gráfico.")

    return 1 if any(r.estado == FALLA for r in RESULTADOS) else 0


if __name__ == "__main__":
    sys.exit(main())
