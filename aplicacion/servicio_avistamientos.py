from aplicacion.excepciones import AvistamientoNoEncontrado, DatosInvalidos
from dominio.validador import CAMPOS


class ServicioAvistamientos:
    """Caso de uso: reglas de la aplicación. Solo conoce el puerto, no SQLite."""

    def __init__(self, repositorio, validador):
        self._repo = repositorio
        self._validador = validador

    def listar(self):
        return self._repo.listar()

    def resumen(self):
        return self._repo.resumen()

    def obtener(self, id_):
        av = self._repo.obtener(id_)
        if av is None:
            raise AvistamientoNoEncontrado()
        return av

    def crear(self, datos):
        self._validar(datos)
        return self._repo.crear(self._normalizar(datos))

    def actualizar(self, id_, datos):
        self.obtener(id_)  # 404 antes de validar, igual que antes
        self._validar(datos)
        return self._repo.actualizar(id_, self._normalizar(datos))

    def eliminar(self, id_):
        self.obtener(id_)
        self._repo.eliminar(id_)

    def _validar(self, datos):
        error = self._validador.validar(datos)
        if error:
            raise DatosInvalidos(error)

    @staticmethod
    def _normalizar(datos):
        return {c: datos[c].strip() for c in CAMPOS}