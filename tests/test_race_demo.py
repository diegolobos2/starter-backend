"""
Demostración didáctica de la condición de carrera pendiente (RET-001).

Este test está marcado con `race_demo` y NO forma parte de la suite
normal (ver pytest.ini). Se ejecuta explícitamente con:

    pytest -m race_demo -v

Objetivo pedagógico: mostrar que, tal como está el starter en la
Semana 1, dos peticiones concurrentes pueden crear dos retenciones
activas para la misma butaca — violando RET-001 — porque el paso
"consultar retenciones existentes" y el paso "insertar la nueva
retención" no son atómicos (ver app/application/use_cases.py y
ADR-001).

Este defecto se resuelve recién en la Semana 3, agregando una
garantía técnica en app/infrastructure (constraint único y/o
transacción con bloqueo).
"""

import threading

import pytest
from datetime import datetime, timedelta

from app.application import use_cases
from app.infrastructure.db import SessionLocal
from app.infrastructure.models import EventModel, SeatModel
from app.infrastructure.repository import SqlAlchemyHoldRepository


def _sembrar_evento_y_butaca():
    session = SessionLocal()
    try:
        evento = EventModel(
            id="evento-race",
            name="Evento para demo de concurrencia",
            starts_at=datetime.utcnow() + timedelta(days=1),
            ends_at=datetime.utcnow() + timedelta(days=1, hours=2),
        )
        session.add(evento)
        session.add(SeatModel(id="butaca-race", event_id=evento.id, label="R1"))
        session.commit()
    finally:
        session.close()


@pytest.mark.race_demo
def test_dos_peticiones_concurrentes_violan_RET_001():
    _sembrar_evento_y_butaca()

    resultados: list[str] = []
    errores: list[Exception] = []

    def intentar_crear_retencion():
        session = SessionLocal()
        try:
            repo = SqlAlchemyHoldRepository(session)
            hold = use_cases.crear_retencion(
                repo,
                event_id="evento-race",
                seat_id="butaca-race",
                # Ensancha la ventana entre "consultar" e "insertar"
                # para que la carrera se manifieste de forma confiable
                # en la demo, en lugar de depender del azar.
                demora_didactica_seg=0.3,
            )
            resultados.append(hold.id)
        except Exception as exc:  # noqa: BLE001
            errores.append(exc)
        finally:
            session.close()

    hilo_a = threading.Thread(target=intentar_crear_retencion)
    hilo_b = threading.Thread(target=intentar_crear_retencion)

    hilo_a.start()
    hilo_b.start()
    hilo_a.join()
    hilo_b.join()

    # Lo esperable, si RET-001 se cumpliera bajo concurrencia, es que
    # UNA de las dos peticiones tenga éxito y la otra sea rechazada.
    # Este assert está escrito para FALLAR en la Semana 1, evidenciando
    # el defecto: ambas peticiones consiguen crear una retención activa.
    assert len(resultados) == 1, (
        f"RET-001 violada bajo concurrencia: se crearon {len(resultados)} "
        f"retenciones activas para la misma butaca (se esperaba 1). "
        f"Este fallo es el punto de partida para la Semana 3."
    )
