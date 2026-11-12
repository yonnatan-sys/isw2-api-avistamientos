import os

from flask import Flask, jsonify, request

from aplicacion.excepciones import AvistamientoNoEncontrado, DatosInvalidos
from aplicacion.servicio_avistamientos import ServicioAvistamientos
from dominio.validador import ValidadorDeAvistamiento
from infraestructura.repositorio_sqlite import RepositorioSQLite


def create_app(db_path=None, reloj=None):
    app = Flask(__name__)
    ruta = db_path or os.environ.get("DB_PATH", "avistamientos.db")
    app.config["DB_PATH"] = ruta

    # Composición: aquí se decide qué adaptador concreto usar
    servicio = ServicioAvistamientos(
        RepositorioSQLite(ruta),
        ValidadorDeAvistamiento(reloj),
    )

    @app.errorhandler(AvistamientoNoEncontrado)
    def _no_encontrado(_e):
        return jsonify({"error": "Avistamiento no encontrado"}), 404

    @app.errorhandler(DatosInvalidos)
    def _datos_invalidos(e):
        return jsonify({"error": e.mensaje}), 400

    @app.get("/avistamientos")
    def listar():
        return jsonify(servicio.listar()), 200

    @app.get("/avistamientos/resumen")
    def resumen():
        return jsonify(servicio.resumen()), 200

    @app.get("/avistamientos/<int:id_>")
    def obtener(id_):
        return jsonify(servicio.obtener(id_)), 200

    @app.post("/avistamientos")
    def crear():
        return jsonify(servicio.crear(request.get_json(silent=True))), 201

    @app.put("/avistamientos/<int:id_>")
    def actualizar(id_):
        return jsonify(servicio.actualizar(id_, request.get_json(silent=True))), 200

    @app.delete("/avistamientos/<int:id_>")
    def eliminar(id_):
        servicio.eliminar(id_)
        return "", 204

    @app.errorhandler(404)
    def no_encontrado_ruta(_e):
        return jsonify({"error": "Ruta no encontrada"}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(_e):
        return jsonify({"error": "Método no permitido"}), 405

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000)