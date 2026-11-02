# Guía para entender el código

Lee el proyecto siguiendo el recorrido de una solicitud. Primero comprende qué recibe cada función y qué devuelve; después revisa sus condiciones y ciclos. Esta guía corresponde a `api.py` y `dashboard.py` de esta versión.

## 1. Dos archivos, dos responsabilidades

**`api.py`** contiene el backend: conecta con MongoDB, valida entradas, consulta documentos y calcula estadísticas. **`dashboard.py`** contiene la interfaz: recoge selecciones, llama a la API y muestra resultados. El dashboard conoce la dirección del backend; la cadena privada de MongoDB pertenece a la API.

En el backend, `return` entrega un resultado que FastAPI convierte en una respuesta HTTP. Un `print` solo escribiría en la terminal y no entregaría los datos al dashboard.

## 2. Qué importamos y para qué

Las dependencias directas son las siete de `requirements.txt`. Pydantic se instala como dependencia de FastAPI y `certifi` como dependencia de `requests`. Este último también se utilizaba en el notebook del segundo corte.

| Importación o herramienta | Uso en este proyecto |
|---|---|
| `pymongo` | `MongoClient` conecta con MongoDB; sus excepciones permiten manejar fallas. |
| `certifi` | `where()` devuelve la ruta al archivo de certificados de confianza usado al conectar con Atlas mediante una URI SRV. |
| `fastapi` | Define rutas, recibe parámetros, comparte filtros y genera respuestas. |
| `pydantic` | `BaseModel`, `Field` y validadores describen las reglas de un registro nuevo. |
| `requests` | Envía solicitudes GET y POST desde el dashboard. |
| `pandas` | Convierte respuestas en tablas y prepara los datos para mostrarlos. |
| `streamlit` | Construye controles, tablas, mensajes y gráficas. |
| `python-dotenv` | `load_dotenv` carga la configuración local. |
| `uvicorn` | Se utiliza en el comando que ejecuta el backend. |

Los demás módulos vienen con Python: `os` lee variables de entorno; `Path` localiza archivos; `datetime` obtiene el año actual; `math` comprueba números finitos y redondea páginas hacia arriba; `statistics.median` calcula medianas; `re` prepara búsquedas de texto; `Literal` limita las opciones permitidas. No requieren nuevas instalaciones.

## 3. Mapa de api.py

El archivo está dividido en configuración, preparación de datos, filtros, rutas de lectura y creación.

| Función o clase | Qué hace |
|---|---|
| `obtener_coleccion` | Lee la configuración, selecciona una colección y reconoce su esquema. |
| `numero_positivo` | Acepta magnitudes positivas y finitas; devuelve `None` si no son utilizables. |
| `anio_valido` | Comprueba que un año sea entero positivo. |
| `normalizar` | Unifica nombres de campos y prepara un documento para responder. |
| `es_evaluable` | Comprueba que radio e insolación tengan datos e indicadores puntuales. |
| `es_candidato` | Aplica los intervalos de radio e insolación del proyecto. |
| `origen_del_radio` | Resume la procedencia descrita en la referencia del radio. |
| `recibir_filtros` | Recibe y valida los parámetros compartidos. |
| `construir_consulta` | Convierte esos parámetros en condiciones de MongoDB. |
| `inicio`, `salud`, `opciones` | Presentan las rutas, comprueban conexión y obtienen opciones de toda la colección. |
| `listar_datos` | Devuelve una página de documentos y el total de coincidencias. |
| `estadisticas` | Calcula las respuestas de las cuatro preguntas sobre toda la selección. |
| `NuevoRegistro`, `crear_registro` | Validan y guardan un documento manual. |
| `datos_invalidos`, `error_mongodb` | Devuelven errores comprensibles sin exponer la conexión privada. |

`obtener_coleccion` conserva una conexión reutilizable en `cliente`. Si se indica una colección, la respeta. En caso contrario busca las colecciones conocidas. El diccionario `ALIAS_CLASE` traduce, por ejemplo, `metodo` a `metodo_descubrimiento` al responder; no reescribe la colección original.

Para una URI que empieza por `mongodb+srv://`, la variable `certificados` contiene la ruta que devuelve `certifi.where()`. `tlsCAFile` indica a `MongoClient` dónde están esos certificados de confianza. Esto conserva el ajuste de conexión del notebook y mantiene la validación del servidor. Con una URI local `mongodb://`, el valor queda en `None` y se conservan sus opciones originales.

MongoDB utiliza un identificador `_id` que puede ser un `ObjectId`. `str(...)` lo convierte a texto para incluirlo en JSON. En Python, `None` significa dato ausente; en JSON se representa como `null`. Esa ausencia se conserva y no se transforma en cero.

## 4. Cómo funciona una consulta

`@app.get("/datos")` registra la función situada debajo para atender esa ruta. El decorador relaciona una dirección HTTP con una función Python.

`Query` describe los parámetros de la URL y sus reglas. Por ejemplo, `ge=1` significa mayor o igual que uno; `le=200`, menor o igual que doscientos. FastAPI valida esos límites antes de ejecutar la consulta.

`Depends(recibir_filtros)` indica a FastAPI que ejecute esa función y entregue su diccionario a la ruta. Tanto `/datos` como `/estadisticas` reciben las mismas reglas de filtrado. Así evitamos que la tabla y las gráficas interpreten de manera distinta una selección.

`construir_consulta` utiliza operadores de MongoDB: `$gte` y `$lte` delimitan años; `$or` busca en planeta o estrella. `re.escape` hace que los signos del texto se busquen literalmente, y la opción `i` permite ignorar mayúsculas.

Para mostrar páginas, calculamos:

```python
salto = (pagina - 1) * por_pagina
```

Si pedimos la página 3 con 25 registros, saltamos 50. `find` consulta, `sort` ordena, `skip` omite los anteriores y `limit` limita la respuesta. `count_documents` cuenta todas las coincidencias.

En `estadisticas`, `aggregate` ejecuta operaciones en MongoDB: `$match` filtra, `$group` agrupa y `$sum: 1` cuenta documentos por grupo. Los cálculos específicos de las cuatro preguntas se realizan después con listas, diccionarios y funciones de Python. Pandas organiza la presentación en el dashboard. Las estadísticas usan toda la selección, aunque la tabla solo muestre una página.

## 5. Cómo se valida y guarda un registro

`NuevoRegistro` hereda de `BaseModel`: describe los campos esperados. `Field` establece condiciones, como texto obligatorio o magnitudes mayores que cero. `float | None` permite un número decimal o ausencia de dato; `Literal[-1, 0, 1]` limita los indicadores a esas opciones.

`ConfigDict` configura reglas comunes: eliminar espacios exteriores, rechazar campos desconocidos y no aceptar números infinitos ni NaN. `field_validator` añade la comprobación de booleanos, porque `True` y `False` no representan mediciones. El validador recibe el valor antes de su conversión.

`crear_registro` busca primero si el nombre ya existe. `registro.model_dump()` convierte el objeto validado en un diccionario. Después adapta los nombres al esquema de la colección, fija la procedencia manual y llama a `insert_one`.

Una creación correcta devuelve `201`; un duplicado, `409`; un dato inválido, `422`; un problema de disponibilidad de MongoDB, `503`. `HTTPException` permite detener una operación con un estado y mensaje concretos. Los manejadores escritos con `async def` son funciones de respuesta que FastAPI ejecuta cuando corresponde.

## 6. Mapa de dashboard.py

| Función | Qué hace |
|---|---|
| `pedir_api` | Envía GET o POST, interpreta JSON y muestra errores. |
| `numero` | Presenta cifras legibles y muestra “Sin dato” cuando corresponde. |
| `preparar_tabla` | Aplana la respuesta y cambia nombres de columnas para mostrarlas. |
| `mostrar_preguntas` | Presenta las cuatro preguntas con tablas, barras y explicaciones. |
| `mostrar_catalogo` | Solicita una página, muestra sus documentos y permite descargarla. |
| `campo_medida` | Crea un control numérico opcional y su indicador. |
| `mostrar_formulario` | Recoge datos, revisa condiciones básicas y envía el POST. |

`pedir_api` utiliza `params=...` para los filtros de un GET y `json=...` para el cuerpo del POST. `respuesta.json()` interpreta la respuesta como datos de Python. Si falla la conexión o llega un error, devuelve `None` y muestra un mensaje.

`pd.json_normalize` convierte el objeto anidado `fuente` en columnas como `fuente.nombre`. Los títulos visibles cambian, pero los nombres usados para enviar solicitudes siguen el contrato de la API.

## 7. Por qué Streamlit vuelve a ejecutar el archivo

Al interactuar con controles, Streamlit vuelve a recorrer el programa. `st.session_state` conserva filtros, página y mensajes entre ejecuciones de la sesión. Cada `key` identifica un control o un dato; sus nombres deben ser distintos cuando representan cosas diferentes.

`st.form` reúne entradas para enviarlas al pulsar el botón. Después de crear, guardamos el nombre nuevo en el estado y ejecutamos `st.rerun()`. Al comenzar otra vez, se aplican los filtros de nombre y procedencia manual antes de dibujar los controles. Así puede comprobarse el registro recién guardado.

`st.stop()` detiene esa ejecución si falta una respuesta necesaria. La interfaz ofrece reintentar en lugar de continuar con datos que no recibió.

## 8. Cómo leer y modificar sin perderse

Usa **cuatro espacios por nivel** y conserva la alineación dentro de funciones, condiciones, ciclos y bloques `with`. El sangrado determina qué instrucciones pertenecen a cada bloque.

Una expresión `[... for ...]` construye una lista recorriendo elementos. `lambda` define una función pequeña para ordenar por un campo. `**magnitudes` incorpora las entradas de ese diccionario en otro. `diccionario.get(clave)` permite consultar una clave que puede faltar.

Practica primero este recorrido: `mostrar_catalogo` → `pedir_api` → `listar_datos` → `construir_consulta` → `normalizar`. Después sigue la creación: `mostrar_formulario` → `NuevoRegistro` → `crear_registro`. Finalmente revisa los cálculos de `estadisticas`, comparándolos con los criterios del segundo corte.
