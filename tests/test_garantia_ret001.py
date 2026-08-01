"""
Árbitro de la Semana 3: la garantía de RET-001.

Este archivo NO debe modificarse durante la implementación. Es el instrumento
de medición de la tarea, no parte de ella (ver CA-000 en
`docs/contrato/criterios_de_aceptacion.md`).

A diferencia de `tests/test_race_demo.py` —que demuestra el defecto y forma
parte del material didáctico—, este módulo afirma la propiedad que el sistema
debe cumplir al terminar la semana:

    Dadas dos solicitudes concurrentes sobre la misma butaca y el mismo evento,
    exactamente una crea la retención y la otra recibe un conflicto de dominio.

Al comenzar la semana estas pruebas FALLAN. Ese es el enunciado del trabajo.
"""

import threading
from datetime import datetime, timedelta

import pytest

from app.application import use_cases
from app.core.rules import RetencionDuplicadaError
from app.infrastructure.db import SessionLocal
from app.infrastructure.models import EventModel, SeatModel
from app.infrastructure.repository import SqlAlchemyHoldRepository

EVENTO = "evento-garantia"
BUTACA = "butaca-garantia"


def _sembrar():
    session = SessionLocal()
    try:
        session.add(
            EventModel(
                id=EVENTO,
                name="Evento para verificar la garantía",
                starts_at=datetime.now() + timedelta(days=1),
                ends_at=datetime.now() + timedelta(days=1, hours=2),
            )
        )
        session.add(SeatModel(id=BUTACA, event_id=EVENTO, label="G1"))
        session.commit()
    finally:
        session.close()


def _intentar_retener(exitos: list, errores: list, demora: float = 0.3):
    """Ejecuta el caso de uso en su propia sesión y clasifica el resultado."""
    session = SessionLocal()
    try:
        repo = SqlAlchemyHoldRepository(session)
        hold = use_cases.crear_retencion(
            repo,
            event_id=EVENTO,
            seat_id=BUTACA,
            demora_didactica_seg=demora,
        )
        exitos.append(hold.id)
    except Exception as exc:  # noqa: BLE001 — la clasificación es el objeto de la prueba
        errores.append(exc)
    finally:
        session.close()


def _correr_dos_concurrentes():
    _sembrar()
    exitos: list = []
    errores: list = []

    hilos = [
        threading.Thread(target=_intentar_retener, args=(exitos, errores))
        for _ in range(2)
    ]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    return exitos, errores


# --------------------------------------------------------------------------
# CA-001 — exactamente una retención
# --------------------------------------------------------------------------


def test_ca_001_dos_solicitudes_concurrentes_producen_una_sola_retencion():
    """Verifica RET-001 a nivel de garantía."""
    exitos, errores = _correr_dos_concurrentes()

    assert len(exitos) == 1, (
        f"RET-001 no está garantizada: {len(exitos)} solicitudes crearon una "
        f"retención sobre la misma butaca (se esperaba exactamente 1). "
        f"Errores observados: {[type(e).__name__ for e in errores]}"
    )
    assert len(errores) == 1, (
        f"Se esperaba que exactamente una solicitud fuera rechazada; "
        f"se observaron {len(errores)} rechazos."
    )


# --------------------------------------------------------------------------
# CA-002 — el conflicto llega como error de dominio, no como error técnico
# --------------------------------------------------------------------------


def test_ca_002_el_rechazo_es_una_excepcion_de_dominio():
    """Verifica ARQ-008: la excepción del ORM no cruza la frontera."""
    _, errores = _correr_dos_concurrentes()

    assert errores, "No hubo ningún rechazo que inspeccionar."
    error = errores[0]

    modulo = type(error).__module__
    assert not modulo.startswith("sqlalchemy"), (
        f"La solicitud rechazada recibió {type(error).__name__} de {modulo}. "
        f"Una excepción de la biblioteca de persistencia no debe salir de "
        f"app/infrastructure: el adaptador tiene que traducirla."
    )
    assert isinstance(error, RetencionDuplicadaError), (
        f"Se esperaba RetencionDuplicadaError y se obtuvo "
        f"{type(error).__name__}: {error}"
    )


# --------------------------------------------------------------------------
# CA-003 — la sesión sigue siendo utilizable después del conflicto
# --------------------------------------------------------------------------


def test_ca_003_la_sesion_queda_utilizable_despues_del_conflicto():
    """Un conflicto sin rollback deja la sesión inservible para lo que sigue."""
    _sembrar()

    session = SessionLocal()
    try:
        repo = SqlAlchemyHoldRepository(session)
        repo.crear_retencion(EVENTO, BUTACA)

        with pytest.raises(Exception):
            repo.crear_retencion(EVENTO, BUTACA)

        # Si el adaptador no hizo rollback, esta consulta falla.
        eventos = repo.listar_eventos()
        assert any(e.id == EVENTO for e in eventos), (
            "La sesión quedó inutilizable después del conflicto: falta un "
            "rollback en el adaptador."
        )
    finally:
        session.close()


# --------------------------------------------------------------------------
# RET-002 — CONFIRMED también ocupa la butaca
# --------------------------------------------------------------------------


def test_ret_002_una_butaca_confirmada_no_admite_nueva_retencion():
    """Verifica RET-002: ACTIVE y CONFIRMED ocupan; el resto no."""
    _sembrar()

    session = SessionLocal()
    try:
        repo = SqlAlchemyHoldRepository(session)
        hold = repo.crear_retencion(EVENTO, BUTACA)
        repo.confirmar_retencion(hold.id)
    finally:
        session.close()

    session = SessionLocal()
    try:
        repo = SqlAlchemyHoldRepository(session)
        with pytest.raises(RetencionDuplicadaError):
            use_cases.crear_retencion(repo, event_id=EVENTO, seat_id=BUTACA)
    finally:
        session.close()


# --------------------------------------------------------------------------
# CA-012 — el conflicto se expone con un código estable
# --------------------------------------------------------------------------


def test_ca_012_el_conflicto_http_incluye_codigo_estable(client):
    """Verifica el contrato de errores de docs/contrato/contrato_api.md."""
    _sembrar()

    cuerpo = {"seat_id": BUTACA}
    primera = client.post(f"/events/{EVENTO}/holds", json=cuerpo)
    assert primera.status_code == 201, primera.text

    segunda = client.post(f"/events/{EVENTO}/holds", json=cuerpo)
    assert segunda.status_code == 409, segunda.text

    detalle = segunda.json().get("detail")
    assert isinstance(detalle, dict), (
        "El contrato exige un objeto con 'code' y 'message' en 'detail'; "
        f"se recibió: {detalle!r}"
    )
    assert detalle.get("code") == "SEAT_UNAVAILABLE", (
        f"Se esperaba el código SEAT_UNAVAILABLE y se recibió: {detalle!r}"
    )
