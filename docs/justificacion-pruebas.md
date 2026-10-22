# Justificación de pruebas

## 1. Cambios para poder probar

- **Validación separada.** La validación estaba dentro de `create_app`. Ahora vive en `validador.py` (`ValidadorDeAvistamiento`) y se prueba sin levantar Flask ni la base de datos.
- **Reloj inyectado.** La fecha de hoy se obtiene de una interfaz `Reloj`, con `RelojSistema` en producción y `RelojFijo` en pruebas. `create_app(db_path, reloj)` lo recibe como parámetro.
- **Regla de negocio nueva.** La especie debe tener entre 3 y 50 caracteres, y la fecha no puede ser posterior a hoy.
- **Conexión cerrada.** La creación de la tabla usa `closing(...)`, para que la conexión a SQLite se cierre.

## 2. Tabla de casos (Parte A)

Especie (partición en tres tramos: menos de 3, de 3 a 50, más de 50):

| Valor | Tipo | Esperado | Razón |
|---|---|---|---|
| `""` o solo espacios | inválido | 400 | Campo vacío, verifica la regla de obligatorios. |
| 2 caracteres | inválido, límite inferior | 400 | Frontera del tramo inválido inferior. |
| 3 caracteres | válido, límite inferior | OK | Primer valor del tramo válido. |
| `colibrí` | representativo | OK | Caso típico del tramo válido. |
| 50 caracteres | válido, límite superior | OK | Último valor del tramo válido. |
| 51 caracteres | inválido, límite superior | 400 | Frontera del tramo inválido superior. |

Fecha (con `RelojFijo` fijado en 2026-10-21):

| Valor | Tipo | Esperado | Razón |
|---|---|---|---|
| `2026-10-21` (hoy) | límite | OK | Último día permitido. |
| `2026-10-22` (mañana) | límite | 400 | Primer día no permitido. |
| `2026-10-20` (ayer) | representativo | OK | Caso típico del tramo válido. |
| `20/09/2026` | formato inválido | 400 | Formato distinto de `AAAA-MM-DD`. |
| `2026-9-1` | formato inválido | 400 | Falta el cero a la izquierda. |
| `2026-02-30` | fecha imposible | 400 | El formato es correcto, pero la fecha no existe. |

## 3. Por qué cada nivel

- **`test_validador.py` (unitarias).** Por ejemplo, `test_especie_de_51_caracteres_es_invalida` llama directamente a `validar()`. No necesita Flask ni SQLite, y falla solo si la regla de longitud cambia.
- **`test_app.py` (integración).** Por ejemplo, `test_crear_y_obtener` hace un POST real, verifica el 201 y luego un GET al id nuevo. Esta prueba detecta lo que el validador no puede: que el `INSERT` guarde los datos correctamente, que la tabla exista, que el `id` se asigne y que la respuesta contenga lo guardado. Ninguna prueba unitaria ve la base de datos.

## 4. Dobles

- **Stub del reloj (`RelojFijo`).** Devuelve siempre la misma fecha. Se usó en `test_fecha_de_manana_es_invalida` y `test_fecha_de_hoy_es_valida`. Sin él, la prueba dependería del día en que se ejecute: una prueba con una fecha fija como "mañana" dejaría de funcionar cuando el calendario real llegue a esa fecha.
- **No hay doble de repositorio.** La API accede a SQLite directamente desde `app.py`, sin una capa de servicio separada. Por eso no se usó fake ni mock de la base. Las pruebas de integración usan una base SQLite real en un directorio temporal (`tmp_path`).

## 5. Lo que decidí no probar

- **`RelojSistema.hoy()`.** Solo envuelve `date.today()`, no tiene lógica. Se ejecuta en producción, pero las pruebas usan `RelojFijo` para tener resultados repetibles.
- **`Reloj.hoy()` con `NotImplementedError`.** Es una interfaz abstracta. Probarla solo subiría el porcentaje sin verificar comportamiento.
- **El bloque `if __name__ == "__main__"`.** Solo arranca el servidor. No contiene lógica.

## 6. Lectura de la cobertura

Con `pytest --cov=app --cov=validador --cov-branch --cov-report=term-missing`:

- `app.py`: 98% de sentencias y ramas. Falta la línea del `if __name__ == "__main__"` y una de sus ramas.
- `validador.py`: 98%. Falta la línea 11, el `raise NotImplementedError` de la interfaz.

Las líneas que faltan no tienen lógica de negocio, por lo que no se probaron. El porcentaje no fue la meta: lo que importa es que cada prueba tenga un `assert` con un resultado esperado. Por eso revisé que los casos de límite (2/3 y 50/51 caracteres, hoy y mañana) tengan aserciones concretas.