import pytest

from app import create_app

AVE = {"especie": "colibrí", "lugar": "Jardín Botánico", "fecha": "2026-09-20", "observador": "Yonnatan"}


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    return app.test_client()


def test_lista_vacia(client):
    r = client.get("/avistamientos")
    assert r.status_code == 200 and r.get_json() == []


def test_crear_y_obtener(client):
    r = client.post("/avistamientos", json=AVE)
    assert r.status_code == 201
    creado = r.get_json()
    assert creado["id"] == 1 and creado["especie"] == "colibrí"
    r = client.get(f"/avistamientos/{creado['id']}")
    assert r.status_code == 200 and r.get_json() == creado


def test_crear_datos_faltantes(client):
    assert client.post("/avistamientos", json={"especie": "colibrí"}).status_code == 400


def test_crear_fecha_invalida(client):
    assert client.post("/avistamientos", json={**AVE, "fecha": "20/09/2026"}).status_code == 400


def test_crear_sin_json(client):
    assert client.post("/avistamientos", data="hola").status_code == 400


def test_obtener_no_existe(client):
    assert client.get("/avistamientos/999").status_code == 404


def test_actualizar(client):
    client.post("/avistamientos", json=AVE)
    r = client.put("/avistamientos/1", json={**AVE, "lugar": "Chingaza"})
    assert r.status_code == 200 and r.get_json()["lugar"] == "Chingaza"


def test_actualizar_no_existe(client):
    assert client.put("/avistamientos/999", json=AVE).status_code == 404


def test_actualizar_datos_invalidos(client):
    client.post("/avistamientos", json=AVE)
    assert client.put("/avistamientos/1", json={"especie": "x"}).status_code == 400


def test_eliminar(client):
    client.post("/avistamientos", json=AVE)
    assert client.delete("/avistamientos/1").status_code == 204
    assert client.get("/avistamientos/1").status_code == 404


def test_eliminar_no_existe(client):
    assert client.delete("/avistamientos/999").status_code == 404


def test_resumen(client):
    client.post("/avistamientos", json=AVE)
    client.post("/avistamientos", json=AVE)
    client.post("/avistamientos", json={**AVE, "especie": "águila"})
    r = client.get("/avistamientos/resumen")
    assert r.status_code == 200
    assert r.get_json() == [{"especie": "colibrí", "total": 2}, {"especie": "águila", "total": 1}]
