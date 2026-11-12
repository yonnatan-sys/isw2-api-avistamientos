import sqlite3
from contextlib import closing

from aplicacion.puertos import AvistamientoRepositoryInterface
from dominio.validador import CAMPOS


class RepositorioSQLite(AvistamientoRepositoryInterface):
    def __init__(self, db_path):
        self._ruta = db_path
        with closing(sqlite3.connect(self._ruta)) as con:
            con.execute(
                """CREATE TABLE IF NOT EXISTS avistamientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    especie TEXT NOT NULL,
                    lugar TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    observador TEXT NOT NULL
                )"""
            )
            con.commit()

    def _conectar(self):
        con = sqlite3.connect(self._ruta)
        con.row_factory = sqlite3.Row
        return con

    def listar(self):
        with closing(self._conectar()) as con:
            rows = con.execute("SELECT * FROM avistamientos ORDER BY id").fetchall()
            return [dict(r) for r in rows]

    def obtener(self, id_):
        with closing(self._conectar()) as con:
            row = con.execute("SELECT * FROM avistamientos WHERE id = ?", (id_,)).fetchone()
            return dict(row) if row else None

    def crear(self, datos):
        with closing(self._conectar()) as con:
            cur = con.execute(
                "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
                tuple(datos[c] for c in CAMPOS),
            )
            con.commit()
            nuevo_id = cur.lastrowid
        return self.obtener(nuevo_id)

    def actualizar(self, id_, datos):
        with closing(self._conectar()) as con:
            con.execute(
                "UPDATE avistamientos SET especie=?, lugar=?, fecha=?, observador=? WHERE id=?",
                (*(datos[c] for c in CAMPOS), id_),
            )
            con.commit()
        return self.obtener(id_)

    def eliminar(self, id_):
        with closing(self._conectar()) as con:
            cur = con.execute("DELETE FROM avistamientos WHERE id = ?", (id_,))
            con.commit()
            return cur.rowcount > 0

    def resumen(self):
        with closing(self._conectar()) as con:
            rows = con.execute(
                "SELECT especie, COUNT(*) AS total FROM avistamientos "
                "GROUP BY especie ORDER BY total DESC, especie"
            ).fetchall()
            return [dict(r) for r in rows]