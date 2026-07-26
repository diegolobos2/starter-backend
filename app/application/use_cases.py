"""
Casos de uso de la aplicación.

Este módulo coordina QUÉ pasos ejecutar y en qué orden. No conoce
detalles HTTP (eso es responsabilidad de app/api) y no ejecuta SQL
directamente (eso es responsabilidad de app/infrastructure).

Depende del PUERTO app.application.ports.HoldRepository (una interfaz),
nunca de una implementación concreta de infraestructura. Quien decide
qué implementación concreta usar (SqlAlchemyHoldRepository, o un doble
de prueba) es la capa de arriba (app/api) o el test, e inyecta esa
implementación como parámetro `repo`.

Ver docs/contrato/arquitectura.md, sección "Flujo de una operación con
reglas de negocio", y docs/adr/ADR-002.md.
"""

from app.application.ports import HoldRepository
from app.core.entities import Event, Hold, Seat
from app.core.rules import validar_creacion_retencion


class EventoNoEncontradoError(Exception):
    pass


class ButacaNoEncontradaError(Exception):
    pass


class RetencionNoEncontradaError(Exception):
    pass


def listar_eventos(repo: HoldRepository) -> list[Event]:
    return repo.listar_eventos()


def obtener_evento(repo: HoldRepository, event_id: str) -> Event:
    evento = repo.obtener_evento(event_id)
    if evento is None:
        raise EventoNoEncontradoError(event_id)
    return evento


def listar_butacas(repo: HoldRepository, event_id: str) -> list[Seat]:
    obtener_evento(repo, event_id)  # valida existencia del evento
    return repo.listar_butacas(event_id)


def crear_retencion(
    repo: HoldRepository,
    event_id: str,
    seat_id: str,
    demora_didactica_seg: float = 0.0,
) -> Hold:
    """
    Caso de uso: crear una retención temporal sobre una butaca.

    Pasos (ver docs/contrato/arquitectura.md):
    1. Infrastructure recupera evento, butaca y retenciones existentes.
    2. Core evalúa la regla RET-001.
    3. Application decide si continuar.
    4. Infrastructure persiste la nueva retención.

    ADVERTENCIA (Semana 1): entre el paso 1 y el paso 4 existe una
    ventana en la que otra petición concurrente puede violar RET-001.
    Esto es intencional. Ver ADR-001 y tests/test_race_demo.py. La
    garantía real llega en Semana 3, a nivel de infraestructura.
    """
    evento = repo.obtener_evento(event_id)
    if evento is None:
        raise EventoNoEncontradoError(event_id)

    butaca = repo.obtener_butaca(seat_id)
    if butaca is None or butaca.event_id != event_id:
        raise ButacaNoEncontradaError(seat_id)

    retenciones_existentes = repo.retenciones_activas_de_butaca(event_id, seat_id)

    # Decisión de dominio, pura, sin acceso a la base de datos.
    validar_creacion_retencion(retenciones_existentes)

    return repo.crear_retencion(
        event_id, seat_id, demora_didactica_seg=demora_didactica_seg
    )


def confirmar_retencion(repo: HoldRepository, hold_id: str) -> Hold:
    retencion = repo.confirmar_retencion(hold_id)
    if retencion is None:
        raise RetencionNoEncontradaError(hold_id)
    return retencion
