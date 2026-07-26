"""
Punto de entrada de la aplicación.

Ensambla la app de FastAPI, monta las rutas y crea las tablas si
no existen (create_all). Ver nota sobre Alembic en README.md.
"""

from fastapi import FastAPI

from app.api.routes import router
from app.infrastructure.db import Base, SessionLocal, engine
from app.infrastructure.repository import sembrar_datos_demo

app = FastAPI(title="Starter Backend IA — Complejo de salas para eventos")
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    # Semana 1: create_all en lugar de migraciones Alembic completas,
    # para mantener el arranque simple. Alembic queda preparado en
    # el proyecto para incorporarse formalmente sin romper nada.
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        sembrar_datos_demo(session)
    finally:
        session.close()
