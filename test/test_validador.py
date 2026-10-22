from datetime import date, timedelta

import pytest

from validador import RelojFijo, ValidadorDeAvistamiento

HOY = date(2026, 10, 21)


@pytest.fixture
def validador():
    # Doble: stub del reloj, siempre devuelve HOY
    return ValidadorDeAvistamiento(RelojFijo(HOY))


def datos_validos(**cambios):
    base = {
        "especie": "colibrí",
        "lugar": "Jardín Botánico",
        "fecha": "2026-10-20",
        "observador": "Yonnatan",
    }
    return {**base, **cambios}


# --- Especie: límites de longitud (partición y valores límite) ---

def test_especie_de_2_caracteres_es_invalida(validador):
    # Arrange
    datos = datos_validos(especie="ab")

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None
    assert "especie" in error


def test_especie_de_3_caracteres_es_valida(validador):
    # Arrange
    datos = datos_validos(especie="abc")

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is None


def test_especie_de_50_caracteres_es_valida(validador):
    # Arrange
    datos = datos_validos(especie="a" * 50)

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is None


def test_especie_de_51_caracteres_es_invalida(validador):
    # Arrange
    datos = datos_validos(especie="a" * 51)

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None
    assert "especie" in error


def test_especie_con_espacios_cuenta_sin_ellos(validador):
    # Arrange: 2 letras con espacios alrededor; tras strip() quedan 2
    datos = datos_validos(especie="   ab   ")

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None


def test_especie_solo_espacios_es_invalida(validador):
    # Arrange
    datos = datos_validos(especie="     ")

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None
    assert "especie" in error


# --- Fecha: límite con el reloj fijo ---

def test_fecha_de_hoy_es_valida(validador):
    # Arrange
    datos = datos_validos(fecha="2026-10-21")

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is None


def test_fecha_de_manana_es_invalida(validador):
    # Arrange
    manana = (HOY + timedelta(days=1)).isoformat()
    datos = datos_validos(fecha=manana)

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None
    assert "posterior" in error


def test_fecha_de_ayer_es_valida(validador):
    # Arrange
    ayer = (HOY - timedelta(days=1)).isoformat()
    datos = datos_validos(fecha=ayer)

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is None


# --- Fecha: formato ---

def test_fecha_con_barras_es_invalida(validador):
    # Arrange
    datos = datos_validos(fecha="20/09/2026")

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None
    assert "AAAA-MM-DD" in error


def test_fecha_sin_ceros_a_la_izquierda_es_invalida(validador):
    # Arrange
    datos = datos_validos(fecha="2026-9-1")

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None
    assert "AAAA-MM-DD" in error


def test_fecha_imposible_es_invalida(validador):
    # Arrange: 30 de febrero no existe
    datos = datos_validos(fecha="2026-02-30")

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None
    assert "AAAA-MM-DD" in error


# --- Estructura y campos obligatorios ---

def test_cuerpo_que_no_es_objeto_es_invalido(validador):
    # Arrange
    datos = ["colibrí", "Jardín", "2026-10-20", "Yonnatan"]

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None


def test_campo_faltante_se_reporta_por_nombre(validador):
    # Arrange
    datos = datos_validos()
    del datos["observador"]

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None
    assert "observador" in error


def test_lugar_solo_espacios_se_reporta(validador):
    # Arrange
    datos = datos_validos(lugar="   ")

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is not None
    assert "lugar" in error


def test_datos_completos_y_validos_no_tienen_error(validador):
    # Arrange
    datos = datos_validos()

    # Act
    error = validador.validar(datos)

    # Assert
    assert error is None