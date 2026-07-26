"""
Tests de arquitectura (Semana 2).

No verifican COMPORTAMIENTO (eso lo hacen test_rules.py, test_events.py,
test_race_demo.py). Verifican ESTRUCTURA: que las capas dependan entre
sí solo en la dirección permitida por la regla de dependencia de Clean
Architecture (ver docs/arquitectura.md y AGENTS.md).

Técnica: se lee cada archivo con `ast` (sin ejecutarlo) y se listan sus
imports. No hace falta instalar nada extra: es Python puro. Herramientas
como import-linter o pytest-archon hacen lo mismo de forma más completa
para proyectos grandes; acá se usa ast para que el mecanismo quede a la
vista y sin dependencias nuevas.

Estos tests son la "constitución hecha código": convierten reglas de
AGENTS.md en verificaciones automáticas que el pipeline de CI puede
correr en cada push. Una regla declarada en prosa se puede violar sin
que nadie lo note; una regla convertida en test se pone en rojo sola.
"""

import ast
from pathlib import Path

APP_DIR = Path(__file__).parent.parent / "app"


def _imports_de(archivo: Path) -> list[str]:
    """Devuelve los módulos importados por un archivo, vía ast (sin ejecutarlo)."""
    arbol = ast.parse(archivo.read_text())
    modulos: list[str] = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.append(nodo.module)
        elif isinstance(nodo, ast.Import):
            modulos.extend(alias.name for alias in nodo.names)
    return modulos


def test_core_no_importa_nada_externo():
    """
    app/core/*.py no debe importar FastAPI, SQLAlchemy, psycopg, ni
    módulos de app/application, app/infrastructure o app/api.

    Es la promesa central del proyecto: el core es un núcleo funcional
    puro, testeable sin base de datos ni framework web. Si este test se
    pone en rojo, alguien contaminó el dominio.
    """
    prohibidos = (
        "fastapi",
        "sqlalchemy",
        "psycopg",
        "app.infrastructure",
        "app.api",
        "app.application",
    )
    violaciones: dict[str, list[str]] = {}

    for archivo in (APP_DIR / "core").glob("*.py"):
        encontrados = [
            m for m in _imports_de(archivo)
            if any(m == p or m.startswith(p + ".") for p in prohibidos)
        ]
        if encontrados:
            violaciones[archivo.name] = encontrados

    assert violaciones == {}, (
        f"app/core no debe depender de infraestructura ni frameworks, "
        f"pero se encontró: {violaciones}"
    )


def test_application_no_importa_infrastructure_concreta():
    """
    app/application/use_cases.py no debe importar app.infrastructure.

    Application depende del PUERTO app.application.ports.HoldRepository,
    no de una implementación concreta. Quien construye el adaptador
    concreto (SqlAlchemyHoldRepository) e inyecta el puerto es app/api.

    Este test FALLABA en la versión inicial del starter (cuando
    use_cases.py importaba app.infrastructure.repository directamente) y
    quedó documentado en ADR-002. Al introducir el puerto en la Semana
    2, la fuga se resolvió y el test pasa a verde.
    """
    archivo = APP_DIR / "application" / "use_cases.py"
    encontrados = [m for m in _imports_de(archivo) if "infrastructure" in m]

    assert encontrados == [], (
        f"application/use_cases.py importa infrastructure directamente: "
        f"{encontrados}. Debe depender del puerto HoldRepository, no del "
        f"adaptador concreto. Ver ADR-002."
    )


def test_core_no_conoce_el_puerto():
    """
    El puerto (app/application/ports.py) pertenece a Application, no al
    core. app/core no debe importarlo: el core recibe datos ya resueltos
    por parámetro, nunca consulta un repositorio (ni siquiera a través
    de una interfaz).

    Esto hace explícita nuestra decisión de diseño (más estricta que el
    mínimo de Clean Architecture): el core no hace I/O, ni directo ni
    vía puerto. Ver docs/arquitectura.md, sección "Core".
    """
    violaciones: dict[str, list[str]] = {}
    for archivo in (APP_DIR / "core").glob("*.py"):
        encontrados = [m for m in _imports_de(archivo) if "ports" in m]
        if encontrados:
            violaciones[archivo.name] = encontrados

    assert violaciones == {}, (
        f"app/core no debe conocer el puerto (es de application): {violaciones}"
    )
