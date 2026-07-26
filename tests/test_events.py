"""
Tests de integración de los endpoints HTTP.

Corren contra SQLite (ver conftest.py). Usan los datos de ejemplo
sembrados por app.infrastructure.repository.sembrar_datos_demo,
que se ejecuta en el evento de startup de la app.
"""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_listar_eventos(client):
    resp = client.get("/events")
    assert resp.status_code == 200
    eventos = resp.json()
    assert len(eventos) == 1
    assert eventos[0]["id"] == "evento-demo"


def test_obtener_evento_existente(client):
    resp = client.get("/events/evento-demo")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Recital de ejemplo"


def test_obtener_evento_inexistente(client):
    resp = client.get("/events/no-existe")
    assert resp.status_code == 404


def test_listar_butacas(client):
    resp = client.get("/events/evento-demo/seats")
    assert resp.status_code == 200
    butacas = resp.json()
    assert len(butacas) == 5


def test_crear_retencion_exitosa(client):
    resp = client.post("/events/evento-demo/holds", json={"seat_id": "butaca-1"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "active"
    assert body["seat_id"] == "butaca-1"


def test_crear_retencion_duplicada_devuelve_409(client):
    primera = client.post("/events/evento-demo/holds", json={"seat_id": "butaca-2"})
    assert primera.status_code == 201

    segunda = client.post("/events/evento-demo/holds", json={"seat_id": "butaca-2"})
    assert segunda.status_code == 409


def test_confirmar_retencion(client):
    creada = client.post(
        "/events/evento-demo/holds", json={"seat_id": "butaca-3"}
    ).json()

    resp = client.post(f"/holds/{creada['id']}/confirm")
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"


def test_confirmar_retencion_inexistente(client):
    resp = client.post("/holds/no-existe/confirm")
    assert resp.status_code == 404
