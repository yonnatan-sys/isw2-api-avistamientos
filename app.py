import os
import sqlite3
from datetime import datetime

from flask import Flask, g, jsonify, request

CAMPOS = ("especie", "lugar", "fecha", "observador")


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("DB_PATH", "avistamientos.db")

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DB_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with sqlite3.connect(app.config["DB_PATH"]) as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS avistamientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                especie TEXT NOT NULL,
                lugar TEXT NOT NULL,
                fecha TEXT NOT NULL,
                observador TEXT NOT NULL
            )"""
        )

    def validar(datos):
        """Devuelve mensaje de error o None si los datos son válidos."""
        if not isinstance(datos, dict):
            return "El cuerpo debe ser un objeto JSON"
        faltan = [c for c in CAMPOS if not isinstance(datos.get(c), str) or not datos[c].strip()]
        if faltan:
            return f"Faltan o están vacíos: {', '.join(faltan)}"
        try:
            datetime.strptime(datos["fecha"], "%Y-%m-%d")
        except ValueError:
            return "fecha debe tener formato AAAA-MM-DD"
        return None

    def buscar(id_):
        row = get_db().execute("SELECT * FROM avistamientos WHERE id = ?", (id_,)).fetchone()
        return dict(row) if row else None

    @app.get("/avistamientos")
    def listar():
        rows = get_db().execute("SELECT * FROM avistamientos ORDER BY id").fetchall()
        return jsonify([dict(r) for r in rows]), 200

    @app.get("/avistamientos/resumen")
    def resumen():
        rows = get_db().execute(
            "SELECT especie, COUNT(*) AS total FROM avistamientos GROUP BY especie ORDER BY total DESC, especie"
        ).fetchall()
        return jsonify([dict(r) for r in rows]), 200

    @app.get("/avistamientos/<int:id_>")
    def obtener(id_):
        av = buscar(id_)
        if av is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        return jsonify(av), 200

    @app.post("/avistamientos")
    def crear():
        datos = request.get_json(silent=True)
        error = validar(datos)
        if error:
            return jsonify({"error": error}), 400
        db = get_db()
        cur = db.execute(
            "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
            tuple(datos[c].strip() for c in CAMPOS),
        )
        db.commit()
        return jsonify(buscar(cur.lastrowid)), 201

    @app.put("/avistamientos/<int:id_>")
    def actualizar(id_):
        if buscar(id_) is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        datos = request.get_json(silent=True)
        error = validar(datos)
        if error:
            return jsonify({"error": error}), 400
        db = get_db()
        db.execute(
            "UPDATE avistamientos SET especie=?, lugar=?, fecha=?, observador=? WHERE id=?",
            (*(datos[c].strip() for c in CAMPOS), id_),
        )
        db.commit()
        return jsonify(buscar(id_)), 200

    @app.delete("/avistamientos/<int:id_>")
    def eliminar(id_):
        if buscar(id_) is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        db = get_db()
        db.execute("DELETE FROM avistamientos WHERE id = ?", (id_,))
        db.commit()
        return "", 204

    @app.errorhandler(404)
    def no_encontrado(_e):
        return jsonify({"error": "Ruta no encontrada"}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(_e):
        return jsonify({"error": "Método no permitido"}), 405

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000)
