# API REST de avistamientos de aves

Trabajo individual de Ingeniería de Software 2 (Sesión 17). API REST para registrar avistamientos de aves.
Python + Flask, datos en SQLite (archivo `avistamientos.db`, se crea solo), intercambio en JSON.

## Instalación y ejecución

Requiere Python 3.10+.

```bash
git clone https://github.com/yonnatan-sys/isw2-api-avistamientos.git
cd isw2-api-avistamientos
python -m venv .venv
# Linux/Mac:  source .venv/bin/activate
# Windows:    .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

La API queda en `http://127.0.0.1:5000`.

### Datos de ejemplo (opcional)

Para cargar 22 avistamientos de ejemplo (en otra terminal o antes de arrancar la API):

```bash
python seed.py              # carga solo si la base está vacía
python seed.py --reiniciar  # borra todo y recarga los ejemplos
```

## Recurso

```json
{ "id": 1, "especie": "colibrí", "lugar": "Jardín Botánico", "fecha": "2026-09-20", "observador": "Yonnatan" }
```

`id` lo asigna el sistema. Reglas de validación:

- `especie`: entre 3 y 50 caracteres (sin contar espacios al inicio y al final).
- `fecha`: formato `AAAA-MM-DD`, existente y no posterior a hoy.
- `lugar` y `observador`: obligatorios, no vacíos.

## Endpoints

| Petición | Respuesta |
|---|---|
| `GET /avistamientos` | 200 con la lista |
| `GET /avistamientos/{id}` | 200, o 404 si no existe |
| `POST /avistamientos` | 201 con el creado, o 400 si los datos son inválidos |
| `PUT /avistamientos/{id}` | 200, 404 si no existe, 400 si los datos son inválidos |
| `DELETE /avistamientos/{id}` | 204, o 404 si no existe |
| `GET /avistamientos/resumen` | 200 con el conteo por especie (bonus) |

Los errores 400 incluyen un mensaje que indica qué campo falló.

### Ejemplos con curl

```bash
# Registrar
curl -i -X POST http://127.0.0.1:5000/avistamientos \
  -H "Content-Type: application/json" \
  -d '{"especie":"colibrí","lugar":"Jardín Botánico","fecha":"2026-09-20","observador":"Yonnatan"}'

# Listar
curl -i http://127.0.0.1:5000/avistamientos

# Ver uno
curl -i http://127.0.0.1:5000/avistamientos/1

# Actualizar (reemplaza el recurso completo)
curl -i -X PUT http://127.0.0.1:5000/avistamientos/1 \
  -H "Content-Type: application/json" \
  -d '{"especie":"colibrí","lugar":"Chingaza","fecha":"2026-09-21","observador":"Yonnatan"}'

# Eliminar
curl -i -X DELETE http://127.0.0.1:5000/avistamientos/1

# Resumen por especie
curl -i http://127.0.0.1:5000/avistamientos/resumen

# Error 400 (faltan datos)
curl -i -X POST http://127.0.0.1:5000/avistamientos \
  -H "Content-Type: application/json" -d '{"especie":"colibrí"}'
```

> En Windows CMD usa comillas dobles escapadas o PowerShell/Git Bash para los `-d`.

## Pruebas

Las pruebas están en la carpeta `test/`: `test_validador.py` (unitarias, sin Flask ni base de datos) y `test_app.py` (integración por HTTP contra una base SQLite temporal).

Correr las pruebas:

```bash
pytest -v
```

Generar el reporte de cobertura (sentencias y ramas):

```bash
pytest --cov=app --cov=validador --cov-branch --cov-report=term-missing
```

Para generar un reporte HTML en `htmlcov/`, cambia la última opción por `--cov-report=html`.

## Estructura del proyecto

```
app.py            # API (Flask + SQLite)
validador.py      # Validación del avistamiento y interfaz Reloj
seed.py           # Datos de ejemplo (opcional)
pytest.ini        # Configuración de pytest
test/
  test_app.py       # Pruebas de integración (HTTP)
  test_validador.py # Pruebas unitarias del validador
docs/
  justificacion-pruebas.md  # Justificación de las decisiones de pruebas
requirements.txt  # Dependencias
.gitignore        # Excluye la base de datos, caché, cobertura y entorno virtual
README.md
```

## Uso de IA

Se usó **Claude (Anthropic), modelo Sonnet 5.5**, para generar la base del código y las pruebas. El código fue revisado y probado por mí.