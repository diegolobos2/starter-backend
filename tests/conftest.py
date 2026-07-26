"""
Fixtures compartidas para la suite de tests.

Decisión pragmática (Semana 1): la suite normal corre contra
SQLite en archivo, no contra PostgreSQL. Esto evita que los tests
dependan de tener Docker/Postgres levantado. Se logra fijando la
variable de entorno DATABASE_URL ANTES de importar cualquier
módulo de la app, para que app/infrastructure/db.py arme el
engine con SQLite.

La demostración de la condición de carrera (test_race_demo.py) es
igualmente válida sobre SQLite, porque el defecto es una condición
de carrera a nivel de aplicación (verificar-y-luego-insertar sin
atomicidad), no específica de PostgreSQL. La garantía final que se
agrega en la Semana 3 sí se valida contra PostgreSQL en un entorno
de integración aparte.
"""

import os
import pathlib

_TEST_DB_PATH = pathlib.Path(__file__).parent / "test_data.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.db import Base, engine


@pytest.fixture(autouse=True)
def _reiniciar_base():
    """Reinicia el esquema antes de cada test para aislarlos entre sí."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    from main import app  # import diferido: ya con DATABASE_URL seteado

    with TestClient(app) as c:
        yield c
