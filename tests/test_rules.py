"""
Tests unitarios de las reglas de negocio (app/core).

Estos tests no tocan la base de datos ni HTTP: son puros, rápidos,
y verifican la regla RET-001 de forma aislada.
"""

from datetime import datetime

import pytest

from app.core.entities import Hold, HoldStatus
from app.core.rules import (
    RetencionDuplicadaError,
    puede_crear_retencion,
    validar_creacion_retencion,
)


def _hold(status: HoldStatus) -> Hold:
    return Hold(
        id="h1",
        event_id="e1",
        seat_id="s1",
        status=status,
        created_at=datetime.utcnow(),
    )


def test_permite_crear_si_no_hay_retenciones():
    assert puede_crear_retencion([]) is True


def test_no_permite_crear_si_ya_hay_una_activa():
    existentes = [_hold(HoldStatus.ACTIVE)]
    assert puede_crear_retencion(existentes) is False


def test_permite_crear_si_la_existente_esta_liberada():
    existentes = [_hold(HoldStatus.RELEASED)]
    assert puede_crear_retencion(existentes) is True


def test_validar_creacion_lanza_error_de_dominio():
    existentes = [_hold(HoldStatus.ACTIVE)]
    with pytest.raises(RetencionDuplicadaError):
        validar_creacion_retencion(existentes)
