from abc import ABC, abstractmethod


class AvistamientoRepositoryInterface(ABC):
    """Puerto de salida: lo que el núcleo necesita de la persistencia."""

    @abstractmethod
    def listar(self) -> list[dict]:
        ...

    @abstractmethod
    def obtener(self, id_: int) -> dict | None:
        ...

    @abstractmethod
    def crear(self, datos: dict) -> dict:
        ...

    @abstractmethod
    def actualizar(self, id_: int, datos: dict) -> dict | None:
        ...

    @abstractmethod
    def eliminar(self, id_: int) -> bool:
        ...

    @abstractmethod
    def resumen(self) -> list[dict]:
        ...