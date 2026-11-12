class AvistamientoNoEncontrado(Exception):
    pass


class DatosInvalidos(Exception):
    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.mensaje = mensaje