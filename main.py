"""
Punto de entrada de la aplicación.

Ensambla la app de FastAPI, monta las rutas y no crea tablas automáticamente.
Ver nota sobre Alembic en README.md.
"""

from fastapi import FastAPI

from app.api.routes import router
from app.infrastructure.db import Base, SessionLocal, engine
from app.infrastructure.repository import sembrar_datos_demo

app = FastAPI(title="Starter Backend IA — Complejo de salas para eventos")
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    # En Semana 3 la aplicación asume que el esquema se gestiona con Alembic.
    # No se ejecuta ninguna creación automática de tablas al iniciar.

    session = SessionLocal()
    try:
        sembrar_datos_demo(session)
    finally:
        session.close()
