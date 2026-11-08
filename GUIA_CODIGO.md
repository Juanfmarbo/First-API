# Guía para entender el código

Lee el proyecto siguiendo el recorrido de una solicitud. Primero comprende qué recibe cada función y qué devuelve; después revisa sus condiciones y ciclos. Esta guía corresponde a `api.py` y `dashboard.py` de esta versión.

## Ejecución local y servicios publicados

El mismo `api.py` se ejecuta ahora en Render en [https://exoplanetas-api-juanfmarbo.onrender.com](https://exoplanetas-api-juanfmarbo.onrender.com). Render proporciona las variables privadas de MongoDB al proceso; no necesita el `.env` del Mac. En local, Uvicorn utiliza el puerto 8000; en Render, el comando de inicio utiliza el puerto asignado mediante `$PORT`.

`dashboard.py` obtiene la dirección del backend de `API_BASE_URL`. Puede utilizar una API local o la URL pública de Render sin cambiar sus funciones. La interfaz está publicada en [https://exoplanetasproyecto.streamlit.app/](https://exoplanetasproyecto.streamlit.app/) y se verificaron consulta, filtros, paginación y creación mediante su formulario, con persistencia en Atlas. En Streamlit, la dirección del backend se configura en los secretos de nivel principal. El alcance de las pruebas está en `PRUEBAS_REALIZADAS.md`.

La ampliación del **8 de noviembre de 2026** incorpora Gemini. El backend lee `GEMINI_API_KEY` y `MODELO_IA` de su entorno; el modelo predeterminado es `gemini-3.6-flash`. Configurar la clave permite realizar la llamada real. Las pruebas anteriores del catálogo y el formulario no sustituyen la comprobación específica de la IA.

## 1. Dos archivos, dos responsabilidades

**`api.py`** contiene el backend: conecta con MongoDB, valida entradas, consulta documentos, calcula estadísticas y llama a Gemini. **`dashboard.py`** contiene la interfaz: recoge selecciones y preguntas, llama a la API y muestra resultados. El dashboard conoce la dirección del backend; la cadena privada de MongoDB y la clave de Gemini pertenecen a la API.

En el backend, `return` entrega un resultado que FastAPI convierte en una respuesta HTTP. Un `print` solo escribiría en la terminal y no entregaría los datos al dashboard.

## 2. Qué importamos y para qué

Las dependencias directas son las siete de `requirements.txt`. Pydantic se instala como dependencia de FastAPI y `certifi` como dependencia de `requests`. Este último también se utilizaba en el notebook del segundo corte.

| Importación o herramienta | Uso en este proyecto |
|---|---|
| `pymongo` | `MongoClient` conecta con MongoDB; sus excepciones permiten manejar fallas. |
| `certifi` | `where()` devuelve la ruta al archivo de certificados de confianza usado al conectar con Atlas mediante una URI SRV. |
| `fastapi` | Define rutas, recibe parámetros, comparte filtros y genera respuestas. |
| `pydantic` | `BaseModel`, `Field` y validadores describen las reglas de los registros y las preguntas. |
| `requests` | Envía solicitudes desde el dashboard a FastAPI y desde FastAPI a Gemini. |
| `pandas` | Convierte respuestas en tablas y prepara los datos para mostrarlos. |
| `streamlit` | Construye controles, tablas, mensajes y gráficas. |
| `python-dotenv` | `load_dotenv` carga la configuración local. |
| `uvicorn` | Se utiliza en el comando que ejecuta el backend. |

Los demás módulos vienen con Python: `os` lee variables de entorno; `Path` localiza archivos; `datetime` obtiene el año actual; `math` comprueba números finitos y redondea páginas hacia arriba; `statistics.median` calcula medianas; `re` prepara búsquedas de texto; `Literal` limita las opciones permitidas; `json` convierte el contexto de la IA en texto JSON. No requieren nuevas instalaciones.

## 3. Mapa de api.py

El archivo está dividido en configuración, preparación de datos, filtros, rutas de lectura, creación y preguntas de IA.

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
| `Pregunta`, `preguntar` | Validan la pregunta, preparan el contexto de la selección, llaman a Gemini y comprueban su respuesta. |
| `registro_para_ia` | Selecciona los campos científicos y su fuente, omitiendo identificadores internos y referencias largas. |
| `extraer_respuesta_ia` | Reconoce bloqueos, respuestas incompletas y partes de texto final antes de mostrarlas. |
| `datos_invalidos`, `error_mongodb` | Devuelven errores comprensibles sin exponer la conexión privada. |

`obtener_coleccion` conserva una conexión reutilizable en `cliente`. Si se indica una colección, la respeta. En caso contrario busca las colecciones conocidas. El diccionario `ALIAS_CLASE` traduce, por ejemplo, `metodo` a `metodo_descubrimiento` al responder; no reescribe la colección original.

Para una URI que empieza por `mongodb+srv://`, la variable `certificados` contiene la ruta que devuelve `certifi.where()`. `tlsCAFile` indica a `MongoClient` dónde están esos certificados de confianza. Esto conserva el ajuste de conexión del notebook y mantiene la validación del servidor. Con una URI local `mongodb://`, el valor queda en `None` y se conservan sus opciones originales.

MongoDB utiliza un identificador `_id` que puede ser un `ObjectId`. `str(...)` lo convierte a texto para incluirlo en JSON. En Python, `None` significa dato ausente; en JSON se representa como `null`. Esa ausencia se conserva y no se transforma en cero.

## 4. Cómo funciona una consulta

`@app.get("/datos")` registra la función situada debajo para atender esa ruta. El decorador relaciona una dirección HTTP con una función Python.

`Query` describe los parámetros de la URL y sus reglas. Por ejemplo, `ge=1` significa mayor o igual que uno; `le=200`, menor o igual que doscientos. FastAPI valida esos límites antes de ejecutar la consulta.

`Depends(recibir_filtros)` indica a FastAPI que ejecute esa función y entregue su diccionario a la ruta. `/datos`, `/estadisticas` y `/preguntar` reciben las mismas reglas de filtrado. Así la tabla, las gráficas y el contexto de la IA parten de la misma selección.

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
| `mostrar_ia` | Recoge la pregunta, envía los filtros a `/preguntar` y conserva la respuesta en la sesión. |

`pedir_api` utiliza `params=...` para enviar filtros tanto en GET como en POST y `json=...` para el cuerpo del POST. El argumento `espera` vale `20` por defecto; `mostrar_ia` utiliza `espera=60`. Ese valor se entrega al `timeout` de `requests`. `respuesta.json()` interpreta la respuesta como datos de Python. Si falla la conexión o llega un error, devuelve `None` y muestra un mensaje.

`pd.json_normalize` convierte el objeto anidado `fuente` en columnas como `fuente.nombre`. Los títulos visibles cambian, pero los nombres usados para enviar solicitudes siguen el contrato de la API.

## 7. Por qué Streamlit vuelve a ejecutar el archivo

Al interactuar con controles, Streamlit vuelve a recorrer el programa. `st.session_state` conserva filtros, página y mensajes entre ejecuciones de la sesión. Cada `key` identifica un control o un dato; sus nombres deben ser distintos cuando representan cosas diferentes.

`st.form` reúne entradas para enviarlas al pulsar el botón. Después de crear, guardamos el nombre nuevo en el estado y ejecutamos `st.rerun()`. Al comenzar otra vez, se aplican los filtros de nombre y procedencia manual antes de dibujar los controles. Así puede comprobarse el registro recién guardado.

`st.stop()` detiene esa ejecución si falta una respuesta necesaria. La interfaz ofrece reintentar en lugar de continuar con datos que no recibió.

## 8. Cómo funciona la ampliación de Gemini

### Validar una pregunta

`Pregunta` hereda de `BaseModel`, igual que el modelo de los registros. Su campo `pregunta` debe ser texto, tener contenido después de quitar espacios exteriores y no superar 1.000 caracteres. Esto también se comprueba cuando la solicitud viene de `/docs` o de otro cliente.

`@app.post("/preguntar")` asocia la ruta con la función `preguntar`. El cuerpo JSON lleva la pregunta y la URL lleva los filtros. Que sea un `POST` no implica que siempre se inserte un documento: en esta ruta se pide al servidor que procese una pregunta.

### Preparar el contexto

La API reutiliza `estadisticas(filtros)` para obtener las respuestas numéricas de toda la selección. También reutiliza `listar_datos` para obtener una muestra de hasta 30 registros. Son llamadas a funciones del mismo archivo, por lo que el backend no necesita hacerse otra solicitud HTTP a sí mismo. `registro_para_ia` prepara los registros de la muestra y los candidatos cercanos: conserva los campos científicos, la procedencia y las distancias calculadas, y omite los identificadores internos y las referencias largas.

El contexto incluye la descripción del proyecto, los criterios de sus cuatro preguntas, el resumen y la muestra. `json.dumps` convierte los diccionarios y listas en un texto organizado que se puede incluir en la solicitud a Gemini. `None` se representa como `null` y mantiene su significado de dato desconocido.

La distinción entre resumen y muestra es esencial: contar candidatos dentro de 30 ejemplos no responde cuántos hay en toda una colección. El resumen ya contiene el cálculo completo. Para un dato que no está en el contexto, la instrucción pide reconocer esa limitación.

### Llamar a otra API REST

`os.environ` u `os.getenv` permiten leer `GEMINI_API_KEY` y `MODELO_IA` sin escribir credenciales en el código. `MODELO_IA` tiene como valor predeterminado `gemini-3.6-flash`, el modelo utilizado en clase.

La dirección de la llamada termina en `models/{MODELO_IA}:generateContent`. `requests.post` envía un cuerpo JSON siguiendo el [contrato REST de Gemini](https://ai.google.dev/api/generate-content?hl=en):

- `systemInstruction` contiene las instrucciones para responder con los datos y reconocer sus límites.
- `contents` contiene el contexto y la pregunta del usuario. Dentro, `parts` agrupa las partes del mensaje y `text` contiene el texto.
- `generationConfig` fija `maxOutputTokens=4096`, un límite para la generación. Un token es una unidad de texto que usa el modelo; no equivale necesariamente a una palabra.

La cabecera `x-goog-api-key` lleva la clave; la URL no necesita contenerla. El backend configura `timeout=30` al llamar a Google. En `requests`, este parámetro controla esperas de conexión y lectura; no garantiza que toda la operación dure exactamente 30 segundos como máximo. La [documentación de Requests](https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts) explica esta diferencia.

La API comprueba la respuesta antes de acceder a su texto. Google puede devolver un error HTTP, una respuesta sin candidatos o contenido bloqueado. `extraer_respuesta_ia` revisa esos campos y el motivo por el que terminó la generación. Cuando hay partes de texto utilizables, se unen para formar la respuesta; las partes marcadas como razonamiento no se muestran. Los errores se describen con mensajes propios, sin copiar excepciones o respuestas completas que puedan revelar información de configuración.

Una respuesta correcta devuelve `respuesta`, `modelo`, `total_registros` y `tamano_muestra`. Los estados de error permiten distinguir situaciones: `422` para una pregunta inválida o un bloqueo del prompt comunicado por Google, `503` si falta configurar la clave o Google rechaza la configuración con `400`, `401`, `403` o `404`, `429` por cuota, `504` por tiempo de espera y `502` si falla la llamada o la respuesta no es utilizable.

### Mostrar y conservar la respuesta

El formulario de Streamlit envía la pregunta solo al pulsar **Preguntar**. La petición al backend configura `timeout=60` para dejar más margen a la lectura de datos y la generación. Durante la consulta se muestra un indicador de espera. Este valor conserva el significado de espera de conexión y lectura de `requests`.

La respuesta se conserva en `st.session_state`. Así una nueva ejecución de la pantalla no necesita llamar de nuevo a Gemini automáticamente. Se limpia al aplicar filtros, pulsar **Actualizar datos** o seleccionar automáticamente un registro recién creado. Esto permite volver a preguntar sobre la selección o los datos actuales. Cambiar la página del catálogo no cambia el conjunto que usa la IA: sus estadísticas corresponden a toda la selección.

Esta ampliación usa las mismas siete dependencias del proyecto. La llamada a Gemini consulta y explica; no inserta registros en MongoDB ni ejecuta código producido por el modelo. Las cifras de una respuesta deben contrastarse con los indicadores y las tablas.

## 9. Cómo leer y modificar sin perderse

Usa **cuatro espacios por nivel** y conserva la alineación dentro de funciones, condiciones, ciclos y bloques `with`. El sangrado determina qué instrucciones pertenecen a cada bloque.

Una expresión `[... for ...]` construye una lista recorriendo elementos. `lambda` define una función pequeña para ordenar por un campo. `**magnitudes` incorpora las entradas de ese diccionario en otro. `diccionario.get(clave)` permite consultar una clave que puede faltar.

Practica primero este recorrido: `mostrar_catalogo` → `pedir_api` → `listar_datos` → `construir_consulta` → `normalizar`. Después sigue la creación: `mostrar_formulario` → `NuevoRegistro` → `crear_registro`. Revisa los cálculos de `estadisticas`, comparándolos con los criterios del segundo corte. Para Gemini, sigue el formulario de pregunta → `POST /preguntar` → `Pregunta` → resumen y muestra → `requests.post` a Google → respuesta visible.
