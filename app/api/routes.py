"""
Adaptador de entrada HTTP.

Responsabilidad: rutas, validación de request, traducción de
errores de dominio a códigos HTTP. No contiene reglas de negocio
ni acceso a SQL. Ver docs/contrato/arquitectura.md.

Esta capa es también quien decide qué adaptador de persistencia
concreto se usa: construye un SqlAlchemyHoldRepository a partir de la
Session y lo inyecta en los casos de uso. Application solo conoce el
puerto HoldRepository, no esta elección concreta.
"""

import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import CreateHoldIn, EventOut, HoldOut, SeatOut
from app.application import use_cases
from app.application.ports import HoldRepository
from app.core.rules import RetencionDuplicadaError
from app.infrastructure.db import get_session
from app.infrastructure.repository import SqlAlchemyHoldRepository

router = APIRouter()

# Permite ensanchar la ventana de la condición de carrera durante la
# demostración didáctica, sin tocar el código de negocio.
DEMORA_DIDACTICA_SEG = float(os.getenv("DEMORA_DIDACTICA_SEG", "0"))


def get_repo(session: Session = Depends(get_session)) -> HoldRepository:
    """
    Construye el adaptador concreto de persistencia y lo entrega como
    puerto. Este es el único lugar donde la API decide qué
    implementación de HoldRepository se usa en producción.
    """
    return SqlAlchemyHoldRepository(session)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/events", response_model=list[EventOut])
def listar_eventos(repo: HoldRepository = Depends(get_repo)):
    return use_cases.listar_eventos(repo)


@router.get("/events/{event_id}", response_model=EventOut)
def obtener_evento(event_id: str, repo: HoldRepository = Depends(get_repo)):
    try:
        return use_cases.obtener_evento(repo, event_id)
    except use_cases.EventoNoEncontradoError:
        raise HTTPException(status_code=404, detail="Evento no encontrado")


@router.get("/events/{event_id}/seats", response_model=list[SeatOut])
def listar_butacas(event_id: str, repo: HoldRepository = Depends(get_repo)):
    try:
        return use_cases.listar_butacas(repo, event_id)
    except use_cases.EventoNoEncontradoError:
        raise HTTPException(status_code=404, detail="Evento no encontrado")


@router.post("/events/{event_id}/holds", response_model=HoldOut, status_code=201)
def crear_retencion(
    event_id: str,
    body: CreateHoldIn,
    repo: HoldRepository = Depends(get_repo),
):
    try:
        return use_cases.crear_retencion(
            repo,
            event_id=event_id,
            seat_id=body.seat_id,
            demora_didactica_seg=DEMORA_DIDACTICA_SEG,
        )
    except use_cases.EventoNoEncontradoError:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    except use_cases.ButacaNoEncontradaError:
        raise HTTPException(status_code=404, detail="Butaca no encontrada")
    except RetencionDuplicadaError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/holds/{hold_id}/confirm", response_model=HoldOut)
def confirmar_retencion(hold_id: str, repo: HoldRepository = Depends(get_repo)):
    try:
        return use_cases.confirmar_retencion(repo, hold_id)
    except use_cases.RetencionNoEncontradaError:
        raise HTTPException(status_code=404, detail="Retención no encontrada")
