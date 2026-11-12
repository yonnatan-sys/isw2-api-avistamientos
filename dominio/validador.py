import re
from datetime import date, datetime

CAMPOS = ("especie", "lugar", "fecha", "observador")
ESPECIE_MIN, ESPECIE_MAX = 3, 50
PATRON_FECHA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


class Reloj:
    def hoy(self) -> date:
        raise NotImplementedError


class RelojSistema(Reloj):
    def hoy(self) -> date:
        return date.today()


class RelojFijo(Reloj):
    def __init__(self, fecha: date):
        self._fecha = fecha

    def hoy(self) -> date:
        return self._fecha


class ValidadorDeAvistamiento:
    def __init__(self, reloj: Reloj | None = None):
        self._reloj = reloj or RelojSistema()

    def validar(self, datos) -> str | None:
        """Devuelve el mensaje de error, o None si los datos son válidos."""
        if not isinstance(datos, dict):
            return "El cuerpo debe ser un objeto JSON"

        faltan = [c for c in CAMPOS if not isinstance(datos.get(c), str) or not datos[c].strip()]
        if faltan:
            return f"Faltan o están vacíos: {', '.join(faltan)}"

        especie = datos["especie"].strip()
        if not ESPECIE_MIN <= len(especie) <= ESPECIE_MAX:
            return "especie debe tener entre 3 y 50 caracteres"

        fecha = datos["fecha"].strip()
        if not PATRON_FECHA.fullmatch(fecha):
            return "fecha debe tener formato AAAA-MM-DD"
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return "fecha debe tener formato AAAA-MM-DD"
        if fecha_dt > self._reloj.hoy():
            return "fecha no puede ser posterior a hoy"

        return None