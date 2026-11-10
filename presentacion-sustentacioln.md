# Presentación y sustentación: First-API, explorador de exoplanetas

**Documento de estudio y defensa del proyecto de Programación Aplicada.** Explica qué construimos, por qué elegimos cada herramienta, cómo funciona el código y cómo demostrarlo. El nombre del archivo se conserva como `presentacion-sustentacioln.md`; reúne la explicación técnica, el despliegue y la evidencia que antes estaban repartidos entre varias guías.

La explicación corresponde al código de [api.py](api.py) y [dashboard.py](dashboard.py), versión de API **1.1.0**. La documentación se reorganizó el **10 de noviembre de 2026**. Las verificaciones de funcionamiento que se citan conservan sus fechas originales; escribir este documento no constituye una nueva prueba de los servicios públicos.

## Índice

1. [Proyecto, alcance y forma de estudiarlo](#proyecto).
2. [Arquitectura y decisiones de diseño](#arquitectura).
3. [Datos, unidades y significado de los campos](#datos).
4. [API: recorrido completo del backend](#api).
5. [Dashboard: ejecución, filtros, gráficas y formulario](#dashboard).
6. [Gemini: contexto, solicitud, respuesta y límites](#gemini).
7. [Instalación, configuración y despliegue](#despliegue).
8. [Verificación y diagnóstico](#verificacion).
9. [Correspondencia con la rúbrica](#rubrica).
10. [Guion para presentar y demostrar](#guion).
11. [Preguntas del profesor y respuestas razonadas](#preguntas).
12. [Glosario y comprobación de comprensión](#glosario).

<a id="proyecto"></a>

## 1. Proyecto, alcance y forma de estudiarlo

### Qué problema resuelve

El segundo corte produjo datos de exoplanetas preparados para analizarlos. Este proyecto permite consultar ese trabajo desde una aplicación: una persona abre una página, selecciona filtros, interpreta resultados y registra una captura manual sin escribir consultas de MongoDB. Un exoplaneta es un planeta exterior a nuestro sistema solar; el catálogo contiene nombres, medidas, métodos de descubrimiento y procedencia.

El programa conserva cuatro preguntas de análisis:

| Pregunta | Qué produce el programa | Qué debemos interpretar con cuidado |
|---|---|---|
| ¿Cuántos planetas parecidos a la Tierra conocemos? | Cuenta los que cumplen los intervalos de radio e insolación y calcula su proporción entre los evaluables. | Parecido bajo dos criterios no equivale a habitabilidad demostrada. |
| ¿Qué tan lejos están y cuánto tardaríamos en llegar? | Ordena candidatos con distancia conocida y calcula años luz y viaje idealizado. | El viaje usa velocidad constante de 17 km/s, sin modelar una misión real. |
| ¿Qué tan lejos puede “ver” cada método? | Compara mínimo, mediana y máximo de las distancias registradas por método. | Describe observaciones del conjunto; no mide por sí solo el límite de un instrumento. |
| ¿Qué tan extremos pueden ser los planetas? | Evalúa temperatura, período y masa bajo reglas explícitas y cuenta casos por método. | Los denominadores varían y un mismo planeta puede cumplir varias categorías. |

El proyecto final agrega una API de lectura y escritura, un dashboard, despliegue público y preguntas mediante Gemini. No vuelve a ejecutar automáticamente la descarga y limpieza del segundo corte: consulta la colección que ya quedó en Atlas. El repositorio actual contiene la aplicación y su configuración; no contiene una copia completa del catálogo ni un proceso periódico de actualización desde NASA.

### Qué significa que el proyecto esté completo

Para defenderlo no basta mostrar una gráfica. Debemos demostrar que la pantalla consume una API, que la API consulta datos persistentes, que los filtros cambian correctamente el análisis, que el POST valida y guarda y que podemos explicar las decisiones. La IA constituye una ampliación: añade generación de explicaciones a partir de contexto, y tiene su propia configuración y sus propias comprobaciones.

Esta aplicación implementa **lectura y creación**. No contiene rutas para editar ni borrar planetas, cuentas de usuario, autenticación o un sistema de permisos. Por ello es preciso describirla como una aplicación académica de consulta y captura, no como un CRUD completo o un sistema de producción con administración de usuarios.

### Cómo estudiar este documento

Haz una primera lectura de arquitectura, datos y guion para entender el recorrido general. En la segunda, abre el archivo Python correspondiente y sigue las funciones descritas. En la tercera, practica la demostración y responde las preguntas finales con tus propias palabras.

Los fragmentos de código explican la implementación existente. Cuando un ejemplo usa registros inventados, se identifica como hipotético o sintético. No hay que pegar todos los fragmentos como un programa nuevo: algunas partes son extractos y dependen de variables definidas en el archivo completo. Las cifras históricas tampoco se deben memorizar como totales permanentes de una colección que admite escrituras.

<a id="arquitectura"></a>

## 2. Arquitectura y decisiones de diseño

### Qué ejecuta cada parte

```mermaid
flowchart TD
    U["Persona en el navegador"] --> S["Streamlit: dashboard.py"]
    S -->|"HTTP: GET y POST"| A["FastAPI: api.py"]
    A -->|"PyMongo: consulta e inserción"| M["MongoDB Atlas"]
    A -->|"REST: contexto y pregunta"| G["API de Gemini"]
    M -->|"Documentos y agregaciones"| A
    G -->|"Texto generado"| A
    A -->|"JSON y código de estado"| S
    S -->|"Tablas, gráficas y mensajes"| U
```

**Frontend** significa la parte con la que interactúa la persona. En este proyecto es Streamlit: el navegador presenta la interfaz, pero `dashboard.py` se ejecuta en un proceso Python, localmente o en Streamlit Cloud. Las llamadas de `requests` salen de ese proceso, no de un archivo JavaScript que hayamos programado en el navegador.

**Backend** significa la parte que atiende solicitudes y aplica las reglas. FastAPI recibe los parámetros, valida entradas, construye las consultas, prepara las estadísticas y decide qué resultado devuelve. Uvicorn mantiene el servidor escuchando conexiones y ejecuta la aplicación FastAPI.

**Base de datos** significa almacenamiento persistente. Atlas aloja MongoDB; PyMongo es la biblioteca que permite utilizarlo desde Python. Un cluster es la infraestructura que aloja bases; una base contiene colecciones; una colección contiene documentos. En nuestro caso la base predeterminada es `proyecto_segundo_corte` y la colección final utilizada en las comprobaciones es `exoplanetas_presentacion`.

**Servicio externo de IA** significa que Google ejecuta el modelo. Nuestro backend realiza una solicitud a ese servicio y recibe una respuesta. La API de Gemini es distinta de nuestra API FastAPI. Cuando decimos que “la aplicación consume dos APIs”, conviene especificar quién las consume: Streamlit consume la del proyecto, y el backend consume la de Gemini.

### Por qué lo organizamos así

| Decisión | Necesidad que resuelve | Consecuencia visible en el código |
|---|---|---|
| Separar `api.py` y `dashboard.py` | Mantener una misma fuente de reglas para diferentes clientes. | Swagger, Streamlit y Gemini reutilizan la lógica del backend. |
| Usar FastAPI | Declarar rutas, tipos, validación y documentación con Python. | Decoradores `@app.get` y `@app.post`, modelos y `/docs`. |
| Ejecutar con Uvicorn | Disponer de un servidor que escuche peticiones. | Comando `python -m uvicorn api:app`. |
| Conservar MongoDB y PyMongo | Continuar con los documentos del segundo corte. | Consultas, agregaciones e `insert_one` sobre la colección existente. |
| Normalizar al devolver datos | Admitir nombres de columnas usados en distintas versiones. | El dashboard recibe un formato uniforme aunque los nombres guardados difieran. |
| Usar Streamlit | Construir la interfaz con las herramientas de Python vistas en clase. | Widgets, pestañas, formularios y gráficas nativas. |
| Usar pandas en la interfaz | Convertir JSON en tablas fáciles de seleccionar, ordenar y exportar. | `DataFrame`, `json_normalize`, selección de columnas y CSV. |
| Usar `requests` para HTTP | Trabajar con el mismo mecanismo de comunicación en dashboard e IA. | `params` para filtros y `json` para cuerpos de solicitudes. |
| Separar configuración y código | Cambiar destinos y credenciales según dónde se ejecute. | Variables de entorno y plantilla `.env.example`. |
| Conservar valores desconocidos | Evitar conclusiones basadas en medidas inventadas. | `None`/`null`, indicadores de límite y conteos de evaluables. |

La separación no elimina todas las limitaciones: las estadísticas se calculan leyendo la selección en memoria, y una petición de IA puede tardar por la red y el proveedor. Para el alcance del curso, la prioridad es que cada paso sea comprensible y demostrable. No se añadieron frameworks de frontend, bases vectoriales ni bibliotecas de agentes.

### Qué significa un recorrido completo

Cuando aplicamos un filtro por `Transit`, Streamlit transforma la selección del widget en parámetros HTTP. FastAPI los valida y los convierte en condiciones MongoDB. MongoDB entrega registros o agregaciones; la API prepara un diccionario, FastAPI lo serializa como JSON y Streamlit lo convierte en una tabla o una gráfica.

Cuando guardamos un registro, Streamlit crea un diccionario con los campos del formulario y lo envía como JSON por POST. Pydantic valida; el backend determina la fuente manual e inserta; MongoDB asigna un identificador; la API devuelve `201` y el documento; Streamlit muestra la confirmación y vuelve a consultar. Consultar de nuevo es lo que permite comprobar persistencia, más allá de mostrar un mensaje optimista en pantalla.

<a id="datos"></a>

## 3. Datos, unidades y significado de los campos

### Un documento no es una fila de texto sin estructura

Un documento MongoDB contiene pares de nombre y valor. Algunos valores son textos, otros números, otros objetos anidados. En Python lo trabajamos normalmente como un diccionario. La API devuelve JSON, donde `null` representa un valor desconocido y los objetos y listas mantienen esa estructura.

El siguiente ejemplo es **sintético**, útil para reconocer la forma de un registro, no una observación astronómica real:

```json
{
  "planeta": "DEMO-EXOPLANETA-001",
  "estrella": "Estrella de demostración",
  "metodo_descubrimiento": "Transit",
  "anio_descubrimiento": 2026,
  "radio_tierras": 1.2,
  "limite_radio": 0,
  "insolacion_tierra": 1.0,
  "limite_insolacion": 0,
  "distancia_sistema_parsec": 10.0,
  "temperatura_planeta_k": null,
  "fuente": {
    "nombre": "Registro manual del proyecto"
  }
}
```

En este ejemplo `fuente` es un objeto dentro de otro objeto. Para filtrar su nombre en MongoDB se utiliza `fuente.nombre`. El ejemplo representa un registro ya identificado por procedencia; **no se envía `fuente` al POST**, porque el servidor la establece y el modelo de entrada no admite ese campo adicional.

### Diccionario de campos que utiliza la aplicación

Las unidades siguientes son las que conserva el esquema del proyecto. Las definiciones originales se pueden contrastar en el [diccionario oficial de columnas de NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html).

| Campo | Tipo o unidad | Papel en el proyecto |
|---|---|---|
| `_id` | Identificador, presentado como texto | Permite reconocer el documento guardado y desempatar el orden del catálogo. |
| `planeta` | Texto | Nombre utilizado para mostrar, buscar y comprobar duplicados. |
| `estrella` | Texto | Nombre de la estrella o sistema asociado; también participa en la búsqueda. |
| `metodo_descubrimiento` | Texto | Filtro y agrupaciones por método. |
| `anio_descubrimiento` | Entero | Filtros por años y distribución temporal. |
| `lugar_descubrimiento` | Texto o desconocido | Información adicional presentada en el catálogo. |
| `radio_tierras` | Radios terrestres | Uno de los dos criterios de candidato. |
| `insolacion_tierra` | Flujo relativo al terrestre | Segundo criterio de candidato. |
| `distancia_sistema_parsec` | Parsecs | Cercanía, conversión de unidades y comparación por método. |
| `temperatura_planeta_k` | Kelvin | Categorías térmicas. En registros NASA procede de `pl_eqt`, no de una medición general de la superficie. |
| `periodo_orbital_dias` | Días | Categoría Relámpago. |
| `masa_tierras` | Masas terrestres | Categoría Supergigante. |
| `densidad_planeta` | g/cm³ | Dato adicional de consulta. |
| `tipo_masa` | Texto o desconocido | Conserva la descripción de la procedencia/tipo de masa del catálogo. |
| `referencia_radio` | Texto o desconocido | Conserva la referencia y permite reconocer valores identificados como calculados por el archivo. |
| `limite_radio` | `-1`, `0`, `1` o desconocido | Indica cómo interpretar el radio. |
| `limite_insolacion` | Igual convención | Indica cómo interpretar la insolación. |
| `limite_temperatura` | Igual convención | Indica cómo interpretar la temperatura. |
| `limite_periodo` | Igual convención | Indica cómo interpretar el período. |
| `limite_masa` | Igual convención | Indica cómo interpretar la masa. |
| `fuente.nombre` | Texto anidado | Distingue procedencia NASA y registro manual. |
| `fuente.tabla` | Texto anidado cuando existe | Conserva la referencia a la tabla de origen. |

`pl_eqt` corresponde a una temperatura de equilibrio modelada; para imagen directa el catálogo contempla temperatura efectiva. Por eso el análisis térmico excluye `Imaging`. No debemos presentar este campo como una lectura de temperatura superficial ni olvidar esa diferencia física. La [definición oficial de NASA](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html) explica la distinción.

Los campos `distancia_anios_luz`, `viaje_anios` y `origen_radio` son resultados añadidos para análisis concretos. No hay que suponer que todos están almacenados originalmente en MongoDB. La API los obtiene cuando prepara la respuesta correspondiente.

### Dato desconocido, valor puntual y límite

En el esquema del proyecto, `0` en un indicador significa valor puntual; `1`, límite superior; `-1`, límite inferior; `None` o `null`, información desconocida. Esto se refiere al **indicador**, no al valor de la medida. Un radio igual a cero no es aceptable aunque el indicador de radio sea `0`.

Si un radio tiene límite superior, sabemos que el valor real no supera el límite informado; no podemos tratar ese número como una medición puntual para decidir que cae dentro de un intervalo. Por eso las preguntas exigen el indicador `0` donde corresponde. Un indicador desconocido no se convierte automáticamente en `0`.

Tampoco son equivalentes “no cumple” y “no se puede evaluar”. Entre los registros evaluables, si el radio o la insolación quedan fuera de su intervalo, el planeta no cumple ambos criterios. Si falta una medida o su indicador, la aplicación lo clasifica como información insuficiente, incluso si otra medida conocida queda fuera del intervalo. La API cuenta esos grupos por separado. Esa decisión protege el significado de los porcentajes.

### Procedencia, selección y alcance

La fuente manual se fija en el servidor. Un registro que acabamos de escribir no se convierte en un descubrimiento NASA por usar un nombre real o por rellenar medidas. Para una exposición de resultados científicos seleccionamos **Solo catálogo NASA**; para mostrar escritura seleccionamos o buscamos los registros manuales.

Los filtros se aplican antes del cálculo. Si elegimos un método o un período, cambian los documentos elegibles, los totales y los denominadores. Si activamos **Solo candidatos**, la selección ya está restringida por esos criterios; no debemos leer su porcentaje como si describiera todo el catálogo.

Cada capítulo siguiente sigue el mismo principio: primero explica qué información entra, después qué transformación hace el código y finalmente cómo interpretar la salida.

<a id="api"></a>

## 4. API: recorrido completo del backend

### La API: qué hace y cómo debemos explicarla

La API es el programa que recibe solicitudes, consulta MongoDB, aplica las reglas del proyecto y entrega respuestas estructuradas. Su implementación está en [api.py](api.py). El dashboard pide información a esta API; la API decide cómo buscarla y calcularla. MongoDB conserva los documentos. Esta separación permite que una misma regla científica se use en la tabla, en las estadísticas y en el contexto enviado a la IA.

Una API es una interfaz para comunicarse con un programa. En nuestro caso usamos HTTP, el protocolo de solicitudes y respuestas que también emplean los sitios web. Cada solicitud indica un **método** y una **ruta**. Por ejemplo, `GET /datos` consulta registros, mientras que `POST /datos` recibe un registro nuevo. Aunque compartan ruta, son operaciones diferentes porque cambia el método. Este proyecto implementa lectura y creación; no contiene rutas para editar ni eliminar planetas.

Los resultados viajan como JSON: un formato de texto que representa objetos, listas, cadenas, números, valores lógicos y ausencia de información. En Python trabajamos con diccionarios y listas; FastAPI los convierte en respuestas JSON. No enviamos al navegador el objeto de conexión de MongoDB ni ejecutamos Python dentro del JSON. En una sustentación podemos decir: “La API transforma una petición del usuario en una consulta o un cálculo, y devuelve datos que el dashboard puede presentar”.

#### Conceptos de Python que aparecen continuamente

Un `dict` o diccionario guarda pares de clave y valor: `{"planeta": "Ejemplo", "radio_tierras": 1.1}`. Accedemos con `planeta["radio_tierras"]` si esperamos que la clave exista. Usamos `.get("campo", valor_por_defecto)` cuando el documento podría no contenerla. Una `list` o lista reúne elementos ordenados: resultados, nombres de campos o etapas de una agregación.

`str` significa texto; `int`, número entero; `float`, número con decimales; y `bool`, `True` o `False`. `None` representa ausencia de información en Python y se convierte en `null` en JSON. No significa cero. En JSON también cambian las mayúsculas: los booleanos se escriben `true` y `false`.

Las anotaciones, como `pagina: int`, describen el tipo esperado. En las entradas gestionadas por FastAPI y Pydantic también sirven para interpretar y validar la solicitud. `str | None` admite texto o ausencia; `Literal["todos", "nasa", "manual"]` restringe las alternativas a esos tres valores.

`def` define una función; `return` entrega su resultado; `if` elige un camino; `for` recorre elementos; `and` exige varias condiciones y `or` admite alternativas. La indentación delimita qué instrucciones pertenecen a cada bloque. Por eso mantener cuatro espacios y bloques consistentes es parte de la corrección del programa.

#### FastAPI, Uvicorn y el registro de rutas

En `app = FastAPI(...)` creamos la aplicación. `title`, `description` y `version="1.1.0"` describen el proyecto en la documentación automática; no son credenciales ni seleccionan la versión instalada de Python.

Uvicorn es el servidor que atiende la conexión HTTP y ejecuta la aplicación. FastAPI define las rutas, interpreta las entradas y prepara las respuestas. Al ejecutar:

```bash
python -m uvicorn api:app --reload
```

`python -m` ejecuta el módulo instalado en ese intérprete; `uvicorn` es el servidor; `api` identifica `api.py`; y `app` identifica la variable que contiene la aplicación. `--reload` reinicia el proceso cuando cambiamos archivos durante el desarrollo. No significa que los datos de MongoDB se borren.

Un decorador conecta una función con un comportamiento del framework. Este fragmento real registra la entrada de la API:

```python
@app.get("/", tags=["Inicio"])
def inicio():
    """Presenta la API y las rutas que puede usar el dashboard."""
    return {
        "proyecto": "Exoplanetas de la NASA: ¿hay otras Tierras?",
        "documentacion": "/docs",
        "rutas": [
            "GET /salud", "GET /opciones", "GET /datos",
            "GET /estadisticas", "POST /datos", "POST /preguntar",
        ],
    }
```

La línea `@app.get` asocia el método GET y la ruta raíz con `inicio`. `tags` organiza la documentación. La función devuelve un diccionario que FastAPI serializa como JSON. Las comillas triples contienen una explicación de la función, llamada *docstring*. No son instrucciones que se ejecuten para consultar MongoDB.

La página `/docs` permite inspeccionar rutas, parámetros y cuerpos esperados. FastAPI obtiene esa información de las declaraciones del código y de los modelos. Las rutas de consulta y creación usan funciones normales `def`; los manejadores de errores usan `async def`. No debemos afirmar que todo el proyecto utiliza operaciones asíncronas: aquí PyMongo y `requests` se usan de forma síncrona. Véanse [api.py](api.py) y la documentación de [entradas de FastAPI](https://fastapi.tiangolo.com/tutorial/query-params/).

### Importaciones y configuración del backend

Los `import` incorporan funciones y clases que necesitamos. No todas las herramientas de `api.py` son librerías que debamos instalar por separado.

| Herramienta | Uso concreto en este archivo |
|---|---|
| `os` y `Path` | Leer variables de entorno y localizar el archivo de configuración junto a `api.py`. |
| `math` | Rechazar números no finitos y redondear hacia arriba el número de páginas. |
| `re` | Tratar literalmente los signos incluidos en nombres buscados. |
| `datetime` | Obtener el año usado como límite de validación. |
| `median` | Calcular la mediana de las distancias por método. |
| `Literal` | Definir conjuntos cerrados de valores permitidos. |
| `json` y `requests` | Preparar contexto y comunicarnos por HTTP con Gemini. |
| `load_dotenv` | Cargar configuración local desde `.env`. |
| `certifi` | Localizar certificados de confianza para la conexión TLS configurada. |
| `MongoClient` y errores de PyMongo | Consultar, agregar e insertar documentos, y reconocer fallos de base de datos. |
| Componentes de FastAPI | Registrar rutas, recibir parámetros, declarar dependencias y responder a errores. |
| Componentes de Pydantic | Definir y validar los cuerpos de entrada. |

`json`, `math`, `os`, `re`, `datetime`, `pathlib`, `statistics` y `typing` pertenecen a la biblioteca estándar. Las dependencias instaladas están declaradas en [requirements.txt](requirements.txt). Pydantic se incorpora con FastAPI y `certifi` con las dependencias de `requests`; no presentamos estas importaciones como tecnologías adicionales que hayamos implementado.

#### Variables de entorno y constantes

`load_dotenv(Path(__file__).with_name(".env"))` busca `.env` junto al archivo de la API. `__file__` identifica ese archivo; `Path` maneja su ruta; y `with_name` cambia el nombre conservando la carpeta. Así no dependemos únicamente de la carpeta desde la cual abrimos la terminal.

`os.getenv("MONGO_URI", "").strip()` lee una variable, usa texto vacío si falta y retira espacios exteriores. `MONGO_DB` tiene como valor predeterminado `proyecto_segundo_corte`; `MONGO_COLLECTION` puede quedar vacío para activar la selección automática. La URI contiene la información de conexión privada y no debe escribirse como ejemplo real en documentación pública.

`GEMINI_API_KEY` y `MODELO_IA` pertenecen a la integración de IA, explicada en su apartado. El nombre predeterminado de modelo que aparece en el archivo es una configuración del programa: su presencia no demuestra por sí sola disponibilidad, permisos o funcionamiento del servicio externo.

Las constantes científicas centralizan decisiones del proyecto:

| Constante | Valor del código | Para qué se usa |
|---|---:|---|
| `PARSEC_A_ANIOS_LUZ` | 3.26 | Conversión aproximada de distancias. |
| `VELOCIDAD_LUZ_KM_S` | 299792.458 | Relación entre años luz y tiempo de viaje. |
| `VELOCIDAD_VIAJE_KM_S` | 17 | Velocidad idealizada del ejercicio. |
| `UMBRAL_MASA_TIERRAS` | `13 * 317.8` | Umbral de 4131.4 masas terrestres usado para “Supergigante”. |
| `ANIO_ACTUAL` | `datetime.now().year` | Límite superior de años recibidos. |

El año se calcula al importar el módulo. Las constantes evitan repetir números dispersos y permiten explicar de dónde sale cada operación. Los conjuntos `CAMPOS_TEXTO`, `CAMPOS_NUMERICOS` y `CAMPOS_LIMITES` agrupan campos que comparten tratamiento; `TIPOS_EXTREMOS` define los cuatro nombres de clasificación. Todo ello se puede contrastar en [api.py](api.py).

### Conexión a MongoDB y reconocimiento de la colección

#### Por qué el cliente comienza en `None`

La variable global `cliente` comienza como `None`. La función `obtener_coleccion()` crea `MongoClient` cuando alguna operación necesita la base de datos y reutiliza ese cliente después. Esto permite abrir `/` y `/docs` aunque todavía falte configurar la conexión. Que estas páginas abran no demuestra que MongoDB esté disponible.

Dentro de la función, `global cliente` indica que vamos a asignar la variable del módulo. Sin esa declaración, una asignación crearía una variable local y no conservaríamos esa referencia de la misma manera entre llamadas.

Primero comprobamos `MONGO_URI` y `MONGO_DB`. Si falta alguno, lanzamos `HTTPException` con estado 503 y un mensaje de configuración. `raise` interrumpe el flujo normal de la solicitud; no continúa hasta consultar una conexión inexistente.

El bloque real de creación es:

```python
if cliente is None:
    certificados = certifi.where() if MONGO_URI.startswith("mongodb+srv://") else None
    cliente = MongoClient(
        MONGO_URI,
        tlsCAFile=certificados,
        serverSelectionTimeoutMS=8000,
        connectTimeoutMS=8000,
        socketTimeoutMS=15000,
    )
```

La primera línea evita crear de nuevo el cliente en cada solicitud ordinaria. La segunda usa el archivo de autoridades certificadoras de `certifi` para la URI SRV configurada. `tlsCAFile` permite verificar la confianza del certificado del servidor. No desactiva la verificación TLS ni convierte a `certifi` en una base de datos intermediaria.

Los tres tiempos están expresados en milisegundos: 8000 para seleccionar servidor, 8000 para establecer una conexión y 15000 para operaciones de socket. Son límites de etapas diferentes; no deben sumarse y presentarse como un tiempo total garantizado de cualquier petición.

Esta configuración aborda la confianza en certificados que puede variar entre instalaciones, incluidas instalaciones de Python en macOS. No significa que MongoDB sea incompatible con Mac. El comportamiento de `MongoClient` se documenta en [MongoDB](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/mongoclient/).

#### Cómo elegimos base, colección y esquema

`base = cliente[MONGO_DB]` obtiene una referencia a la base; `base[nombre]` obtiene una referencia a una colección. Esto no copia todos sus documentos a Python.

Si `MONGO_COLLECTION` tiene un nombre, lo usamos directamente. Si está vacío, buscamos una colección con algún documento en este orden:

1. `exoplanetas_presentacion`.
2. `exoplanetas_clase`.
3. `exoplanetas`.

`find_one()` permite examinar un documento. Si ninguna opción automática contiene datos, respondemos 503. Una colección configurada explícitamente puede estar vacía: el programa puede reconocer su referencia y después recibir una captura manual.

El primer documento también permite comprobar que la estructura es plana: debe contener `planeta` y ese campo no debe ser otro diccionario. Posteriormente reconocemos tres nombres de esquema: `final`, `clase` o `borrador`. Si aparece `metodo` y falta `metodo_descubrimiento`, reconocemos el esquema de clase. También contemplamos una colección de clase vacía por su nombre. Para la colección `exoplanetas`, la ausencia de `limite_radio` identifica el borrador en el caso previsto.

Esto es una detección a partir de una muestra, no una validación exhaustiva de todos los documentos. Una colección con esquemas mezclados podría necesitar revisión. La API no ejecuta una migración ni renombra automáticamente los campos guardados.

El diccionario `ALIAS_CLASE` relaciona los nombres públicos con los nombres cortos:

| Nombre usado por la API | Nombre del esquema de clase |
|---|---|
| `metodo_descubrimiento` | `metodo` |
| `anio_descubrimiento` | `anio` |
| `lugar_descubrimiento` | `lugar` |
| `distancia_sistema_parsec` | `distancia_pc` |
| `temperatura_planeta_k` | `temperatura_k` |
| `periodo_orbital_dias` | `periodo_dias` |
| `densidad_planeta` | `densidad` |

La función devuelve `coleccion, campos, esquema`. Al recibirlos en tres variables hacemos un desempaquetado: separamos los tres componentes del resultado. `campos` permite consultar el nombre almacenado y entregar siempre nombres públicos consistentes. Así el dashboard no necesita duplicar su lógica para cada versión del segundo corte.

### Normalización: preparar documentos sin inventar información

#### `numero_positivo` y `anio_valido`

`numero_positivo(valor)` acepta únicamente enteros o decimales mayores que cero y finitos. Rechaza `True` y `False` antes de revisar el tipo numérico, porque en Python los booleanos tienen una relación especial con los enteros. No sería correcto interpretar `True` como un radio de una Tierra.

`math.isfinite` excluye infinito, menos infinito y `NaN`, que representa un resultado numérico indefinido. También se rechazan textos, incluso un texto como `"1.2"`. Cuando el valor no cumple, la función devuelve `None`. No lo sustituye por cero ni modifica el documento guardado.

`anio_valido` reutiliza esta limpieza y comprueba que el resto al dividir por uno sea cero: `numero % 1 != 0` detecta una parte decimal. Si el año resulta válido, lo convierte con `int`. Esta normalización de lectura exige un entero positivo; el límite superior del año actual se aplica a los filtros y al modelo de creación, no dentro de este ayudante.

#### `normalizar`

Esta función construye un diccionario nuevo. Convierte `_id` a texto porque MongoDB suele usar un identificador BSON `ObjectId`, que necesitamos representar de forma compatible con JSON.

Para los campos de texto conserva cadenas y retira espacios exteriores; para magnitudes aplica `numero_positivo`. Para indicadores acepta valores numéricos no booleanos pertenecientes a `[-1, 0, 1]` y los convierte a entero. Lo demás queda como `None`.

Usamos `campos.get(campo, campo)`: si existe una traducción, empleamos el alias; si no existe, conservamos el nombre original. El año se procesa con `anio_valido` y `fuente` se conserva si es un diccionario; en caso contrario se usa un diccionario vacío.

Normalizar significa producir una salida coherente. No demuestra que cada medición sea científicamente correcta ni repara de forma permanente todos los datos históricos. Además, no existe aquí una comprobación que obligue a que cada indicador tenga su magnitud correspondiente. Las reglas de evaluación verifican ambas cosas cuando las necesitan.

Los indicadores tienen una función decisiva: `0` representa el valor puntual empleado por nuestros cálculos; `-1` y `1` identifican límites según el esquema del catálogo; `None` significa que no tenemos un indicador interpretable. Ausencia de indicador no equivale a indicador cero.

#### `es_evaluable`, `es_candidato` y `origen_del_radio`

`es_evaluable` exige radio e insolación disponibles, más `limite_radio == 0` y `limite_insolacion == 0`. Es una condición específica de la primera pregunta. Un planeta puede no ser evaluable para ella y sí para otro criterio, por ejemplo el periodo orbital.

`es_candidato` exige primero que sea evaluable y después aplica los intervalos inclusivos `0.8 <= radio <= 1.6` y `0.35 <= insolacion <= 1.5`. “Inclusivo” significa que aceptamos exactamente los extremos.

`origen_del_radio` clasifica la referencia textual: sin texto devuelve “Sin referencia”; si contiene `calculated value`, ignorando mayúsculas, devuelve “Calculado por el archivo”; en los demás casos, “Otra referencia”. No recalcula el radio ni demuestra que todo lo clasificado como otra referencia sea una medición directa. El catálogo compuesto puede completar un radio ausente mediante una relación entre masa y radio; ese valor depende de un modelo y no debe presentarse como una medición exacta. Conservamos la referencia para reconocer esa diferencia. Véanse [la explicación del archivo sobre valores calculados](https://exoplanetarchive.ipac.caltech.edu/docs/pscp_calc.html) y la implementación en [api.py](api.py).

### Filtros: de la URL a una consulta de MongoDB

#### `recibir_filtros`, `Query` y `Depends`

Los parámetros de consulta aparecen después de `?` y se separan con `&`. En `/datos?pagina=2&por_pagina=25`, pedimos la segunda página de 25 registros. Aunque la URL contiene texto, FastAPI utiliza las anotaciones para interpretarlo y verificarlo.

`recibir_filtros` centraliza los parámetros compartidos:

| Parámetro | Tipo y regla | Significado |
|---|---|---|
| `metodo` | Texto opcional, máximo 100 caracteres. | Igualdad con el método seleccionado. |
| `nombre` | Texto opcional, máximo 150. | Búsqueda en planeta o estrella. |
| `anio_min`, `anio_max` | Enteros opcionales, entre 1 y el año configurado. | Intervalo inclusivo de descubrimiento. |
| `solo_candidatos` | Booleano, inicialmente falso. | Aplicar radio, insolación e indicadores. |
| `origen` | `todos`, `nasa` o `manual`. | Seleccionar procedencia. |

`Query` declara restricciones y valores por defecto: `ge` significa mayor o igual y `le`, menor o igual. Si el año inicial supera al final, la función lanza 422. Al devolver el diccionario también retira espacios exteriores de los textos recibidos.

En las rutas escribimos `filtros: dict = Depends(recibir_filtros)`. Esto pide a FastAPI que resuelva esa función y entregue su resultado al parámetro `filtros`. Compartimos reglas en lugar de mantener interpretaciones distintas para tabla y gráficas. Es una dependencia de funciones dentro de la aplicación, no otra petición HTTP. Véase [la documentación oficial de dependencias](https://fastapi.tiangolo.com/tutorial/dependencies/).

#### `construir_consulta` y sus operadores

El resultado de `recibir_filtros` aún es un diccionario de opciones de nuestra aplicación. `construir_consulta` lo traduce a la sintaxis de MongoDB. Comienza con `consulta = {}`: una consulta vacía selecciona todos los documentos.

El método se busca por igualdad usando el nombre de campo reconocido. Para el nombre construimos:

```python
texto = {"$regex": re.escape(filtros["nombre"]), "$options": "i"}
consulta["$or"] = [{"planeta": texto}, {"estrella": texto}]
```

En la primera línea, `re.escape` hace que signos como punto, paréntesis o más se busquen literalmente. `$regex` realiza la búsqueda textual y `$options: "i"` ignora diferencias entre mayúsculas y minúsculas. La segunda línea acepta que coincida el planeta **o** la estrella. Aquí no añadimos anclas de inicio y final: también puede coincidir una parte del nombre.

Los operadores `$gte` y `$lte` construyen los límites del año y los intervalos de candidatos. Las condiciones colocadas juntas en el nivel principal se deben cumplir simultáneamente. `$or` únicamente expresa la alternativa entre los dos campos de nombre.

Para el origen usamos la ruta de campo anidado `fuente.nombre`, comparada con “NASA Exoplanet Archive” o “Registro manual del proyecto”. `todos` no añade condición de procedencia. Por ello una selección sin filtro de origen puede incluir capturas manuales: el usuario debe elegir NASA si desea estudiar únicamente esa procedencia.

La consulta se aplica sobre los valores almacenados antes de normalizarlos. Esto importa si alguien introduce documentos incompatibles directamente en MongoDB: la limpieza de salida no convierte retroactivamente esos valores para el motor de filtros.

### Las rutas GET, una por una

#### `GET /`: identificar la aplicación

`inicio()` devuelve el título, la dirección relativa de documentación y la lista de operaciones. Sirve para reconocer el servicio y orientarnos. No consulta MongoDB y no prueba Gemini.

#### `GET /salud`: comprobar acceso real a MongoDB

`salud()` obtiene la colección y ejecuta `cliente.admin.command("ping")`. Después devuelve `estado`, `base`, `coleccion`, `esquema` y el número de documentos obtenido con `count_documents({})`.

Esta respuesta confirma que la operación de diagnóstico pudo acceder a la base en ese momento. No incluye la URI privada ni verifica la clave de IA. Si la conexión falla, se aplica el manejo de errores explicado más adelante.

#### `GET /opciones`: preparar los controles

`opciones()` obtiene los métodos mediante `distinct`, que devuelve valores diferentes del campo. Conserva textos no vacíos y los ordena. Para los años obtiene valores distintos, los valida y calcula mínimo y máximo; si no hay años válidos devuelve `None`.

También cuenta cuántos documentos tienen cada indicador dentro de `[-1, 0, 1]`, usando `$in`. Este resultado es `cobertura_limites`. Si no existe cobertura de radio o insolación, añade una advertencia sobre la primera pregunta. Si falta cobertura en temperatura, periodo o masa, advierte sobre los criterios extremos.

Contar indicadores no equivale a contar planetas evaluables: también necesitamos las magnitudes correspondientes. Las opciones se construyen sobre la colección completa, de manera que los controles no dependan solamente de los 25 registros de una página.

#### `GET /datos`: consultar y paginar

`listar_datos` recibe `pagina`, como entero desde 1, y `por_pagina`, entre 1 y 200, con valor predeterminado 25. Además recibe los filtros compartidos. Primero calcula `total = coleccion.count_documents(consulta)`; después obtiene únicamente la página solicitada.

El núcleo real es:

```python
salto = (pagina - 1) * por_pagina

documentos = (
    coleccion.find(consulta)
    .sort([("planeta", 1), ("_id", 1)])
    .skip(salto)
    .limit(por_pagina)
)
datos = [normalizar(documento, campos) for documento in documentos]
```

La primera línea calcula cuántos registros debemos saltar. En la página 1 no saltamos ninguno; en la 2, con 25 por página, saltamos 25. `find` crea un cursor, un objeto que permite recorrer resultados. `sort` ordena por planeta y después por identificador; `1` indica orden ascendente. El segundo campo resuelve empates de nombre.

`skip` avanza el número calculado y `limit` restringe la cantidad devuelta. La última línea es una comprensión de lista: recorremos el cursor, normalizamos cada documento y reunimos las salidas. Los paréntesis permiten distribuir la expresión en varias líneas legibles. La función de estos métodos está documentada en [PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/query/specify-documents-to-return/).

Devolvemos `total`, `pagina`, `por_pagina`, `paginas` y `datos`. `math.ceil(total / por_pagina)` redondea hacia arriba: 27 registros con páginas de 25 requieren dos páginas. `len(datos)` podría ser 2 en la segunda página, mientras que `total` seguiría siendo 27. Confundir ambas cantidades reduciría equivocadamente las estadísticas a lo visible.

Si no hay coincidencias, `total` y `paginas` valen cero y `datos` es una lista vacía. Si pedimos una página posterior a la última, esta ruta devuelve una lista vacía; no reajusta automáticamente el número pedido.

El orden es estable para un conjunto sin cambios. Inserciones concurrentes pueden desplazar resultados entre páginas, y el conteo y la lectura son operaciones separadas. Tampoco afirmamos que saltar un número grande de registros tenga coste constante.

### `GET /estadisticas`: cómo respondemos las cuatro preguntas

`estadisticas` recibe los mismos filtros y construye la misma consulta. Normaliza todos los documentos de la selección para los cálculos realizados en Python. Las agrupaciones por método y año se ejecutan separadamente en MongoDB sobre los valores almacenados; después se validan las claves de año. La agrupación por método no aplica la limpieza de texto de `normalizar`. No usa `pagina` ni `por_pagina`. Así una gráfica describe la selección completa aunque la tabla muestre solamente una página. Esta función combina agregaciones ejecutadas en MongoDB y operaciones realizadas en Python.

#### Agregaciones por método y año

Una agregación es una secuencia ordenada de etapas que transforma conjuntos de documentos. Para contar por método usamos este fragmento real:

```python
grupos_metodo = coleccion.aggregate([
    {"$match": consulta},
    {"$group": {
        "_id": "$" + campos["metodo_descubrimiento"],
        "conteo": {"$sum": 1},
    }},
    {"$sort": {"conteo": -1, "_id": 1}},
])
```

`aggregate` envía la secuencia a MongoDB. `$match` conserva la selección. `$group` reúne documentos que comparten método. En esta etapa `_id` significa la clave del grupo, no el identificador de un planeta. El signo `$` delante del nombre indica que tomamos el valor de ese campo. `$sum: 1` añade una unidad por documento.

`$sort` ordena por conteo descendente, indicado por `-1`, y desempata por nombre ascendente. Después convertimos los grupos a diccionarios con `metodo` y `conteo`; si falta un método se presenta “Sin método informado”.

La agregación por año repite la idea, agrupando por el campo del año y ordenando de menor a mayor. El código pasa cada clave por `anio_valido` antes de incorporarla a `por_anio`. Un registro sin año interpretable puede formar parte de otros totales y no aparecer en esta serie.

#### Primera pregunta: candidatos por radio e insolación

Recorremos la selección y contamos los que cumplen `es_evaluable`. Luego guardamos en una lista los que cumplen `es_candidato`. Usamos listas porque más adelante necesitamos los documentos completos para estudiar distancias.

El porcentaje es:

**Porcentaje de candidatos = candidatos / evaluables × 100.**

Redondeamos a dos decimales. Si no hay evaluables, devolvemos `None` para evitar dividir entre cero y no dar una falsa impresión de porcentaje conocido. `sin_informacion = total_filtrado - evaluables`.

Los registros evaluables que no cumplen los intervalos de radio e insolación suman `evaluables - candidatos`. Todos ellos ya pertenecen a la selección definida por los filtros activos. Los registros sin información suficiente deben permanecer como una categoría distinta. No haber podido evaluar un planeta no prueba que esté fuera del intervalo científico.

“Candidato” significa que cumple este filtro exploratorio de dos magnitudes y sus indicadores. El código no evalúa atmósfera, agua, campo magnético ni presencia de vida. Para defender el trabajo debemos distinguir la selección matemática de una conclusión de habitabilidad.

#### Segunda pregunta: cercanía y viaje idealizado

Recorremos los candidatos y conservamos los que tienen distancia positiva conocida. La conversión es:

**Distancia en años luz = distancia en pársecs × 3.26.**

La función `numero_positivo` vuelve a revisar el resultado. Copiamos cada diccionario con `.copy()` para añadir `distancia_anios_luz`, `viaje_anios` y `origen_radio` sin alterar el diccionario de la lista original. Tampoco escribimos estos cálculos en MongoDB.

El tiempo del ejercicio se calcula así:

**Años de viaje = distancia en años luz × 299792.458 / 17.**

La razón entre ambas velocidades es adimensional. Un año luz es una distancia: la recorrida por la luz en un año. Si expresáramos la distancia en kilómetros y luego dividiéramos por 17 km/s, al convertir segundos a años se cancelaría el factor de segundos por año. Por eso la fórmula no necesita introducirlo otra vez.

Como ejemplo puramente matemático, un objeto a 10 años luz daría aproximadamente 176348.5 años bajo este supuesto. No es una previsión de misión: el cálculo supone velocidad constante y omite aceleración, frenado y otras condiciones del viaje.

Ordenamos mediante `sort(key=lambda p: p["distancia_anios_luz"])`. `lambda` define una función breve que indica qué valor comparar. `cercanos` devuelve hasta los primeros diez con `[:10]`; `candidatos_con_distancia` informa cuántos tienen distancia conocida en toda la selección, aunque sean más de diez.

#### Tercera pregunta: distancias por método de descubrimiento

Aquí usamos todos los documentos filtrados, no solamente los candidatos. Para cada registro con método informado y distancia válida, convertimos a años luz y añadimos el resultado a una lista asociada a ese método.

Después construimos una fila con `metodo`, `cantidad`, `minima`, `mediana` y `maxima`. `min` y `max` encuentran extremos; `median` obtiene el valor central ordenado, o el promedio de los dos centrales cuando hay una cantidad par. La mediana ayuda a describir el centro sin depender tanto de unos pocos valores muy alejados.

Ordenamos las filas por distancia máxima descendente con `reverse=True`. `cantidad` cuenta distancias utilizables, mientras que `por_metodo.conteo` cuenta registros del método aunque no tengan distancia. Estos denominadores pueden diferir sin que exista un error.

La máxima es la mayor distancia **observada en nuestra selección**, no el límite físico o tecnológico definitivo de un método. Si cambiamos filtros, también puede cambiar esa máxima.

#### Cuarta pregunta: cuatro criterios de planetas extremos

Para cada planeta creamos un diccionario de resultados inicialmente en `None`. La distinción entre tres estados es esencial:

| Estado interno | Interpretación |
|---|---|
| `None` | No tenemos condiciones suficientes para evaluar ese criterio. |
| `False` | Se pudo evaluar y no cumple el umbral. |
| `True` | Se pudo evaluar y cumple el umbral. |

Las reglas exactas del código son:

| Categoría | Condiciones para evaluar | Condición para ser caso |
|---|---|---|
| Infierno | Temperatura válida, indicador cero, método informado y diferente de `Imaging`. | Temperatura mayor que 2000 K. |
| Congelado | Las mismas condiciones de temperatura. | Temperatura menor que 100 K. |
| Relámpago | Periodo válido e indicador de periodo cero. | Periodo menor que 1 día. |
| Supergigante | Masa válida e indicador de masa cero. | Masa mayor que 4131.4 masas terrestres. |

Aquí las desigualdades son estrictas: exactamente 2000 K no cumple “Infierno”, exactamente un día no cumple “Relámpago”. La exclusión de `Imaging` pertenece a la regla implementada para temperatura y no se aplica automáticamente a periodo o masa.

En los datos procedentes del archivo, `temperatura_planeta_k` corresponde a `pl_eqt`. Su definición describe una temperatura de equilibrio obtenida mediante un modelo; para planetas observados por imagen directa puede contener una temperatura efectiva asociada a su luminosidad. No debemos llamarla temperatura superficial medida. Esta diferencia ayuda a entender por qué el proyecto conserva una precaución específica para `Imaging`. La definición se puede consultar en [las columnas oficiales de NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html).

Cada categoría tiene su propio contador de `evaluables` y `casos`. Un porcentaje por categoría, cuando se presente, debe dividir sus casos entre sus propios evaluables. Las capturas con masa catalogada también conservan `tipo_masa`; no debemos convertir una masa mínima en una medición exacta de masa real mediante una afirmación verbal.

Además contamos casos y evaluables por método. `any(valor is True for valor in casos.values())` pregunta si al menos un criterio se cumple y aumenta una sola vez `planetas_con_extremos`. Un planeta puede pertenecer a varias categorías; por eso sumar los cuatro conteos puede superar la cantidad de planetas distintos con algún extremo.

#### Qué contiene la respuesta estadística

| Campos de salida | Contenido |
|---|---|
| `total_coleccion`, `total` | Todos los documentos de la colección y documentos de la selección, respectivamente. |
| `evaluables`, `candidatos`, `porcentaje_candidatos`, `sin_informacion` | Primera pregunta. |
| `candidatos_con_distancia`, `cercanos` | Segunda pregunta y hasta diez primeros por cercanía. |
| `por_metodo`, `por_anio` | Distribuciones de documentos. |
| `distancias_por_metodo` | Mínimo, mediana y máximo de distancias utilizables. |
| `extremos` | Casos y evaluables de cada criterio. |
| `extremos_por_metodo`, `evaluables_extremos_por_metodo` | Desglose de ambos conteos por método. |
| `planetas_con_extremos` | Planetas distintos que cumplen al menos un criterio. |

La función carga la selección en memoria y la recorre varias veces. Es una implementación comprensible para este catálogo académico; no es un procesamiento de memoria constante. Además, lecturas, agregaciones y conteos no forman una única transacción de instantánea. Los resultados describen lo leído durante la solicitud, con esa limitación ante cambios concurrentes.

### `POST /datos`: validación y creación de una captura manual

#### `NuevoRegistro`: el contrato de entrada

`class NuevoRegistro(BaseModel)` define un modelo de datos usando Pydantic. Una clase agrupa una estructura y su comportamiento; heredar de `BaseModel` incorpora la validación que usa FastAPI para el cuerpo JSON. La declaración `registro: NuevoRegistro` en la ruta hace que el programa reciba un objeto ya validado, o responda con un error antes de insertar. Véase [FastAPI: cuerpo de solicitud](https://fastapi.tiangolo.com/es/tutorial/body/).

`ConfigDict` establece tres decisiones: `extra="forbid"` rechaza campos no declarados; `str_strip_whitespace=True` retira espacios exteriores del texto; y `allow_inf_nan=False` rechaza números no finitos. La configuración oficial está descrita en [Pydantic](https://docs.pydantic.dev/latest/api/config/).

Son obligatorios `planeta`, `estrella`, `metodo_descubrimiento` y `anio_descubrimiento`. Los dos primeros requieren entre 1 y 150 caracteres; el método, entre 1 y 100. El año debe ser entero, al menos 1 y no mayor que `ANIO_ACTUAL`. Su `strict=True` exige el tipo entero: no basta enviar el texto `"2020"`.

Las siete magnitudes de `CAMPOS_NUMERICOS` son opcionales, aceptan `None` y, cuando se informan, deben ser mayores que cero mediante `gt=0`. `tipo_masa` y `lugar_descubrimiento` admiten hasta 100 caracteres; `referencia_radio`, hasta 3000. Los cinco indicadores solo admiten `-1`, `0`, `1` o ausencia.

`Field` expresa estas restricciones junto al campo. `default=None` permite omitirlo. No todos los campos numéricos tienen modo estricto: el año sí lo declara; no debemos decir que ninguna conversión de tipos es posible en el resto del modelo. La función de las restricciones se documenta en [Pydantic: campos](https://docs.pydantic.dev/latest/concepts/fields/).

#### Rechazar booleanos antes de convertir

Este fragmento real añade una comprobación específica:

```python
@field_validator(*CAMPOS_NUMERICOS, *CAMPOS_LIMITES, mode="before")
@classmethod
def rechazar_booleanos(cls, valor):
    """True y False no son magnitudes ni indicadores de límites válidos."""
    if isinstance(valor, bool):
        raise ValueError("Introduce un número o deja el campo sin dato.")
    return valor
```

El asterisco delante de cada lista distribuye sus nombres como argumentos del decorador. `mode="before"` ejecuta la comprobación antes de las conversiones posteriores. `@classmethod` declara un método asociado a la clase; `cls` representa esa clase.

`isinstance(valor, bool)` detecta valores lógicos. `ValueError` señala una entrada inválida y Pydantic lo incorpora al error de validación. Si no es booleano, devolvemos el valor para que continúen las demás comprobaciones. Así `true` no se acepta como una masa o como el indicador 1.

#### `crear_registro`: del modelo al documento persistido

El decorador `@app.post("/datos", status_code=201, tags=["Creación"])` registra la creación y declara 201 para el éxito. Tras obtener la colección construimos un patrón exacto:

`"^" + re.escape(registro.planeta) + "$"`.

`^` indica inicio y `$` final; por eso, a diferencia de la búsqueda parcial de GET, aquí buscamos el nombre completo. La opción `i` ignora mayúsculas. Si `find_one` encuentra coincidencia, respondemos 409.

Después recorremos `registro.model_dump().items()`. `model_dump` convierte el modelo a diccionario; `items` permite obtener cada nombre y valor. Traducimos nombres con `campos.get(campo, campo)` para guardar en el esquema reconocido.

La API fija `fuente.nombre` como “Registro manual del proyecto” y `fuente.tabla` como `captura_manual`. El cliente no puede declarar arbitrariamente una procedencia NASA mediante este modelo, porque `fuente` no es un campo aceptado del cuerpo.

`insert_one(documento)` realiza la escritura. Su resultado contiene `inserted_id`; lo añadimos al diccionario y devolvemos mensaje, identificador textual y registro normalizado. Esa información queda persistida en MongoDB, no solamente en una variable de la pantalla. El método está descrito en [MongoDB: inserciones](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/insert/).

El bloque `try/except DuplicateKeyError` transforma un conflicto de clave detectado por MongoDB en 409. Hay un límite que debemos explicar correctamente: comprobar y después insertar son dos operaciones. Dos solicitudes simultáneas podrían superar la comprobación previa. Este archivo no crea un índice único para `planeta`; por tanto, no afirmamos unicidad atómica del nombre. Un índice único existente podría impedir determinadas duplicaciones, pero no lo suponemos sin verificarlo.

### Errores y respuestas HTTP del backend

Un estado HTTP describe el resultado general; el JSON aporta el detalle. En nuestras operaciones de datos usamos principalmente:

| Estado | Interpretación en el proyecto |
|---|---|
| 200 | Consulta completada. Una lista vacía también puede ser una consulta correcta. |
| 201 | Captura manual creada. |
| 409 | Conflicto detectado al intentar crear un registro. |
| 422 | Parámetro, cuerpo o combinación de filtros inválida. |
| 503 | Falta configuración o no fue posible completar una operación de MongoDB. |

`datos_invalidos` maneja `RequestValidationError`: recorre los problemas y conserva `loc`, `msg` y `type`. `loc` identifica dónde ocurrió el problema, por ejemplo el cuerpo y un campo. No devolvemos el valor original completo de la entrada.

`Request` representa la solicitud HTTP que FastAPI entrega al manejador. El argumento `error` representa la excepción que ocurrió; la firma permite al framework invocar la función aunque no necesitemos leer todos sus atributos. `@app.exception_handler` registra el tipo de excepción que atenderá cada manejador.

`error_mongodb` maneja `PyMongoError` y responde 503 con un mensaje sobre configuración, usuario, acceso de red y conexión. No incorpora la excepción original ni la URI al mensaje público. `JSONResponse` permite definir explícitamente cuerpo y estado en ambos manejadores.

Una `HTTPException` que lanzamos deliberadamente interrumpe esa operación y devuelve su detalle. No todos los errores tienen un `detail` de la misma forma: puede ser una lista de problemas de validación o un texto explicativo. El dashboard debe tratarlo como respuesta de error, no como un registro válido. FastAPI explica estos mecanismos en [su documentación de errores](https://fastapi.tiangolo.com/es/tutorial/handling-errors/).

La ruta `POST /preguntar` añade los errores relacionados con IA, tratados en su apartado. Su existencia no cambia las reglas de validación ni el comportamiento de las rutas de lectura y creación que acabamos de explicar.

### Dos recorridos completos para explicar en la sustentación

#### Ejemplo hipotético de GET: una selección sin coincidencias

Este ejemplo es didáctico: suponemos una colección disponible sin ningún planeta ni estrella que contenga el texto indicado. No describe una consulta ejecutada ni un resultado medido en producción.

Solicitud:

```http
GET /datos?nombre=EJEMPLO-SIN-COINCIDENCIAS&origen=nasa&pagina=1&por_pagina=25
```

FastAPI interpreta la ruta y los parámetros. Valida que página y tamaño sean permitidos. `recibir_filtros` construye el diccionario con el texto, origen NASA y los demás valores por defecto. `obtener_coleccion` entrega la colección y los nombres de campo.

`construir_consulta` combina una búsqueda textual en planeta o estrella con `fuente.nombre = "NASA Exoplanet Archive"`. MongoDB encuentra cero coincidencias. El salto es `(1 - 1) * 25 = 0`; el cursor no produce documentos y la lista normalizada queda vacía.

Respuesta HTTP 200, completa para este supuesto:

```json
{
  "total": 0,
  "pagina": 1,
  "por_pagina": 25,
  "paginas": 0,
  "datos": []
}
```

La API respondió correctamente: “sin coincidencias” es diferente de “sin conexión”. El dashboard puede mostrar un mensaje de selección vacía y permitir cambiar filtros.

#### Ejemplo hipotético de POST: una captura identificada como manual

Los nombres, identificadores y mediciones siguientes son ficticios para explicar el flujo. No representan un descubrimiento real ni una inserción realizada durante la preparación del documento.

Solicitud:

```http
POST /datos
Content-Type: application/json
```

```json
{
  "planeta": "PLANETA-DEMO",
  "estrella": "ESTRELLA-DEMO",
  "metodo_descubrimiento": "Demostración",
  "anio_descubrimiento": 2020,
  "radio_tierras": 1.1,
  "insolacion_tierra": 0.9,
  "limite_radio": 0,
  "limite_insolacion": 0
}
```

FastAPI entrega el cuerpo a `NuevoRegistro`. Están presentes los cuatro campos obligatorios, el año es un entero y las magnitudes son positivas. Los campos omitidos toman `None`. Suponemos que la colección no contiene el nombre.

La API comprueba duplicados, transforma los campos si el esquema lo requiere, añade la fuente manual e inserta el documento. MongoDB asigna un identificador. La API lo convierte a texto y normaliza la respuesta.

Una respuesta 201 hipotética completa sería:

```json
{
  "mensaje": "Registro manual guardado correctamente.",
  "id": "000000000000000000000001",
  "registro": {
    "_id": "000000000000000000000001",
    "planeta": "PLANETA-DEMO",
    "estrella": "ESTRELLA-DEMO",
    "metodo_descubrimiento": "Demostración",
    "lugar_descubrimiento": null,
    "tipo_masa": null,
    "referencia_radio": null,
    "radio_tierras": 1.1,
    "insolacion_tierra": 0.9,
    "distancia_sistema_parsec": null,
    "temperatura_planeta_k": null,
    "periodo_orbital_dias": null,
    "masa_tierras": null,
    "densidad_planeta": null,
    "limite_radio": 0,
    "limite_insolacion": 0,
    "limite_temperatura": null,
    "limite_periodo": null,
    "limite_masa": null,
    "anio_descubrimiento": 2020,
    "fuente": {
      "nombre": "Registro manual del proyecto",
      "tabla": "captura_manual"
    }
  }
}
```

Una consulta posterior con origen manual podría recuperar ese documento. Con origen NASA quedaría excluido. Cumpliría el filtro matemático de candidatos por radio e insolación, pero seguiría siendo una demostración manual y, al faltar distancia, no entraría en la lista de cercanos.

Si enviáramos `radio_tierras: true`, recibiríamos 422 antes de insertar. Si repitiéramos el nombre ya existente, la comprobación ordinaria devolvería 409. Si MongoDB no estuviera accesible, la operación respondería 503 según el manejo descrito.

### Fuentes para contrastar este capítulo

La fuente principal de cada función, campo y regla presentada es [api.py](api.py); las dependencias se consultan en [requirements.txt](requirements.txt). Estas referencias oficiales respaldan el uso de los frameworks, no sustituyen la lectura del código particular del proyecto:

- [FastAPI: parámetros de consulta](https://fastapi.tiangolo.com/tutorial/query-params/).
- [FastAPI: dependencias](https://fastapi.tiangolo.com/tutorial/dependencies/).
- [FastAPI: cuerpo de solicitud](https://fastapi.tiangolo.com/es/tutorial/body/).
- [FastAPI: manejo de errores](https://fastapi.tiangolo.com/es/tutorial/handling-errors/).
- [Pydantic: configuración](https://docs.pydantic.dev/latest/api/config/) y [campos](https://docs.pydantic.dev/latest/concepts/fields/).
- [MongoDB: MongoClient](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/mongoclient/).
- [MongoDB: orden, salto y límite de resultados](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/query/specify-documents-to-return/).
- [MongoDB: inserción de documentos](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/insert/).
- [NASA Exoplanet Archive: definición de columnas](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html) y [valores calculados del catálogo compuesto](https://exoplanetarchive.ipac.caltech.edu/docs/pscp_calc.html).

<a id="dashboard"></a>

## 5. Dashboard: ejecución, filtros, gráficas y formulario

### El dashboard: convertir las respuestas de la API en una aplicación

El archivo [dashboard.py](dashboard.py) contiene el **frontend**, es decir, la parte del proyecto con la que interactuamos: filtros, indicadores, tablas, gráficas y formularios. Usamos Streamlit para construir esa interfaz escribiendo Python. El navegador muestra los componentes; el programa de Streamlit se ejecuta en el servidor que lo aloja. Por eso la petición a nuestra API sale del programa de Streamlit y no de una conexión directa del navegador a MongoDB.

La separación tiene una razón concreta: en [api.py](api.py) concentramos las consultas, validaciones, estadísticas y acceso a Gemini; en el dashboard decidimos cómo pedir y mostrar esos resultados. Por ejemplo, la API calcula cuántos candidatos existen y el dashboard dibuja la barra correspondiente. El dashboard conoce `API_BASE_URL`, pero no necesita la contraseña de MongoDB ni la clave de Gemini.

Un **módulo** es un archivo de Python que podemos importar para utilizar su código. Un `import` da acceso a funciones y objetos de ese módulo. Una **variable** es un nombre asociado a un valor: `resumen` contiene un diccionario con estadísticas; `pagina` contiene un número. Una **función**, definida con `def`, reúne instrucciones que ejecutamos cuando la llamamos. Definir `mostrar_catalogo` no consulta inmediatamente la API; esa consulta ocurre cuando más adelante llamamos a la función.

#### Importaciones y configuración inicial

Todas las importaciones del dashboard tienen un uso identificable:

| Importación | Para qué la usamos aquí |
|---|---|
| `math` | `ceil` redondea hacia arriba el número de páginas; `isfinite` rechaza valores numéricos infinitos o no definidos. |
| `os` | `os.getenv` lee la dirección de la API desde el entorno. |
| `datetime` | `datetime.now().year` obtiene el año actual para limitar y proponer años en los formularios. |
| `pandas as pd` | Construye tablas, aplana documentos, selecciona columnas, ordena datos y prepara el CSV. `pd` es un alias corto. |
| `requests` | Hace las peticiones HTTP GET y POST a nuestra API. |
| `streamlit as st` | Crea los componentes de pantalla y administra las interacciones. `st` también es un alias. |
| `load_dotenv` | Carga variables definidas en un archivo `.env` local, si existe. |

La configuración principal es:

```python
load_dotenv()
API = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
ANIO_ACTUAL = datetime.now().year
```

Si falta `API_BASE_URL`, usamos la API local del puerto 8000. `rstrip("/")` quita barras finales: después podremos unir `API` con una ruta como `/datos` sin formar dos barras consecutivas. Una dirección de API y una URI de MongoDB cumplen funciones distintas; no intercambiamos sus valores. `st.set_page_config` establece el título de la pestaña del navegador, el icono y `layout="wide"` para aprovechar el ancho disponible.

Los tres diccionarios de configuración son conjuntos de parejas **clave: valor**. `ORIGENES` traduce las etiquetas visibles a `todos`, `nasa` y `manual`, los valores que entiende la API. `INDICADORES` traduce «Desconocido» a `None`, «Valor puntual» a `0`, «Límite superior» a `1` y «Límite inferior» a `-1`. `None` representa ausencia de información; no es cero. `NOMBRES_COLUMNAS` relaciona nombres internos como `radio_tierras` con títulos como «Radio (Tierras)». Incluye medidas, procedencia de la masa, distancias convertidas, tiempo de viaje y los campos anidados de la fuente. Estas traducciones facilitan la lectura sin cambiar los documentos almacenados.

#### `pedir_api`: la conexión común para todas las pantallas

Usamos una sola función para evitar repetir el manejo de peticiones y errores:

```python
def pedir_api(ruta, parametros=None, registro=None, espera=20):
```

`ruta` identifica el recurso, por ejemplo `/estadisticas`. `parametros` contiene filtros o paginación. `registro` contiene un cuerpo que enviaremos por POST. `espera` controla el tiempo de espera de Requests. Los valores después de `=` son valores predeterminados, utilizados cuando no proporcionamos ese argumento.

La elección del método depende de `registro is None`:

```python
if registro is None:
    respuesta = requests.get(
        f"{API}{ruta}", params=parametros, timeout=espera
    )
else:
    respuesta = requests.post(
        f"{API}{ruta}", params=parametros, json=registro, timeout=espera
    )
```

La letra `f` permite insertar variables dentro del texto. GET consulta información. POST envía un cuerpo para que la API lo procese: puede crear un registro en `/datos` o formular una pregunta en `/preguntar`. Por eso el nombre `registro` no significa que todos los POST guarden un planeta.

`params` hace que Requests codifique los parámetros en la URL; no concatenamos manualmente espacios, acentos o símbolos. `json=registro` serializa el diccionario como JSON en el cuerpo de la petición. En una pregunta usamos simultáneamente `params=filtros` y `json={"pregunta": ...}`: los filtros viajan como parámetros y la pregunta viaja en el cuerpo. [Requests documenta estos mecanismos](https://requests.readthedocs.io/en/latest/user/quickstart/).

`try` ejecuta una operación que podría fallar; `except` define la reacción. Capturamos `Timeout`, `ConnectionError` y, finalmente, otros `RequestException`. Mostramos un mensaje con `st.error` y devolvemos `None`. El valor `timeout=20`, o `60` para la IA, limita esperas de conexión/lectura; no garantiza que toda la operación termine exactamente en ese número de segundos. No implementamos reintentos automáticos.

Recibir una respuesta HTTP no garantiza que su contenido sea JSON. `respuesta.json()` intenta convertirlo en objetos de Python; si falla, capturamos `ValueError`. Después comprobamos `respuesta.ok`. En errores de `/preguntar`, mostramos el `detail` textual de nuestra API cuando está disponible. Para las demás rutas traducimos `409` a nombre duplicado, `422` a entrada inválida y `503` a problema con la base de datos; otros códigos reciben un mensaje general.

Si el `422` trae una lista de errores de validación, recorremos cada error. `error.get("loc", [])[1:]` omite el primer elemento de la ubicación, por ejemplo `body`, y `".".join(...)` une el resto para identificar el campo. `get` permite proporcionar un valor alternativo cuando una clave no existe. `isinstance` comprueba tipos antes de tratar un dato como lista, diccionario o texto.

Finalmente exigimos que una respuesta satisfactoria sea un diccionario. Así las funciones que la consumen reciben siempre un diccionario utilizable o `None`. Este último hace que abandonen su operación de forma controlada. La función no calcula estadísticas ni guarda una copia permanente de las respuestas.

#### `numero` y `preparar_tabla`: presentación sin alterar los datos

`numero(valor, decimales=0)` presenta números con separadores habituales en español. Si recibe `None`, devuelve «Sin dato». Si recibe cero, devuelve `0`: distinguir estos casos evita inventar una medición. La expresión `f"{valor:,.{decimales}f}"` genera texto con separador de miles y decimales configurables. Después intercambiamos coma y punto usando `_` temporalmente, para que un reemplazo no destruya el siguiente. Por ejemplo, `numero(1234.56, 2)` produce `1.234,56`. Redondear el texto mostrado no modifica la medición original.

Un **DataFrame** de pandas es una tabla con filas y columnas identificadas. Lo usamos como estructura común para tablas, gráficas y exportación:

```python
tabla = pd.json_normalize(registros)
presentes = [columna for columna in columnas if columna in tabla.columns]
return tabla[presentes].rename(columns=NOMBRES_COLUMNAS)
```

`pd.json_normalize` transforma la lista de documentos en filas. También aplana objetos anidados: `{"fuente": {"nombre": "...", "tabla": "..."}}` origina columnas `fuente.nombre` y `fuente.tabla`. Ese comportamiento está explicado en la [documentación de pandas](https://pandas.pydata.org/docs/reference/api/pandas.json_normalize.html).

La comprensión de lista `[...]` recorre las columnas solicitadas y conserva solamente las existentes, en ese orden. Así evitamos intentar mostrar una columna ausente. `tabla[presentes]` selecciona esas columnas; `rename` cambia sus títulos visibles según el diccionario. Ninguna de estas instrucciones modifica MongoDB.

### Cómo se ejecuta la pantalla y cómo funcionan los filtros

Streamlit vuelve a ejecutar el archivo de arriba abajo cuando se produce una interacción que dispara una ejecución. Un **evento** es precisamente una interacción de este tipo, como pulsar un botón. No mantenemos un bucle propio esperando clics. Las variables normales se vuelven a calcular; `st.session_state` permite conservar ciertos valores entre ejecuciones dentro de una sesión. No es una colección de MongoDB ni un almacén compartido por todos los visitantes. Véase la [documentación de Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state).

Primero mostramos el título y las instrucciones con `st.title` y `st.write`. Si aún no existen, inicializamos `session_state["filtros"]` con `{"origen": "todos"}` y `session_state["pagina"]` con `1`. Después hacemos GET `/opciones`. Sus métodos, años y advertencias alimentan la interfaz. Si falla, mostramos «Volver a intentar» y `st.stop()` termina esa ejecución: no continuamos usando opciones inexistentes. El clic en ese botón provoca otra ejecución y, por tanto, otro intento.

Ordenamos los métodos con `sorted`. Recorremos las advertencias mediante `for`; si no hay clave, `get("advertencias", [])` proporciona una lista vacía. Antes de crear los filtros procesamos los mensajes y el nombre de un registro recién guardado; más adelante explicamos esa sincronización.

#### Barra lateral, formularios y selección activa

`with st.sidebar:` dirige los componentes a la barra lateral. La palabra `with` establece un contexto: lo que escribimos dentro queda en ese contenedor. Los **widgets** son componentes interactivos. Cada `key` los identifica y vincula su valor con el estado de la sesión.

| Componente del filtro | Función exacta |
|---|---|
| `st.text_input` | Escribir un nombre de planeta o estrella. |
| `st.selectbox` de método | Elegir una opción entre «Todos» y los métodos disponibles. |
| `st.selectbox` de procedencia | Elegir una etiqueta de `ORIGENES`. `list(ORIGENES)` obtiene sus claves visibles. |
| `st.checkbox` de candidatos | Activar o desactivar la exigencia de cumplir radio e insolación. |
| `st.checkbox` de años | Decidir si el intervalo escrito se aplicará a la consulta. |
| Dos `st.number_input` | Elegir los años inicial y final como enteros entre 1 y el año actual. |
| `st.form_submit_button` | Enviar juntas las elecciones al pulsar «Aplicar filtros». |

`st.form` agrupa cambios: editar sus campos no aplica inmediatamente cada filtro. Al enviar, Streamlit entrega sus valores juntos. Esa es la razón de usar formulario y botón de aplicación, según el [comportamiento documentado de los formularios](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form). Los años iniciales se toman de `/opciones`, con alternativas cuando faltan, y `min`/`max` los mantienen dentro de los límites permitidos.

Si el intervalo está activado y el año inicial supera al final, mostramos un error y conservamos la selección anterior. Si es válido, construimos un diccionario con origen y condición de candidatos. Añadimos nombre solo si contiene texto después de `strip()`, método solo si no es «Todos» y años solo si su casilla está activada. `strip()` elimina espacios al principio y al final.

Guardamos el diccionario como selección activa, volvemos a la página 1 y eliminamos la respuesta anterior de IA. `pop("respuesta_ia", None)` elimina esa entrada si existe sin fallar si no existe. «Actualizar datos» también elimina la respuesta de IA; el propio clic vuelve a ejecutar las consultas. No hay un caché de estadísticas que tengamos que vaciar.

#### Indicadores, contenedores y pestañas

Con los filtros activos pedimos GET `/estadisticas`. Si falla, usamos `st.stop()`. Si funciona, `st.columns(4)` crea cuatro espacios para métricas: total de toda la colección, total de la selección, evaluables y candidatos. `st.metric` muestra un valor destacado, no calcula ese valor. Solo la primera cifra ignora los filtros. Las demás cifras y las gráficas usan la **selección completa**, aunque el catálogo muestre 25 filas.

Si está activo el filtro de candidatos, advertimos que todos los registros seleccionados cumplen. Si la colección está vacía, explicamos que el formulario puede crear el primer registro. No confundimos colección vacía con una selección sin coincidencias.

`st.tabs` crea cuatro contenedores y asignamos cada uno a una variable. Dentro de sus bloques `with` llamamos a las cuatro funciones correspondientes. En este uso, **se ejecuta el contenido de todas las pestañas**, incluso de las que no están visibles: cambiar de pestaña no constituye una carga independiente. Es el [comportamiento predeterminado documentado de `st.tabs`](https://docs.streamlit.io/develop/api-reference/layout/st.tabs). Dibujar la pestaña de IA no llama por sí mismo a Gemini: esa llamada está dentro de la condición de envío.

Los demás componentes organizan o comunican: `st.subheader` y `st.header` titulan; `st.caption` añade precisiones; `st.divider` separa bloques; `st.info`, `st.warning`, `st.error` y `st.success` distinguen información, advertencia, error y éxito. `st.expander` recoge contenido en una sección desplegable. Cerrarlo no evita ejecutar el código que contiene. `st.columns(2)` reparte el espacio por igual; `st.columns([2, 1])` reserva aproximadamente el doble de ancho a la primera columna.

### Las cuatro preguntas: datos, gráficas e interpretación

`mostrar_preguntas(resumen)` recibe estadísticas ya calculadas por [la función `estadisticas` de api.py](api.py). No descarga cada página para reconstruirlas. Usamos las gráficas integradas de Streamlit, sin incorporar otra biblioteca gráfica explícita al proyecto. En `st.bar_chart`, `x` identifica la columna de categorías y `y` la magnitud. `horizontal=True` coloca las categorías al costado y representa la magnitud mediante la longitud horizontal de las barras. `sort=False` conserva el orden preparado. Estas opciones están descritas en la [referencia de `st.bar_chart`](https://docs.streamlit.io/develop/api-reference/charts/st.bar_chart).

#### Primera pregunta: candidatos, descartes y ausencia de información

Comparamos radio entre 0,8 y 1,6 radios terrestres e insolación entre 0,35 y 1,5 veces la terrestre, incluyendo ambos extremos. Para evaluar necesitamos las dos magnitudes positivas y sus dos indicadores en `0`, es decir, valores puntuales. Tener un número sin conocer su indicador no basta. Estas son las reglas de nuestro proyecto; cumplirlas no demuestra habitabilidad.

Construimos un DataFrame desde un diccionario con dos listas:

```python
clasificacion = pd.DataFrame({
    "Resultado": ["Cumplen ambos criterios", "No cumplen ambos", "Sin información suficiente"],
    "Planetas": [candidatos, evaluables - candidatos, resumen["sin_informacion"]],
})
```

Los elementos que ocupan la misma posición forman una fila. Las tres barras representan categorías excluyentes: cumplen, podemos evaluar pero no cumplen ambos, y no podemos evaluar. Su suma da el total seleccionado. Las barras permiten comparar cantidades sin interpretar áreas ni confundir información ausente con un resultado negativo.

En la segunda columna mostramos `100 × candidatos / evaluables`. El denominador no es el total seleccionado. Si hay 2 candidatos, 10 evaluables y 5 registros insuficientes, el resultado ilustrativo es 20 %, no 13,3 %. Si no existen evaluables, la API entrega `None` y mostramos «No calculable», en vez de fabricar un 0 %. `numero(..., 1)` muestra una cifra decimal. Cuando hay registros pero ninguno evaluable también explicamos la causa.

Si previamente activamos «Solo cumplen radio e insolación», la selección ya contiene únicamente candidatos y el porcentaje será 100 % cuando no esté vacía. Eso describe ese filtro, no la proporción del catálogo completo.

#### Segunda pregunta: cercanía y viaje idealizado

La API filtra los candidatos con distancia positiva conocida, convierte parsecs a años luz, los ordena de menor a mayor y entrega como máximo diez en `cercanos`. El dashboard prepara una tabla con planeta, distancia, viaje, radio, insolación, procedencia del radio y fuente. Las barras horizontales facilitan leer los nombres y comparar distancias; `sort=False` conserva el orden recibido. `st.dataframe` permite consultar cifras exactas, usa el ancho del contenedor y oculta el índice técnico de pandas con `hide_index=True`.

El texto complementario informa cuántos candidatos con distancia existen en toda la selección. Ese número puede superar las diez filas mostradas. Si no hay candidatos con distancia, mostramos un mensaje; no dibujamos una supuesta distancia cero.

Las operaciones implementadas en la API son:

```text
distancia en años luz = distancia en parsecs × 3,26
tiempo en años = distancia en años luz × (299.792,458 / 17)
```

La segunda expresión parte de dividir distancia por velocidad. Un año luz equivale a lo que recorre la luz en un año; por eso multiplicar su cantidad por la razón entre la velocidad de la luz y 17 km/s produce años de viaje. Un año luz **mide distancia**. El escenario supone velocidad constante, sin aceleración ni frenado; no constituye un plan de misión. La columna de procedencia del radio permite advertir cuándo ese valor figura como calculado por el archivo. No inferimos una medición directa a partir de que aparezca un número.

#### Tercera pregunta: distancias por método

`distancias_por_metodo` contiene cantidad de datos con distancia, mínima, mediana y máxima para cada método. La API usa los registros con método informado y distancia válida de la selección. Creamos el DataFrame y renombramos sus columnas.

`st.radio` permite elegir una sola medida: mediana o máxima. Su clave `medida_distancia` conserva la elección. La gráfica recibe `distancias.sort_values(medida)`, de modo que ordenamos por el valor elegido y evitamos un nuevo orden automático con `sort=False`. La tabla recibe `distancias` sin esa ordenación adicional: muestra todas las medidas y mantiene el orden entregado por la API, basado en la máxima descendente.

La mediana es el centro de los valores ordenados; si la cantidad es par, promediamos los dos centrales. La máxima es el caso más lejano observado. Por ejemplo, en distancias ilustrativas de 10, 12 y 100, la mediana es 12 y la máxima 100. El valor extremo cambia mucho la máxima, pero no desplaza el centro hasta 100.

Por eso ofrecemos ambas medidas y mostramos cuántos datos respaldan cada grupo. Un método con más registros puede tener más oportunidades de incluir un extremo. Las diferencias también reflejan qué objetos se buscaron y qué distancias están disponibles. La gráfica describe los descubrimientos registrados; no mide el alcance físico máximo de un instrumento ni demuestra que un método sea mejor. La mínima está en la tabla, aunque no sea una opción del selector. Si faltan grupos utilizables, mostramos información en lugar de una comparación vacía.

#### Cuarta pregunta: extremos y denominadores diferentes

Usamos cuatro etiquetas definidas por el proyecto:

| Etiqueta | Condición estricta |
|---|---|
| Infierno | Temperatura mayor que 2.000 K. |
| Congelado | Temperatura menor que 100 K. |
| Relámpago | Período orbital menor que un día. |
| Supergigante | Masa catalogada mayor que `13 × 317,8 = 4.131,4` masas terrestres. |

Kelvin es la unidad de temperatura usada; no presentamos esos números como grados Celsius. El período es el tiempo de una órbita. Para cada categoría necesitamos su magnitud válida y su indicador de valor puntual. Los extremos térmicos excluyen además métodos desconocidos e `Imaging`, según las reglas implementadas en la API. Conservamos la advertencia sobre las distintas procedencias de la masa catalogada.

Un planeta puede ser simultáneamente Relámpago e Infierno. Por eso no usamos un gráfico circular ni barras apiladas para presentarlos como partes excluyentes de un total. `planetas_con_extremos` cuenta una sola vez cada planeta que cumple al menos una condición; sumar las cuatro categorías puede producir un número superior.

La primera tabla muestra casos, evaluables y porcentaje por criterio:

```python
100 * casos / disponibles if disponibles else None
```

Aplicamos esa operación mediante una comprensión de lista. `zip` empareja el conteo y su denominador de cada fila. Si hay cero evaluables, devolvemos `None`, porque dividir entre cero no produce un porcentaje interpretable. Cada criterio tiene su propio denominador: conocer el período no implica conocer la temperatura o la masa.

Después `st.selectbox` permite elegir un extremo para comparar sus **conteos** entre métodos. Las barras horizontales facilitan leer esas categorías. Para acompañarlas seleccionamos las dos columnas necesarias de casos y evaluables, renombramos el método y usamos `merge(..., on="Método", how="left")`. Esto une las filas por el nombre del método y conserva los grupos de la tabla de casos. Si faltara un denominador, `pd.notna` lo detecta; también exigimos que sea mayor que cero antes de dividir.

La tabla resultante permite comparar cantidades y proporciones. Por ejemplo, 20 casos entre 100 evaluables son 20 %, mientras que 10 entre 20 son 50 %. Más casos absolutos no significa mayor proporción. Cuando los grupos tienen tamaños distintos necesitamos ambas cifras para defender la interpretación.

### El catálogo: páginas, detalles y descarga

`mostrar_catalogo(filtros, resumen)` usa un `selectbox` para elegir 25, 50 o 100 registros por página. Calcula `max(1, math.ceil(resumen["total"] / cantidad))`: `ceil` redondea hacia arriba y `max` mantiene una página seleccionable incluso si no hay coincidencias. Por ejemplo, 51 registros a 25 por página requieren tres páginas. No rellenamos la última con registros inventados.

Si el tamaño elegido reduce el número de páginas, ajustamos `session_state["pagina"]` antes de crear el widget. Así una página que antes era válida no queda fuera del intervalo. `st.number_input` permite escoger un entero entre 1 y el máximo.

```python
parametros = dict(filtros)
parametros.update({"pagina": int(pagina), "por_pagina": cantidad})
respuesta = pedir_api("/datos", parametros=parametros)
```

`dict(filtros)` copia el diccionario. Añadimos paginación a esa copia para no convertirla en parte de los filtros generales usados en estadísticas e IA. `int` asegura un entero. Si falla GET `/datos`, `return` termina esta función. Si hay resultados, `preparar_tabla` selecciona identificación, método, año, principales magnitudes y fuente; `st.dataframe` los presenta. La leyenda compara filas visibles, página y total real de coincidencias devuelto por la API.

El botón de descarga entrega **esa página y esas columnas visibles**:

```python
data=tabla.to_csv(index=False).encode("utf-8-sig")
```

`to_csv` construye texto separado por comas; `index=False` evita una columna adicional con el índice de pandas. `encode("utf-8-sig")` genera bytes UTF-8 con una marca inicial que facilita reconocer los acentos en programas como Excel. `file_name` incluye la página y `mime="text/csv"` identifica el tipo de archivo. El botón no exporta automáticamente toda la selección ni todos los campos ocultos.

El desplegable «Consultar todos los campos de esta página» sí muestra la normalización completa de esos mismos registros, sin limitar sus columnas. Si no hay registros, mostramos un mensaje. Que el selector conserve página 1 no significa que exista una fila.

El segundo desplegable muestra distribuciones de **toda la selección**, tomadas del resumen. Las barras por método comparan conteos categóricos. Para los años ordenamos con `sort_values("Año")` y usamos `st.line_chart`: el orden temporal permite seguir las diferencias entre años. Se cuentan registros actuales con año conocido; la gráfica no reconstruye cuánto contenía el archivo en cada fecha histórica y el año en curso puede estar incompleto.

### Crear un registro manual desde el formulario

#### `campo_medida`: repetir una regla sin duplicar instrucciones

Esta función construye una entrada numérica opcional y, cuando corresponde, su indicador. `etiqueta` es el texto visible y `clave` ayuda a generar identificadores distintos con `f"nuevo_{clave}"` y `f"indicador_{clave}"`. Si reutilizáramos una misma clave para radio y masa, no estaríamos identificando correctamente dos campos diferentes.

`st.number_input` usa `value=None` para comenzar vacío, `min_value=0.0`, `step=0.01` y `format="%.6f"`. El paso regula el incremento de sus controles; el formato muestra seis decimales. Esa presentación no acredita precisión científica. Aunque el widget admite cero, la validación posterior exige que una magnitud informada sea estrictamente positiva.

Si `con_indicador` es verdadero, añadimos el selector y traducimos su etiqueta con `INDICADORES[opcion]`. Su opción inicial es desconocido. Si es falso, el indicador queda en `None`. `return valor, indicador` devuelve una tupla de dos elementos; la asignación `radio, limite_radio = campo_medida(...)` los desempaqueta en dos variables. En distancia y densidad escribimos `distancia, _` o `densidad, _`: `_` señala que no utilizaremos ese segundo resultado.

#### `mostrar_formulario`: campos y envío completo

Agrupamos todas las entradas en `st.form("nuevo_registro")`; escribirlas no crea registros. Dos columnas organizan los cuatro campos obligatorios:

| Campo | Implementación |
|---|---|
| Planeta | Texto de hasta 150 caracteres. |
| Estrella | Texto de hasta 150 caracteres. |
| Método | Selector con «Seleccionar» y los métodos disponibles; alternativamente, texto de hasta 100 caracteres para otro método. |
| Año | Número entero entre 1 y el año actual, inicialmente el año actual. |

Los desplegables organizan todos los campos opcionales:

| Grupo | Datos incluidos |
|---|---|
| Tamaño y energía | Radio en radios terrestres, insolación relativa a la Tierra, sus indicadores y referencia del radio de hasta 2.000 caracteres. |
| Distancia y órbita | Distancia al sistema en parsecs y período en días; el período tiene indicador. |
| Temperatura, masa y otros | Temperatura en kelvin y masa en masas terrestres con indicadores; densidad en g/cm³; lugar del descubrimiento y procedencia de la masa, ambos de hasta 100 caracteres. |

«Guardar registro», creado con `st.form_submit_button`, es de tipo `primary` para destacarlo. Si no se pulsó, `if not enviar: return` evita la validación y el POST, pero los widgets ya se dibujaron.

Al enviar, `otro_metodo.strip() or (...)` da prioridad al método escrito. Si no hay uno, usamos el seleccionado salvo que siga en «Seleccionar». Comprobamos que planeta, estrella y método contengan texto. El año ya está restringido por el widget y también será validado por la API.

Construimos `magnitudes`, un diccionario con las siete medidas. `for campo, valor in magnitudes.items()` recorre cada nombre y valor. Una magnitud vacía puede seguir siendo `None`; una informada debe pasar `math.isfinite(valor)` y ser mayor que cero. Si falla, mostramos el campo y terminamos sin enviar. Después construimos `indicadores` con los cinco indicadores disponibles.

El cuerpo final combina identificación, textos opcionales, medidas e indicadores:

```python
"lugar_descubrimiento": lugar.strip() or None,
"tipo_masa": tipo_masa.strip() or None,
"referencia_radio": referencia.strip() or None,
**magnitudes, **indicadores,
```

Un texto opcional vacío se convierte en `None`. `**` incorpora las parejas de un diccionario dentro de otro; así no tenemos que repetir todas sus asignaciones. Al enviarlo como JSON, `None` se representa como `null`. No transformamos desconocidos en ceros físicos ni asignamos por defecto el indicador puntual a cualquier número.

`pedir_api("/datos", registro=registro)` hace POST. La API vuelve a validar y decide la procedencia manual; el formulario no puede declararlo parte del catálogo NASA. La validación del servidor también funciona cuando alguien utiliza `/docs` sin pasar por esta interfaz. Si la API rechaza el registro, mostramos el error y no anunciamos éxito.

#### Después de guardar: sincronizar lo que vemos y lo que consultamos

Cuando recibimos una respuesta satisfactoria, guardamos `mensaje_exito` y `buscar_recien_creado` en la sesión y llamamos a `st.rerun()`. Esta llamada interrumpe la ejecución actual y vuelve a comenzar el archivo.

En la siguiente ejecución, antes de crear la barra lateral, encontramos ese nombre pendiente. Eliminamos la respuesta de IA, establecemos filtros por nombre y procedencia manual, sincronizamos sus widgets, quitamos el método específico, desactivamos candidatos e intervalo de años y volvemos a página 1. Hacerlo antes de crear los widgets permite que su estado inicial coincida con la nueva selección.

Así evitamos que un filtro anterior oculte el registro que acabamos de crear. Mostramos el mensaje de éxito con `pop`, por lo que se consume una sola vez. Las opciones vuelven a consultarse y pueden incluir el nuevo método. El código no borra automáticamente todos los campos del formulario; no debemos describirlo como si lo hiciera. La búsqueda por nombre usa las reglas generales de la API, por lo que la selección puede incluir otras coincidencias de ese texto.

### La interfaz de Gemini: una pregunta sobre la selección

`mostrar_ia(filtros)` explica el alcance del asistente y usa otro formulario. `st.text_input` admite hasta 1.000 caracteres, se identifica como `pregunta_ia` y muestra un ejemplo con `placeholder`. El texto orientativo no es una pregunta enviada automáticamente.

Al pulsar «Preguntar», primero eliminamos la respuesta anterior. Si `pregunta.strip()` queda vacía, mostramos una advertencia. De lo contrario, `st.spinner("Pensando...")` indica que esperamos la operación:

```python
resultado = pedir_api(
    "/preguntar", parametros=filtros,
    registro={"pregunta": pregunta.strip()}, espera=60,
)
```

La API recibe filtros y pregunta. Es el backend el que reúne las estadísticas de toda la selección, hasta 30 ejemplos y las instrucciones para Gemini. Las 30 filas de contexto no sustituyen las estadísticas generales y tampoco equivalen necesariamente a la página visible. Para consultar un planeta concreto, primero filtramos por su nombre y aplicamos los filtros, como indica la propia pantalla.

Al volver, comprobamos que `resultado["respuesta"]` sea texto no vacío. Guardamos en `session_state["respuesta_ia"]` la pregunta respondida, una copia de los filtros y los datos devueltos mediante `**resultado`. Luego mostramos la pregunta, la respuesta y una leyenda con modelo, número de registros resumidos y cantidad de ejemplos. Esa información permite conocer el alcance de la respuesta y contrastarla con las tablas.

Solo mostramos la respuesta guardada cuando sus filtros coinciden con los actuales. Así otra ejecución provocada por cambiar la página o una medida gráfica no vuelve a consultar Gemini ni borra innecesariamente la respuesta. Sin embargo, se elimina al aplicar filtros válidos, actualizar datos, registrar un planeta y activar su selección, o enviar otra pregunta, incluso si esa nueva consulta falla.

**Esto conserva una respuesta en la sesión; no implementa memoria conversacional.** Cada petición contiene la pregunta actual, no un historial de intercambios. Tampoco almacena un chat en MongoDB ni utiliza un caché de contexto de Google. Escribir otra pregunta sin enviarla no genera una respuesta nueva: la pantalla identifica expresamente cuál fue la pregunta respondida. Los límites de conocimiento y las instrucciones del asistente pertenecen al backend; esta función no convierte la pregunta en código ejecutable ni modifica el catálogo.

### Dos recorridos completos para explicar en la sustentación

#### De un filtro a una barra

1. Elegimos un método en la barra lateral. Todavía no cambia la selección activa porque está dentro de un formulario.
2. Pulsamos «Aplicar filtros»; Streamlit vuelve a ejecutar el archivo con los valores enviados.
3. Validamos el intervalo, construimos el diccionario de filtros, lo guardamos y reiniciamos la página y la respuesta de IA.
4. `pedir_api` hace GET `/estadisticas` con esos parámetros. La API construye la consulta, consulta MongoDB, normaliza y calcula el resumen completo.
5. El JSON vuelve y `respuesta.json()` lo transforma en un diccionario de Python.
6. `mostrar_preguntas` construye DataFrames a partir de las listas y conteos recibidos. `st.bar_chart` toma la columna categórica y la numérica para dibujar sus barras.
7. El catálogo hace además GET `/datos` con los mismos filtros y su propia paginación. Por eso una tabla puede tener 25 filas mientras una barra resume muchas más.

#### De un formulario a un planeta visible

1. Escribimos los campos y pulsamos «Guardar registro»; la interfaz verifica obligatorios y magnitudes.
2. Construimos el diccionario y hacemos POST `/datos`. La API valida de nuevo, comprueba duplicados y guarda el registro manual.
3. Con la respuesta satisfactoria conservamos un mensaje y el nombre, y llamamos a `st.rerun()`.
4. Al comenzar de nuevo, consultamos opciones y sincronizamos filtros y widgets con ese nombre y procedencia manual.
5. Volvemos a pedir estadísticas y la página del catálogo. Ahora podemos revisar el dato guardado y comprobar su fuente.

Si el profesor pregunta «¿por qué una gráfica cambió al agregar un registro?», respondemos que las cifras dependen de los documentos consultados y de la selección activa; después de crear, la aplicación cambia deliberadamente esa selección para facilitar la comprobación. Si pregunta «¿el dashboard guarda los datos?», aclaramos que envía la solicitud, mientras la API valida y escribe en MongoDB. Si pregunta «¿la gráfica calcula sola?», señalamos la separación entre el cálculo del resumen, la preparación del DataFrame y el componente que lo dibuja.

<a id="gemini"></a>

## 6. Gemini: contexto, solicitud, respuesta y límites

### Cómo incorporamos Gemini al proyecto

La función **«Pregúntale a tus datos»** permite escribir una pregunta en español y recibir una explicación construida a partir de la selección actual del catálogo. Conservamos la idea que presentó el profesor: un formulario de Streamlit envía un `POST` a nuestra API, y nuestra API envía otro `POST` a Gemini mediante `requests`. No instalamos un SDK de Google ni una biblioteca adicional de inteligencia artificial. Un SDK es un conjunto de herramientas específico de un proveedor; aquí practicamos directamente las peticiones HTTP que ya utilizamos en el proyecto.

La implementación se encuentra en las funciones `preguntar`, `registro_para_ia` y `extraer_respuesta_ia` de [api.py](api.py), y en `mostrar_ia` de [dashboard.py](dashboard.py). El modelo proporciona la redacción; las cifras y reglas del análisis se preparan en nuestro código. Esto permite explicar de dónde sale una respuesta y contrastarla con las tablas.

#### Qué puede razonar y qué información recibe

Gemini tiene capacidad general de razonamiento. Nuestra integración limita las fuentes que debe utilizar: descripción del proyecto, criterios científicos definidos, estadísticas calculadas y algunos registros del catálogo. No configuramos búsqueda en Internet, ejecución de código, consultas autónomas a MongoDB ni herramientas para obtener información adicional.

Por eso puede explicar una conclusión derivada de los datos. Ante «¿Crees que podremos llegar a un planeta parecido a la Tierra?», puede relacionar las distancias y los tiempos de viaje calculados a 17 km/s, y explicar lo que implica ese supuesto. No dispone en este contexto de evidencia suficiente para predecir tecnologías futuras ni para afirmar que un planeta es habitable. Una respuesta adecuada debe separar el resultado numérico, la inferencia y aquello que no se puede concluir.

Tampoco basta que Gemini conozca un planeta por su entrenamiento previo. Las instrucciones le piden responder con el contexto enviado y reconocer lo que falta. Estas instrucciones reducen respuestas ajenas al proyecto, pero no convierten al modelo en una calculadora infalible: comprobamos sus cifras en las estadísticas.

No entrenamos ni afinamos el modelo con nuestra base de datos. En cada petición enviamos contexto como parte de la entrada. La aplicación tampoco implementa una conversación acumulada: no envía las preguntas anteriores ni sus respuestas. Conservar el último resultado visible en Streamlit no equivale a darle memoria al modelo.

#### Cómo validamos la pregunta

El cuerpo JSON esperado es, por ejemplo:

```json
{
  "pregunta": "¿Cuántos planetas cumplen ambos criterios?"
}
```

La clase `Pregunta` declara el contrato de entrada:

```python
class Pregunta(BaseModel):
    pregunta: str = Field(min_length=1, max_length=1000)

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "pregunta": "¿Cuántos planetas cumplen ambos criterios?"
            }
        },
    )
```

`BaseModel` pertenece a Pydantic, la biblioteca de validación utilizada por FastAPI. `str` exige texto; `Field` establece entre 1 y 1.000 caracteres. `str_strip_whitespace` elimina espacios al principio y al final antes de validar, de modo que una cadena de espacios no constituye una pregunta válida. `extra="forbid"` rechaza propiedades no declaradas, y `json_schema_extra` proporciona el ejemplo mostrado en Swagger. Este ejemplo documenta el formato; no responde automáticamente esa pregunta. Una solicitud que incumple el modelo devuelve `422` antes de llamar a Google.

La ruta se declara con `@app.post("/preguntar")`. Los filtros entran mediante `Depends(recibir_filtros)`, igual que en las consultas del catálogo; la pregunta entra por el cuerpo JSON. Usamos `POST` para enviar ese cuerpo y solicitar una generación. Este `POST` no crea un planeta: la operación de crear registros corresponde a otra ruta.

#### Cómo construimos el contexto de datos

Primero comprobamos `GEMINI_API_KEY`. Si falta, devolvemos `503` con un mensaje de configuración. Así el resto de la aplicación puede funcionar sin IA y la falta de clave no se confunde con un problema de MongoDB.

Después reutilizamos dos funciones existentes:

```python
resumen = estadisticas(filtros)
pagina = listar_datos(pagina=1, por_pagina=30, filtros=filtros)
muestra = [registro_para_ia(registro) for registro in pagina["datos"]]
```

Son llamadas a funciones de Python dentro del mismo proceso, no peticiones HTTP de la API a sí misma. Ambas reciben los mismos filtros, por lo que la IA analiza la selección que el usuario está viendo. `resumen` contiene las estadísticas de **todos los documentos seleccionados**; `muestra` contiene hasta 30 registros para aportar detalles concretos. La lista se ordena por `planeta` y después por `_id`, y se toma la primera página. No es una muestra aleatoria ni se afirma que sea representativa.

Esta distinción evita un error importante: si hay 6.375 documentos seleccionados, no podemos contar los métodos de esos 30 y anunciar que ese resultado describe todo el catálogo. Para totales, porcentajes, comparaciones y extremos, las instrucciones ordenan utilizar el resumen completo. Además, que un planeta no aparezca entre los 30 no demuestra que no exista. Para preguntar por uno concreto, conviene filtrar primero por su nombre.

`registro_para_ia` reduce cada documento a campos útiles: planeta, estrella, método y año de descubrimiento, tipo de masa, los siete campos numéricos normalizados y los cinco indicadores de límites. Incluye únicamente el nombre de la fuente, y agrega `distancia_anios_luz`, `viaje_anios` y `origen_radio` cuando están presentes. Se omiten `_id`, las referencias extensas y otros datos que no necesita la explicación. La misma reducción se aplica a los planetas cercanos incluidos en el resumen.

El contexto también contiene las reglas que emplea el programa: intervalos de radio e insolación, condiciones de validez, conversión de pársecs a años luz, velocidad hipotética del viaje, comparación de distancias por método y definiciones de las categorías extremas. Así la IA recibe tanto el resultado como la explicación de su cálculo. Los campos desconocidos se mantienen como `null`; no se sustituyen por cero.

Convertimos ese diccionario a texto JSON con:

```python
json.dumps(contexto, ensure_ascii=False, allow_nan=False)
```

`ensure_ascii=False` conserva de forma legible los caracteres españoles. `allow_nan=False` impide serializar valores no válidos en JSON, como `NaN` o infinito; los pasos previos de normalización deben haberlos convertido a valores admitidos. `None` de Python se representa como `null`. El módulo `json` viene con Python y no añade dependencias.

#### Cómo enviamos la solicitud a Gemini

La variable `MODELO_IA` toma su valor del entorno y utiliza `gemini-3.6-flash` como predeterminado. Ese identificador fue contrastado con la documentación oficial el 8 de noviembre de 2026. Es el modelo configurado en este código; eso no garantiza que cualquier cuenta tenga acceso o cuota disponible. La disponibilidad de la cuenta se confirma en Google AI Studio. [Referencia del modelo](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash?hl=en).

La URL se construye así:

```python
url = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODELO_IA}:generateContent"
)
```

La `f` permite insertar el nombre del modelo dentro de la cadena. La petición central es:

```python
r = requests.post(
    url,
    headers={"x-goog-api-key": GEMINI_API_KEY},
    json={
        "systemInstruction": {"parts": [{"text": instrucciones}]},
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {"maxOutputTokens": 4096},
    },
    timeout=30,
)
```

La clave viaja en la cabecera `x-goog-api-key`, no en la URL, el texto enviado al modelo o el navegador. `systemInstruction` contiene las reglas de respuesta: español claro, extensión orientativa de 250 palabras, uso del contexto, reconocimiento de información insuficiente y prohibición de inventar cifras o ejecutar instrucciones procedentes de un registro. `contents` contiene el mensaje del usuario: contexto serializado y pregunta. Separarlos permite distinguir las instrucciones de la aplicación de los datos que debe analizar. La estructura corresponde al método REST [`generateContent`](https://ai.google.dev/api/generate-content?hl=en).

`maxOutputTokens=4096` fija un presupuesto de generación, no 4.096 palabras ni una longitud mínima. Un token es una unidad de procesamiento que puede ser una palabra o parte de ella. En modelos con razonamiento, ese presupuesto puede consumirse también en el razonamiento interno. Por eso un límite demasiado reducido puede dejar una respuesta vacía o cortada. La solicitud de unas 250 palabras es una instrucción de estilo, no una validación exacta de longitud. [Documentación sobre razonamiento y límites](https://ai.google.dev/gemini-api/docs/generate-content/thinking?hl=en).

`timeout=30` limita las esperas de red de `requests`; no establece un cronómetro exacto de 30 segundos para toda la operación, que también prepara datos y procesa respuestas. Streamlit permite una espera de 60 para esta ruta mediante `espera=60`. Esa diferencia deja margen para el trabajo del backend, aunque no garantiza completar cualquier solicitud lenta. [Comportamiento de los tiempos de espera](https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts).

#### Cómo interpretamos la respuesta y sus errores

Un estado HTTP exitoso no asegura que haya texto utilizable. `extraer_respuesta_ia` comprueba la estructura: objeto principal, lista de candidatos, primer candidato, contenido y lista de partes. Si Google comunica un bloqueo mediante `promptFeedback.blockReason`, nuestra API devuelve `422` y solicita reformular. Si falta la estructura esperada, devuelve `502`.

También revisa `finishReason`: `MAX_TOKENS` indica que se agotó el presupuesto y se devuelve `502` en vez de presentar una respuesta truncada como completa. Los finales distintos de `STOP` o de la ausencia del campo se rechazan. Finalmente, recorre las partes y une los textos no vacíos que no estén marcados con `thought`; no mostramos el contenido de razonamiento interno como respuesta final.

El manejo de errores distingue las causas sin reproducir el cuerpo completo de Google o excepciones que puedan contener datos sensibles:

| Situación detectada | Código de nuestra API | Qué significa para el usuario |
|---|---:|---|
| Falta `GEMINI_API_KEY` | 503 | Debe configurarse la clave en el backend. |
| Google devuelve 400 | 503 | Revisar configuración de clave, modelo o solicitud. |
| Google devuelve 401 o 403 | 503 | Revisar validez y permisos de la clave. |
| Google devuelve 404 | 503 | Revisar el identificador y acceso al modelo. |
| Google devuelve 429 | 429 | Se alcanzó un límite de cuota o solicitudes. |
| Se agota la espera a Google | 504 | El proveedor no respondió dentro de la espera permitida. |
| Problema de red, JSON inválido u otro fallo del proveedor | 502 | No se obtuvo una respuesta utilizable. |
| Pregunta inválida o bloqueo comunicado por el proveedor | 422 | Revisar o reformular la entrada. |

Cuando todo funciona, devolvemos `respuesta`, `modelo`, `total_registros` y `tamano_muestra`. Los dos últimos valores permiten distinguir el alcance del resumen de la cantidad de ejemplos enviados. No guardamos la pregunta o la respuesta en MongoDB ni ejecutamos código generado por el modelo.

#### Cómo lo presenta Streamlit

`mostrar_ia` utiliza `st.form`, un campo de texto con máximo de 1.000 caracteres y el botón **Preguntar**. El formulario agrupa la entrada: escribir no dispara una petición por cada carácter. Al enviarlo, elimina la respuesta anterior, revisa si la pregunta está vacía, muestra el indicador **Pensando...** y llama a `pedir_api("/preguntar", ...)` con los filtros actuales y el cuerpo JSON.

Si llega una respuesta válida, `st.session_state` conserva la pregunta, una copia de los filtros y el resultado. La interfaz muestra el texto, el modelo, el total seleccionado y el tamaño de la muestra. Solo muestra ese resultado si sus filtros coinciden con los actuales. Aplicar otros filtros, actualizar datos o seleccionar automáticamente un nuevo registro manual limpia la respuesta anterior, para evitar explicar una selección que ya cambió. Este estado pertenece a la sesión del usuario; no es un historial persistente compartido.

<a id="despliegue"></a>

## 7. Instalación, configuración y despliegue

### Librerías, versiones y archivos de configuración

En [requirements.txt](requirements.txt) fijamos las siete dependencias directas del proyecto. `==` significa instalar la versión indicada, para reducir diferencias entre máquinas. La verificación se realizó con Python 3.12, versión declarada en [.python-version](.python-version).

| Dependencia | Versión fijada | Función dentro del proyecto |
|---|---|---|
| `pymongo` | 4.19.0 | Conectar Python con MongoDB, consultar e insertar documentos. |
| `pandas` | 3.1.0 | Preparar las tablas y series que la interfaz muestra y grafica. |
| `fastapi` | 0.162.0 | Definir rutas, parámetros, validaciones y documentación HTTP. |
| `uvicorn` | 0.54.0 | Ejecutar el servidor que atiende las solicitudes a FastAPI. |
| `streamlit` | 1.66.1 | Construir filtros, tablas, gráficas y formularios de la interfaz. |
| `requests` | 2.34.2 | Comunicar el dashboard con la API y la API con Gemini. |
| `python-dotenv` | 1.2.4 | Leer la configuración local desde `.env`. |

Pydantic y `certifi` también aparecen en el código, pero llegan como dependencias transitivas: FastAPI utiliza Pydantic y Requests incorpora `certifi`. No agregamos otras bibliotecas directas para resolver la IA. `os`, `json`, `math`, `re`, `datetime`, `statistics`, `typing` y `pathlib` forman parte de Python.

Un archivo con variables de entorno separa la configuración del programa. El mismo código puede conectarse a un MongoDB de trabajo local o ejecutarse en Render cambiando valores, sin escribir contraseñas dentro de `api.py`. [.env.example](.env.example) documenta los nombres y valores iniciales; la copia `.env` contiene los valores privados de cada instalación.

| Variable | Dónde se utiliza | Qué configuramos |
|---|---|---|
| `MONGO_URI` | API | Cadena de conexión entregada por Atlas. |
| `MONGO_DB` | API | `proyecto_segundo_corte`, salvo que la base real tenga otro nombre. |
| `MONGO_COLLECTION` | API | Colección específica; vacía permite buscar una colección conocida con registros. |
| `API_BASE_URL` | Dashboard | Dirección del backend, local o pública. |
| `GEMINI_API_KEY` | API | Clave de Google AI Studio. |
| `MODELO_IA` | API | `gemini-3.6-flash` en esta implementación. |

### Cómo ejecutar el proyecto en un Mac

#### Preparar Python y el entorno virtual

Abrimos una terminal dentro de la carpeta que contiene `api.py`, `dashboard.py` y `requirements.txt`. Si el nombre tiene espacios, escribimos la ruta entre comillas; por ejemplo, `cd "/Users/tu_usuario/Desktop/First API"`, sustituyendo el usuario por el real. Comprobamos la versión disponible:

```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

El entorno `venv` separa las bibliotecas de este proyecto de otras instalaciones. Debe crearse con Python 3.12 para reproducir el entorno validado; si `python3` apunta a otra versión, utilizamos el ejecutable de Python 3.12 instalado. `source` activa el entorno **en esa terminal**; no crea la carpeta. Por eso aparece `source: no such file or directory: venv/bin/activate` cuando aún no se creó o estamos en otro directorio.

`python -m pip` instala paquetes con el mismo intérprete que utilizaremos para ejecutar. Un `venv` recién creado todavía no contiene Streamlit: hay que instalar `requirements.txt`. Esta es la explicación del error `No module named streamlit` que ocurrió durante el montaje. La carpeta del entorno no se sube a GitHub; cada instalación la reconstruye. [Documentación de entornos virtuales](https://docs.python.org/3/library/venv.html).

#### Configurar las variables sin mezclar formatos

Si todavía no existe `.env`, copiamos `.env.example` con ese nombre y completamos sus valores. No sustituimos una configuración ya existente sin revisarla. En `.env` podemos escribir cadenas entre comillas:

```dotenv
MONGO_URI="mongodb+srv://USUARIO:CLAVE@HOST/"
MONGO_DB=proyecto_segundo_corte
MONGO_COLLECTION=
API_BASE_URL=http://localhost:8000
GEMINI_API_KEY="CLAVE_PRIVADA_DE_GOOGLE"
MODELO_IA=gemini-3.6-flash
```

`USUARIO`, `CLAVE`, `HOST` y `CLAVE_PRIVADA_DE_GOOGLE` son marcadores de ejemplo, no credenciales funcionales. `python-dotenv` interpreta las comillas. En cambio, si Render presenta campos separados de nombre y valor, pegamos solo el valor, sin `MONGO_URI=` y sin agregar comillas literales. Las comillas del código Python, las de `.env` y las de una interfaz de configuración pertenecen a contextos distintos.

La API carga `.env` junto a `api.py`. Las variables que ya proporciona el entorno tienen prioridad sobre la lectura habitual de `load_dotenv`; por ello un valor antiguo configurado fuera del archivo puede explicar que editarlo no cambie la conexión. Reiniciamos los procesos después de modificar sus variables.

#### Mantener los dos procesos en funcionamiento

En la primera terminal, con el entorno activo:

```bash
python -m uvicorn api:app --reload
```

`api:app` significa importar el archivo `api.py` y servir el objeto llamado `app`. `--reload` reinicia el servidor cuando editamos código durante el desarrollo. La dirección local habitual es `http://localhost:8000`, y Swagger se abre en `http://localhost:8000/docs`.

En una segunda terminal entramos en la misma carpeta y ejecutamos:

```bash
source venv/bin/activate
python -m streamlit run dashboard.py
```

Streamlit utiliza habitualmente `http://localhost:8501`. La terminal de la API debe seguir abierta: el dashboard necesita solicitarle datos. `Control+C` detiene el proceso de la terminal activa. Activar el entorno en la primera ventana no lo activa automáticamente en la segunda.

La comprobación útil es abrir primero `/salud`: verifica la conexión con los datos. Abrir `/` únicamente comprueba que la API puede responder con su información básica. Si `/salud` funciona y el dashboard falla, revisamos `API_BASE_URL` y el proceso de Streamlit antes de cambiar la URI de MongoDB.

#### Qué resolvió el problema de certificados en macOS

En este proyecto `certifi.where()` aporta el archivo de autoridades certificadoras usado para verificar TLS cuando la URI comienza con `mongodb+srv://`. Ese archivo ayuda a comprobar que nos conectamos a un servidor con un certificado válido. No es un servidor intermediario ni un proxy, y no desactiva la verificación del certificado.

La validez de la URI, la contraseña, los permisos de Atlas, la red y la confianza en certificados son comprobaciones diferentes. Una URI correctamente escrita puede fallar por otra de ellas. No solucionamos un error de certificado agregando comillas al azar ni desactivando TLS. El código existente conserva la validación y especifica el conjunto de certificados.

### Cómo publicamos la aplicación

#### Qué ejecuta cada plataforma

MongoDB Atlas conserva los documentos. Render ejecuta `api.py` mediante Uvicorn. Streamlit Community Cloud ejecuta `dashboard.py` y presenta la interfaz. GitHub conserva el código y su historial. Google procesa las peticiones de IA que realiza el backend con contexto limitado.

| Recurso publicado | Dirección |
|---|---|
| Dashboard | <https://exoplanetasproyecto.streamlit.app/> |
| API | <https://exoplanetas-api-juanfmarbo.onrender.com> |
| Swagger | <https://exoplanetas-api-juanfmarbo.onrender.com/docs> |
| Salud y conexión | <https://exoplanetas-api-juanfmarbo.onrender.com/salud> |

Estas son las direcciones del despliegue registrado; que estén anotadas no constituye una comprobación permanente de disponibilidad. Para mostrarlas al profesor conviene abrirlas antes de la exposición. No necesitamos publicar un puerto desde Visual Studio Code para utilizar estas aplicaciones alojadas: cada plataforma ya ofrece una URL HTTPS.

`localhost` siempre identifica la máquina donde se ejecuta la solicitud. En el dashboard público sería el servidor de Streamlit, no nuestro Mac ni el servidor de Render. Por eso el valor público de `API_BASE_URL` debe ser la URL HTTPS de Render, sin añadir `/docs`, `/datos` o `/salud` al final.

#### Configuración de Render y significado de render.yaml

El servicio existente se llama `exoplanetas-api-juanfmarbo`. Sus comandos documentados son:

```bash
python -m pip install -r requirements.txt
```

para instalar, y:

```bash
python -m uvicorn api:app --host 0.0.0.0 --port $PORT
```

para arrancar. `0.0.0.0` permite escuchar en las interfaces de red del servicio; `$PORT` toma el puerto suministrado por Render. La URL pública no tiene que mostrar ese puerto interno. En producción no utilizamos `--reload`.

[render.yaml](render.yaml) describe una configuración reproducible: servicio web Python, rama `main`, plan Free, región Virginia, comandos, variables y una ruta de comprobación `/`. `sync: false` indica que el valor de la variable debe aportarse de forma privada; no escribe la clave en el archivo.

La existencia del YAML no significa que el servicio actual esté administrado automáticamente por un Blueprint. El servicio ya fue creado y hay que consultar sus ajustes reales. En la verificación del 8 de noviembre se registró una comprobación TCP por defecto, mientras que la plantilla propone HTTP en `/`. Ninguna de ellas equivale por sí sola a confirmar MongoDB: para eso utilizamos `/salud`. [Tipos de comprobaciones de Render](https://render.com/docs/health-checks).

#### Configuración de Streamlit y de la clave de Gemini

En Streamlit Community Cloud seleccionamos el repositorio `Juanfmarbo/First-API`, la rama correspondiente y `dashboard.py` como archivo principal. En **Secrets** se usa TOML; allí los textos sí llevan comillas. La variable debe estar en la raíz:

```toml
API_BASE_URL = "https://exoplanetas-api-juanfmarbo.onrender.com"
```

No la encerramos bajo una sección `[api]`, porque el código la lee mediante `os.getenv("API_BASE_URL", ...)`. Streamlit expone las claves de la raíz como variables de entorno; las tablas anidadas se manejan de otra forma. [Secretos y variables de entorno de Streamlit](https://docs.streamlit.io/develop/concepts/connections/secrets-management).

La clave de Gemini se obtiene en [Google AI Studio](https://aistudio.google.com/apikey) y se configura como `GEMINI_API_KEY` en el **backend**: `.env` si la API es local o Environment del servicio de Render si es pública. Ponerla solo en Streamlit no permite que la API de Render la lea. Después guardamos la configuración y verificamos que el servicio activo la haya cargado.

La última comprobación funcional registrada, el **8 de noviembre de 2026**, confirmó que la pestaña estaba publicada pero la API respondía que faltaba configurar `GEMINI_API_KEY`. Esa observación está fechada: no presentamos como comprobada una respuesta real de Gemini mientras no exista una verificación posterior con la clave configurada. El catálogo, las gráficas y la creación de registros pueden funcionar independientemente de ese extra.

#### Actualizaciones, arranque lento y entorno de desarrollo remoto

Actualizar GitHub y actualizar un servicio son acciones relacionadas pero diferentes. El 8 de noviembre el cambio no produjo automáticamente el nuevo despliegue y se realizó uno manual en el servicio existente. Después de cambiar código verificamos el commit desplegado y que el estado sea **Live**. Render documenta que los despliegues automáticos requieren un proveedor Git conectado; un repositorio enlazado por URL pública necesita despliegues manuales. No basta suponerlo por haber ejecutado `git push`. [Despliegues de Render](https://render.com/docs/deploys).

Para cambios exclusivamente documentales se puede incluir `[skip render]` en el mensaje del commit y evitar una reconstrucción automática innecesaria. Esto no elimina el commit ni impide leer los nuevos Markdown en GitHub. Borrar guías antiguas mediante un commit ordinario las retira de la versión actual, pero conserva su contenido en las revisiones históricas.

Según la documentación consultada el 10 de noviembre de 2026, un servicio Free de Render puede detenerse después de 15 minutos sin tráfico y tardar aproximadamente un minuto en arrancar al recibir otra petición. Streamlit Community Cloud también puede hibernar una aplicación tras 12 horas sin tráfico y mostrar una opción para reactivarla. Antes de la sustentación, abrimos primero la API y luego el dashboard; una pantalla de arranque no demuestra por sí sola que la URI esté mal. [Render Free](https://render.com/docs/free) · [Hibernación de Streamlit](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app).

La carpeta [.devcontainer](.devcontainer/devcontainer.json) contiene una plantilla para trabajar con VS Code/Codespaces dentro de un contenedor. Es un entorno de desarrollo, independiente de los dos servicios públicos. Su imagen actual utiliza Python 3.11, aunque la versión validada del proyecto es 3.12; además ejecuta un segundo comando `pip3 install --user streamlit` sin indicar una versión. Ese comando no solicita explícitamente una actualización y puede conservar la versión ya instalada. La diferencia comprobada es Python 3.11 frente al entorno validado 3.12; no afirmamos que la plantilla lo reproduzca exactamente.

Su arranque automático inicia únicamente el dashboard y reenvía el puerto 8501. Para obtener datos necesitaría una `API_BASE_URL` pública o iniciar también la API. El comando existente desactiva CORS y protección XSRF para esa vista de desarrollo; esos indicadores no forman parte del comando de producción descrito aquí ni deben presentarse como requisitos del despliegue. La documentación describe el archivo tal como existe, sin cambiarlo durante la reorganización.

### Manejo de credenciales y alcance de seguridad

[.gitignore](.gitignore) excluye `.env`, otras variantes de ese archivo, `secrets.toml`, entornos virtuales, cachés, registros y archivos locales del editor. La excepción `!.env.example` permite compartir la plantilla vacía. Un archivo ignorado que ya estuviera bajo seguimiento no desaparece automáticamente del repositorio, y la regla tampoco borra revisiones anteriores. [Comportamiento de gitignore](https://git-scm.com/docs/gitignore).

MongoDB y Gemini se conectan desde el servidor. El dashboard necesita la dirección de nuestra API, no sus credenciales. A Google se envían los campos seleccionados y las estadísticas necesarios para responder; no se le entrega la URI ni acceso directo a Atlas. Para una demostración usamos datos del catálogo y evitamos introducir información privada en los campos de texto.

La aplicación publicada no implementa cuentas de usuario, roles o un limitador propio de solicitudes. La validación comprueba la forma de los datos; no equivale a autenticar a la persona. Una vez activada la IA, las solicitudes públicas a `/preguntar` utilizan la cuota de la clave del propietario. Revisamos los límites y la facturación de esa cuenta antes de promover un uso amplio. Esto describe el alcance académico real del proyecto sin atribuirle controles que no programamos.

<a id="verificacion"></a>

## 8. Verificación y diagnóstico

### Qué se verificó y cómo defender la evidencia

Debemos separar **pruebas con servicios reales**, **pruebas locales** y **simulaciones controladas**. Una simulación permite producir de forma predecible errores que serían difíciles de provocar en Google; no demuestra que una clave real funcione. Los siguientes resultados proceden del registro de verificación del proyecto cerrado el 8 de noviembre de 2026, no de una nueva ejecución hecha al reorganizar los Markdown.

| Fase documentada | Alcance | Resultado y límite de la evidencia |
|---|---|---|
| Validación local inicial | MongoDB 8.0.17 temporal con 235 documentos sintéticos, API por HTTP y Streamlit AppTest. | 112 comprobaciones de condiciones, sin fallos; no son 112 pruebas independientes. |
| API pública, 2 de noviembre | 12 GET y un POST de registro técnico. | 31 comprobaciones sin fallos; verificó lectura y una creación real. |
| Dashboard público, 2 de noviembre | Navegación y creación de un registro técnico desde la interfaz. | Flujo confirmado; verificador posterior con seis GET y 12 comprobaciones, sin otro POST. |
| IA local, 8 de noviembre | TestClient/AppTest, MongoDB y Google simulados. | 20 métodos de prueba con 39 subcasos incluidos, sin fallos ni errores. |
| Publicación de IA, 8 de noviembre | Tres GET de verificación y uso de la nueva pestaña. | Seis comprobaciones sin fallos; ruta publicada, configuración de clave pendiente según el mensaje observado. |

La fase local inicial cubrió los esquemas de datos del segundo corte, valores faltantes, `NaN`, infinitos, indicadores de límite, paginación, estadísticas y respuestas `201`, `409`, `422` y `503`. La prueba de certificados de esa fase verificó la configuración mediante simulación; no se presenta como una conexión real a Atlas. El usuario confirmó posteriormente la conexión desde su Mac y el funcionamiento del dashboard.

Las pruebas de IA cubrieron pregunta vacía o demasiado larga, filtros compartidos, distinción entre resumen completo y muestra, clave en cabecera, errores del proveedor, espera agotada, JSON inválido, bloqueos, respuesta truncada y conservación correcta del estado de Streamlit. Por ejemplo, utilizaron un total ficticio de 1.234 frente a 30 ejemplos para comprobar que esos conceptos no se confundieran. **No se hicieron llamadas reales a Gemini en esas pruebas automatizadas.**

El despliegue de IA registrado utilizó el commit `a4ae5d07c1b4c0c17b5b7607a591a1e47f7d4a65` y alcanzó estado Live el 8 de noviembre a las 10:25:43, hora de Bogotá. La revisión posterior encontró 6.379 registros totales; con filtro NASA eran 6.375, de los cuales 5.693 resultaban evaluables para radio e insolación, 27 cumplían ambos criterios y 682 no tenían información suficiente para esa evaluación. Son cifras de esa fotografía temporal; una inserción posterior o un filtro distinto puede cambiarlas.

Los registros técnicos creados en las verificaciones del 2 de noviembre se identificaron como manuales y con magnitudes desconocidas. No se deben presentar como descubrimientos NASA. La fase de Gemini del 8 de noviembre no creó planetas nuevos. No sumamos los métodos y subcasos como si fueran pruebas independientes ni afirmamos haber repetido toda la batería al modificar documentación.

### Cómo diagnosticar los errores más frecuentes

La primera decisión es localizar la capa que falla. Un error al activar Python ocurre antes de la API; un `503` de MongoDB ocurre dentro de la API; un `429` de Gemini corresponde al proveedor de IA. Cambiar toda la configuración al mismo tiempo dificulta identificar la causa.

| Síntoma | Comprobación concreta | Explicación |
|---|---|---|
| No existe `venv/bin/activate` | Revisar carpeta actual y crear `venv` con Python 3.12. | No se activa un entorno que todavía no existe en esa ruta. |
| `No module named streamlit` | Activar el entorno e instalar `python -m pip install -r requirements.txt`. | El intérprete activo no tiene las dependencias. |
| No abre `localhost:8000` | Revisar la terminal de Uvicorn y su mensaje de arranque. | El dashboard no inicia automáticamente la API. |
| `/` responde pero `/salud` falla | Revisar `MONGO_URI`, base, colección, permisos de Atlas y conectividad. | El proceso web puede estar vivo sin poder consultar MongoDB. |
| Falla un certificado en Mac | Confirmar dependencias instaladas y el uso de `certifi.where()` en la conexión SRV. | La confianza TLS es diferente de la sintaxis de la URI. |
| Dashboard público no conecta | Comprobar la clave raíz `API_BASE_URL` en Secrets. | `localhost` en la nube no apunta al Mac. |
| La IA indica que falta la clave | Configurar `GEMINI_API_KEY` en el backend y cargar la nueva configuración. | La clave puesta únicamente en Streamlit no llega a Render. |
| Modelo no disponible o sin permisos | Revisar `MODELO_IA` y acceso de la clave en AI Studio. | Un identificador válido no asegura acceso para todas las cuentas. |
| IA devuelve `429` | Revisar cuota y frecuencia de solicitudes. | Repetir inmediatamente puede mantener el mismo límite. |
| La respuesta se corta o aparece `MAX_TOKENS` | Formular una pregunta más concreta y revisar la configuración de generación. | No se presenta un resultado incompleto como exitoso. |
| Streamlit pide reactivar la aplicación | Usar la opción de reactivación y esperar el inicio. | La hibernación es una condición del alojamiento. |
| GitHub tiene cambios y la API aún usa el código anterior | Revisar el commit Live y desplegar en el servicio existente si corresponde. | Publicar código y ejecutar ese código son pasos diferentes. |

Para la demostración podemos recorrer `/docs`, `/salud`, filtros, gráficas y formulario sin generar registros de prueba innecesarios. Antes de mostrar la IA comprobamos la configuración; si el servicio externo no está disponible, explicamos qué parte está implementada y qué respuesta controlada ofrece. Una sustentación sólida distingue lo programado, lo probado y lo que depende de una cuenta o de un servicio externo.

<a id="rubrica"></a>

## 9. Correspondencia con la rúbrica

La distribución procede de la guía docente del proyecto final suministrada para este trabajo. Esta tabla vincula cada criterio con una parte que podemos mostrar y explicar; la calificación corresponde al profesor.

| Componente | Valor | Evidencia del proyecto | Qué debes poder explicar |
|---|---:|---|---|
| API de lectura: filtros y agregación | 1,2 | `GET /datos`, filtros compartidos, paginación y `GET /estadisticas`. | Cómo los parámetros se convierten en una consulta; qué calcula MongoDB y qué calcula Python. |
| API de escritura: POST, validación y códigos | 1,0 | `NuevoRegistro`, `POST /datos`, respuesta `201`, validación `422` y duplicado detectado `409`. | Cómo llega el cuerpo JSON, por qué se valida y cómo se comprueba persistencia. |
| Dashboard: consumo, filtros, gráfica y creación | 1,4 | Las preguntas, el catálogo, filtros, gráficas y formulario. | Cómo `requests` conecta la interfaz con el backend y cómo pandas prepara los resultados. |
| Integración, calidad y credenciales | 0,8 | Recorrido completo Streamlit–FastAPI–Atlas, funciones separadas y configuración externa. | Cómo se distribuyen responsabilidades y dónde se configuran los secretos. |
| Sustentación y defensa | 0,6 | Demostración coherente y respuestas justificadas. | El recorrido de los datos, las decisiones y los límites de las conclusiones. |
| **Total ordinario** | **5,0** | | |

La guía contempla un bono de **hasta 0,3** por despliegue público y una penalización de **0,3 a 0,5** por credenciales expuestas. El extra de Gemini se añadió después: el material disponible no establece un puntaje adicional concreto para esa ampliación. No debemos inventarle una ponderación ni garantizar una nota.

Para apoyar el bono mostramos las direcciones públicas del dashboard y de la API. Para apoyar la integración demostramos una consulta y, si corresponde a la exposición, una captura manual que después aparece al consultar. Para apoyar la sustentación explicamos un recorrido completo con nuestras palabras y relacionamos cada paso con su función.

<a id="guion"></a>

## 10. Guion para presentar y demostrar

### Preparación de la demostración

Abre previamente el [dashboard público](https://exoplanetasproyecto.streamlit.app/), [Swagger](https://exoplanetas-api-juanfmarbo.onrender.com/docs) y el [repositorio](https://github.com/Juanfmarbo/First-API). Comprueba `/salud` y deja preparada la selección **Solo catálogo NASA** para el análisis. La aplicación pública puede necesitar activarse después de un período de inactividad; por eso conviene comprobarla antes de empezar la exposición.

Si mostrarás una generación real, verifica antes que el backend tenga la clave y envía una pregunta de ensayo. Si aparece un error, identifica su causa; no presentes una respuesta escrita de antemano como salida real. Si necesitas mostrar ejecución local, prepara dos terminales con el entorno correcto y conserva visible el comando de cada proceso.

El material disponible no fija aquí una duración obligatoria. El orden siguiente funciona como recorrido adaptable: resume las partes generales si el profesor limita el tiempo y conserva las explicaciones técnicas para las preguntas.

### Apertura: qué construimos

Puedes explicarlo así, con tus propias palabras:

> Este proyecto transforma el análisis de exoplanetas del segundo corte en una aplicación web. MongoDB Atlas conserva los datos; nuestra API FastAPI los consulta, calcula estadísticas y recibe registros; Streamlit permite usar esas funciones desde el navegador. Mantenemos cuatro preguntas de análisis y añadimos una pestaña para que Gemini explique los datos de la selección.

Después señala la separación de componentes en el diagrama. Explica que el dashboard no accede directamente a MongoDB, que las estadísticas pertenecen al backend y que los registros manuales conservan su procedencia.

### Demostración de lectura y filtros

En la barra lateral elige **Solo catálogo NASA**, aplica filtros y muestra el total. Cambia un método o un intervalo de años y vuelve a aplicar. Describe qué ha cambiado: la selección, los indicadores y las gráficas. Si la selección queda vacía, explica que eso es un resultado posible de la consulta.

Abre el catálogo y relaciona el tamaño de página con el total. Si aparecen 25 filas de una selección mayor, explica que se han pedido solo 25 documentos para esa página, mientras las estadísticas siguen usando todos los registros filtrados. Cambia de página y muestra el CSV como descarga de esa página, sin llamarlo exportación completa de la colección.

En Swagger abre `GET /datos`, utiliza los mismos filtros y muestra el JSON. Señala `total`, `pagina`, `por_pagina`, `paginas` y `datos`. Esa comparación conecta la interfaz con la API que realmente consume.

### Demostración de las cuatro preguntas

En la primera pregunta muestra candidatos, evaluables y datos insuficientes. Di explícitamente que el denominador del porcentaje son los evaluables. Si cambias a **Solo candidatos**, explica que has cambiado la población que estás analizando.

Busca la distancia en parsecs de un candidato en el Catálogo o en `/datos`; después muestra su conversión a años luz y el viaje idealizado en la segunda pregunta. Explica que la velocidad es un supuesto de 17 km/s y que no se modela una misión real. No afirmes que los diez ejemplos constituyen todos los candidatos cuando la selección contiene más.

En la tercera alterna mediana y máxima. La mediana representa el centro de las distancias ordenadas; la máxima corresponde al extremo observado. Explica por qué una distancia máxima alta no demuestra que un método sea siempre mejor.

En la cuarta elige una categoría y muestra casos por método y evaluables. Recuerda que la temperatura excluye `Imaging`, que los indicadores deben permitir valores puntuales y que un planeta puede ser extremo por más de una condición.

### Demostración de escritura

Si la exposición incluye una captura, utiliza **un nombre claramente identificable como demostración**. No hace falta inventar medidas: puedes dejar las magnitudes desconocidas y mostrar que el sistema acepta un registro con los cuatro campos obligatorios.

Explica el recorrido antes de pulsar: formulario → diccionario → `requests.post` → `NuevoRegistro` → comprobación de duplicado → fuente manual → `insert_one` → respuesta `201`. Después muestra la confirmación y la consulta del registro recién creado. El cambio automático de filtros busca precisamente hacer visible ese resultado.

Para explicar validación puedes enseñar en Swagger un cuerpo que omita un campo obligatorio y observar `422`, o recorrer el ejemplo del documento sin realizar una nueva solicitud. Si se repite un nombre existente, el control habitual responde `409`. Aclara que el programa no crea un índice único de nombres y no resuelve por sí solo una carrera entre dos inserciones simultáneas.

Una captura válida queda persistida. El proyecto no tiene botón ni endpoint de borrado; no prometas que se eliminará al cerrar el navegador. Los registros de demostración deben permanecer identificados como manuales.

### Demostración de Gemini

Aplica primero los filtros deseados. Una pregunta útil es: **“¿Cuántos candidatos cumplen radio e insolación y por qué eso no demuestra habitabilidad?”**. Otra es: **“¿Qué implica el tiempo de viaje calculado para el candidato más cercano de esta selección?”**.

Mientras se realiza la solicitud, explica que la API envía las reglas, un resumen completo y hasta treinta registros de ejemplo. Cuando llegue una respuesta real, contrasta sus cifras con la primera pestaña y muestra el tamaño de la selección y de la muestra. Si pregunta por un planeta que no aparece en los ejemplos, busca su nombre antes de generar de nuevo.

Si el proveedor no responde, usa el código y el mensaje observado para explicar la integración. Las pruebas con respuestas simuladas acreditan que nuestro programa interpreta esas situaciones; no acreditan una respuesta real de Gemini. La última comprobación pública registrada el 8 de noviembre detectó falta de clave, por lo que una activación posterior requiere su propia comprobación.

### Recorrido por el código

Abre `api.py` y localiza, en este orden, configuración, `obtener_coleccion`, `recibir_filtros`, `construir_consulta`, `listar_datos`, `estadisticas`, `NuevoRegistro`, `crear_registro` y `preguntar`. No es necesario leer todas las líneas en voz alta: explica entrada, transformación y salida de cada bloque, y amplía donde el profesor pregunte.

Abre `dashboard.py` y localiza `pedir_api`, `mostrar_preguntas`, `mostrar_catalogo`, `mostrar_formulario`, `mostrar_ia` y el flujo principal. Relaciona cada función con la pestaña que acabas de mostrar. Termina señalando las variables de entorno, las siete dependencias y los dos comandos de ejecución.

### Cierre de la exposición

> La aplicación completa el recorrido desde una interfaz hasta datos persistentes y vuelve con resultados interpretables. Las reglas están explícitas, los valores desconocidos se conservan y las capturas manuales se distinguen del catálogo. La IA aporta explicaciones sobre ese contexto; las estadísticas se calculan en nuestro código y se pueden comprobar. Los siguientes pasos, si el proyecto creciera, serían controlar quién puede escribir, gestionar cuotas y optimizar las consultas.

<a id="preguntas"></a>

## 11. Preguntas del profesor y respuestas razonadas

Estas respuestas sirven para practicar. Lo importante es poder justificarlas señalando el archivo, la función o la pantalla correspondiente.

### Fundamentos y arquitectura

**1. ¿Qué hace el proyecto en una frase?**

Permite explorar un catálogo de exoplanetas, analizar cuatro preguntas, guardar capturas manuales y consultar explicaciones de IA mediante una aplicación que integra Streamlit, FastAPI y MongoDB Atlas.

**2. ¿Qué es una API?**

Es una interfaz que define cómo otro programa puede solicitar operaciones y recibir resultados. La nuestra define rutas HTTP: por ejemplo, `GET /datos` acepta filtros y devuelve JSON con documentos paginados.

**3. ¿Qué diferencia hay entre URL, ruta y método?**

La URL completa incluye protocolo, servidor, ruta y posibles parámetros. La ruta `/datos` identifica una operación o recurso dentro del servidor; el método indica la acción. `GET /datos` consulta y `POST /datos` crea, aunque compartan la ruta.

**4. ¿Por qué GET para consultar y POST para guardar?**

GET expresa recuperación de información y nuestros filtros van en la URL. POST envía un cuerpo para que el servidor procese una operación, como crear un documento. No todo POST guarda algo: `/preguntar` solicita una generación y no inserta un planeta.

**5. ¿Un diccionario de Python es lo mismo que JSON?**

Un diccionario es una estructura en memoria de Python; JSON es un formato de intercambio de texto. FastAPI serializa estructuras a JSON y `requests` interpreta JSON recibido. `None` pasa a `null`; JSON utiliza `true` y `false` en lugar de `True` y `False`.

**6. ¿Por qué usamos FastAPI y también Uvicorn?**

FastAPI declara la aplicación, rutas y validación. Uvicorn es el servidor que atiende conexiones y ejecuta esa aplicación. En `api:app`, `api` es el módulo y `app` es la instancia FastAPI que contiene.

**7. ¿Escribimos Swagger manualmente?**

FastAPI genera el esquema OpenAPI a partir de rutas, anotaciones, modelos y metadatos. La interfaz `/docs` utiliza ese esquema para mostrar los parámetros y permitir peticiones. Los ejemplos de Pydantic ayudan a documentar el cuerpo esperado.

**8. ¿Quién se conecta a la base de datos?**

`api.py`, mediante PyMongo. Streamlit utiliza HTTP contra nuestra API. La clave de Gemini tampoco pertenece al dashboard: la utiliza el backend al llamar a Google.

### MongoDB, filtros y validación

**9. ¿Cuál es la diferencia entre Atlas y PyMongo?**

Atlas es el servicio donde está alojada la base MongoDB. PyMongo es la biblioteca que usa nuestro código para operar sobre ella. El cluster contiene infraestructura; la base organiza colecciones; la colección contiene documentos.

**10. ¿Por qué hay nombres largos y nombres cortos para algunos campos?**

Son variantes del esquema del segundo corte. `ALIAS_CLASE` relaciona los nombres finales con los cortos. La API adapta consultas y salida al esquema detectado; no hace una migración automática de todos los documentos.

**11. ¿Por qué un dato desconocido no vale cero?**

Porque cero es un número con significado y ausencia de información es otra situación. Sustituir una temperatura desconocida por cero podría clasificar erróneamente un objeto como congelado. `None` permite excluirlo del cálculo que no puede evaluarse.

**12. ¿Qué significan `limite_*` y por qué se exige `0`?**

Distinguen valor puntual, límite superior, límite inferior y desconocido. Para aplicar nuestros umbrales usamos valores puntuales. Saber que un radio es como máximo cierto valor no equivale a conocer su radio exacto dentro de un intervalo.

**13. ¿Qué hace Pydantic?**

Interpreta y valida el cuerpo según clases como `NuevoRegistro` y `Pregunta`. Comprueba campos, tipos, longitudes y restricciones; rechaza propiedades adicionales. El backend conserva esa validación aunque alguien evite el formulario y llame directamente a la API.

**14. ¿Por qué validamos también en Streamlit?**

La interfaz puede explicar un error inmediatamente y evitar una petición innecesaria. La validación definitiva sigue en la API porque puede recibir otros clientes. Ambas capas cumplen propósitos distintos dentro del mismo recorrido.

**15. ¿Por qué rechazamos booleanos en medidas e indicadores?**

En Python `bool` tiene una relación con `int`, por lo que `True` podría confundirse con `1` en determinadas comprobaciones. El validador previo evita que una respuesta booleana se interprete como medida física o indicador numérico válido.

**16. ¿Qué hacen `Query` y `Depends`?**

`Query` declara condiciones para parámetros de URL, como rangos y longitudes. `Depends` hace que FastAPI ejecute una función compartida y entregue su resultado a la ruta. Usamos `recibir_filtros` para mantener las mismas reglas en datos, estadísticas y preguntas de IA.

**17. ¿Para qué usamos `re.escape`?**

Para que símbolos especiales introducidos en una búsqueda se interpreten como texto literal dentro de la expresión regular. En duplicados añadimos anclas de inicio y fin para comparar el nombre completo; en búsqueda se permiten coincidencias parciales de planeta o estrella.

**18. ¿Dónde van los filtros de una pregunta de IA?**

En los parámetros de la URL, igual que en otras consultas. La pregunta va en el cuerpo JSON como `{"pregunta": "..."}`. Por eso la función puede utilizar simultáneamente `params=filtros` y `json=registro` en una solicitud POST.

**19. ¿Qué significa paginar?**

Dividir una selección en páginas. Calculamos cuántos documentos coinciden y después usamos orden, salto y límite para devolver una porción. Una página de 25 filas no significa que el total de coincidencias sea 25.

**20. ¿Por qué ordenar por planeta y `_id`?**

El nombre proporciona un orden comprensible y el identificador desempata nombres iguales. Eso vuelve determinista el orden para un conjunto que no cambia. No crea una instantánea inmune a inserciones simultáneas entre consultas.

**21. ¿Qué es una agregación de MongoDB?**

Una secuencia de etapas que transforma documentos para obtener resultados resumidos. Aquí `$match` filtra, `$group` agrupa y `$sum: 1` cuenta documentos; `$sort` ordena los grupos. Los cálculos científicos adicionales se hacen con las estructuras normalizadas en Python.

**22. ¿Cómo evitamos duplicados?**

Antes de insertar buscamos un nombre completo igual sin distinguir mayúsculas y devolvemos `409` cuando existe. También se captura `DuplicateKeyError`. El código no crea un índice único de nombre, así que la comprobación previa no garantiza unicidad atómica ante dos inserciones simultáneas.

**23. ¿Qué hace `201` y qué hacen `409`, `422` y `503`?**

`201` comunica creación correcta; `409`, un conflicto como el duplicado detectado; `422`, entrada que no cumple el contrato; `503`, un servicio o configuración no disponible. El mensaje de detalle permite identificar la causa concreta. `503` no significa exclusivamente error de MongoDB.

### Estadísticas y significado científico

**24. ¿Por qué el porcentaje de candidatos no divide entre todo el catálogo?**

Porque solo los evaluables tienen radio, insolación e indicadores suficientes para decidir. El porcentaje describe candidatos entre evaluables; también informamos cuántos carecen de información suficiente. Si no hay evaluables, el resultado es desconocido, no un cero inventado.

**25. ¿Encontramos planetas habitables?**

Seleccionamos candidatos según dos intervalos exploratorios. No demostramos presencia de agua, atmósfera adecuada o vida. La etiqueta debe conservar ese alcance aunque Gemini redacte la explicación.

**26. ¿Cómo calculamos el tiempo de viaje?**

Convertimos parsecs a años luz multiplicando por 3,26 y después multiplicamos los años luz por `299792.458 / 17`. Esto compara la velocidad de la luz con la velocidad hipotética de viaje y devuelve años. El modelo supone velocidad constante y no incluye aceleración, frenado ni trayectorias.

**27. ¿Por qué utilizamos la mediana y no solo el máximo?**

La mediana describe el punto central de los valores ordenados y el máximo describe el extremo. Una sola distancia muy grande afecta directamente al máximo. Mostrar ambos permite distinguir una distancia típica del caso más lejano del conjunto.

**28. ¿El método con mayor distancia máxima es el mejor?**

El resultado solo dice que, en la selección, ese método tiene el registro más lejano entre los comparados. Los conjuntos pueden diferir en tamaños, condiciones y objetos observados. Nuestro cálculo no controla esos factores para establecer superioridad general.

**29. ¿Por qué se excluye `Imaging` de los extremos térmicos?**

Porque el parámetro original puede representar temperatura efectiva para imagen directa, mientras otros registros usan temperatura de equilibrio modelada. El proyecto conserva una regla para no mezclar directamente esas interpretaciones en esa clasificación. No afirmamos que sea temperatura superficial.

**30. ¿Puedo sumar Infierno, Congelado, Relámpago y Supergigante para obtener planetas únicos?**

No en general. Un mismo planeta puede cumplir, por ejemplo, temperatura alta y período corto. El código calcula por separado los casos de cada criterio y el conjunto de planetas con al menos un extremo.

**31. ¿Por qué cada extremo tiene su propio porcentaje?**

Cada condición tiene requisitos de evaluación. Infierno y Congelado comparten temperatura e indicador; Relámpago utiliza período y Supergigante utiliza masa. Puede haber muchos registros con período válido y menos con masa válida. El denominador de cada porcentaje es su conjunto evaluable, no un total común elegido por comodidad.

**32. ¿Qué ocurre si mezclo registros manuales con NASA?**

Los registros manuales que satisfagan las reglas pueden contribuir cuando el origen es `todos`. Por eso existe el filtro de procedencia y la fuente no la decide el cliente. Para presentar resultados del catálogo original utilizamos el origen NASA.

### Dashboard y ejecución

**33. ¿Pandas dibuja todas las gráficas?**

En este código pandas prepara las tablas y columnas; Streamlit presenta las gráficas con sus funciones nativas. El backend calcula los resultados principales con MongoDB y Python, incluida `statistics.median`. No debemos atribuir todos los cálculos a pandas.

**34. ¿Qué es un rerun de Streamlit?**

Es una nueva ejecución del script para reconstruir la interfaz después de una interacción que la dispara. No es simplemente cambiar el color de un componente. Por eso distinguimos variables locales de estado de sesión y agrupamos entradas en formularios.

**35. ¿Para qué sirve `st.session_state`?**

Conserva información entre ejecuciones de la misma sesión, como filtros aplicados, página y última respuesta de IA. No reemplaza MongoDB como almacenamiento persistente y no crea memoria conversacional en Gemini. El estado está asociado a la sesión de la interfaz.

**36. ¿Para qué sirven los formularios?**

Permiten reunir varias entradas y procesarlas al pulsar el botón de envío. Así editar campos no equivale a crear registros o generar respuestas inmediatamente. La lógica distingue si se está mostrando el formulario o si se acaba de enviar.

**37. ¿Una pestaña oculta deja de ejecutar su código?**

Con el uso actual de `st.tabs`, el contenido de las pestañas se ejecuta aunque no esté visible. La llamada a Gemini está dentro de la condición de envío del formulario, por lo que no se genera una respuesta al abrir cada pestaña. No debemos confundir visibilidad con ejecución condicional.

**38. ¿El CSV descarga la base completa?**

Descarga la página visible y las columnas preparadas para esa tabla. Se genera con `to_csv(index=False)` y se codifica como `utf-8-sig`. Para obtener otra página hay que consultarla; el proyecto no implementa un botón de exportación de toda la selección.

**39. ¿Por qué aparece el registro después de crearlo?**

La interfaz guarda un mensaje y el nombre recién creado, solicita `st.rerun` y ajusta la selección antes de reconstruir los widgets. Activa el origen manual y la búsqueda correspondiente. Esa nueva lectura comprueba el resultado guardado; la búsqueda por texto puede devolver otras coincidencias si existen.

### IA, configuración y evidencia

**40. ¿Gemini solo puede repetir los datos?**

Puede explicar y razonar a partir del contexto, como relacionar distancia y tiempo de viaje. Las instrucciones le piden limitarse a la evidencia suministrada. Una predicción sobre tecnología futura o habitabilidad puede requerir información que nuestra integración no proporciona.

**41. ¿Qué recibe Gemini y qué no recibe?**

Recibe descripción, reglas, filtros, resumen de toda la selección y hasta treinta registros reducidos de la primera página. No recibe la contraseña de MongoDB, acceso directo a la colección, todas las conversaciones anteriores ni una herramienta de búsqueda web configurada por nosotros.

**42. ¿Por qué enviar un resumen completo además de treinta ejemplos?**

Los ejemplos dan detalles concretos pero no contienen necesariamente todos los planetas. El resumen proporciona totales y comparaciones calculados sobre la selección completa. Los primeros treinta ordenados no son una muestra aleatoria representativa.

**43. ¿Entrenamos nuestro propio modelo?**

No. Usamos un modelo del proveedor y le enviamos contexto en cada solicitud REST. No hay ajuste de pesos, entrenamiento con nuestra base ni un sistema de búsqueda vectorial. Esa sencillez permite mantener el enfoque de APIs enseñado en clase.

**44. ¿Qué ocurre si Gemini no responde?**

El backend distingue errores de configuración, cuota, tiempo y respuesta no utilizable. Streamlit muestra el mensaje. Las rutas normales del catálogo y las gráficas no necesitan una clave de Gemini para funcionar; una generación fallida no modifica documentos.

**45. ¿Por qué `timeout=30` en la API y `60` en el dashboard?**

La API limita la espera de su llamada al proveedor y el dashboard concede más margen a la operación completa, que también consulta datos y procesa resultados. En Requests esos valores controlan esperas de conexión/lectura; no garantizan exactamente ese tiempo total de reloj para toda la operación.

**46. ¿Dónde ponemos las credenciales?**

En variables de entorno: `.env` local o configuración privada del servicio que ejecuta el backend. Streamlit necesita `API_BASE_URL`; la API necesita la conexión a Atlas y la clave de Gemini. `.env.example` documenta nombres sin publicar valores reales.

**47. ¿`certifi` es el intermediario que conecta MongoDB en Mac?**

Es un conjunto de certificados de confianza, no un servidor intermediario. `certifi.where()` devuelve la ruta que PyMongo usa para validar TLS en las conexiones SRV del proyecto. No corrige una contraseña errónea, una IP bloqueada ni un problema DNS.

**48. ¿`localhost` sirve desde Streamlit Cloud para llegar a la API de mi Mac?**

No. `localhost` siempre se refiere a la máquina donde se ejecuta el proceso que hace la petición. En Streamlit Cloud debe configurarse la URL pública del backend. Los puertos locales 8000 y 8501 sirven para el desarrollo en el equipo.

**49. ¿Qué pruebas se hicieron realmente?**

Hubo comprobaciones locales con datos sintéticos y MongoDB real, verificaciones públicas de lectura y creación, y pruebas de integración de IA con respuestas simuladas. El 8 de noviembre se verificó públicamente la nueva pestaña y su diagnóstico de clave ausente. Cada grupo tiene fecha y alcance; no se suman condiciones y subcasos como si fueran ejecuciones independientes.

**50. ¿Qué mejorarías si el proyecto creciera?**

Autenticación y permisos para escritura, control de consumo de IA, garantías de unicidad mediante una estrategia de índice apropiada y consultas que eviten cargar grandes selecciones en memoria. También revisaría límites del proveedor y configuración del entorno de desarrollo. Son mejoras futuras justificadas por límites identificados, no funciones que debamos afirmar que ya existen.

<a id="glosario"></a>

## 12. Glosario y comprobación de comprensión

### Términos que debes poder traducir a lenguaje sencillo

| Término | Explicación dentro de este proyecto |
|---|---|
| Endpoint | Combinación de método y ruta que atiende una operación. |
| Request / response | Solicitud que envía un cliente y respuesta que devuelve el servidor. |
| Query string | Parámetros que aparecen después de `?` en la URL, separados por `&`. |
| Body | Cuerpo de la solicitud; transporta el JSON de registro o pregunta. |
| Header | Metadato HTTP; por ejemplo, la autenticación `x-goog-api-key`. |
| Serializar | Convertir una estructura en un formato transmisible, como JSON. |
| Validar | Comprobar que una entrada cumple el contrato antes de utilizarla. |
| Normalizar | Dar una representación uniforme a campos y valores que pueden variar. |
| Cursor | Resultado recorrible de una consulta de MongoDB. |
| Agregación | Operación que agrupa o resume documentos mediante etapas. |
| Paginación | Devolver una parte ordenada de una selección y datos sobre su total. |
| Persistencia | Que el registro siga almacenado después de terminar la solicitud o cerrar la interfaz. |
| Dependencia de Python | Paquete necesario para ejecutar el programa. |
| Dependencia de FastAPI | Función cuyo resultado FastAPI prepara e inyecta en otra operación. |
| Entorno virtual | Instalación aislada de Python y paquetes para el proyecto. |
| Variable de entorno | Configuración que recibe un proceso desde su entorno de ejecución. |
| Rerun | Nueva ejecución de `dashboard.py` para reconstruir la interfaz. |
| Estado de sesión | Información que Streamlit conserva entre ejecuciones de la misma sesión. |
| Prompt | Entrada con contexto y pregunta que enviamos al modelo. |
| Token | Unidad de texto utilizada por el modelo; no equivale siempre a una palabra. |
| Mock o simulación | Sustitución controlada de un servicio para comprobar el comportamiento del código. |
| Despliegue | Preparar y ejecutar una versión del proyecto en un servidor accesible. |
| Commit | Registro de una versión de cambios en Git. |

### Ejercicios mentales para verificar que lo entendiste

**Caso A: hay 100 registros, 80 evaluables y 4 candidatos.** El porcentaje del criterio es `4 / 80 × 100 = 5 %`; hay 20 no evaluables. Si el catálogo muestra 25 filas, el porcentaje no pasa a ser `4 / 25`. La paginación y el denominador científico cumplen funciones diferentes.

**Caso B: un radio vale 1,1 pero `limite_radio` es `1`.** Ese valor es un límite superior; no se utiliza como medición puntual para declarar un candidato. Debes mirar también insolación e indicadores, no solo comparar dos números con los intervalos.

**Caso C: un objeto tiene temperatura de 2.500 K y período de 0,5 días, ambos evaluables.** Puede contar en Infierno y en Relámpago. Al sumar casos de ambas categorías se cuenta dos veces, mientras el total de planetas con al menos un extremo lo cuenta una vez.

**Caso D: Gemini recibe treinta registros y el objeto buscado no aparece.** Eso no demuestra que no exista en la selección. La muestra es limitada; filtra por el nombre y vuelve a preguntar. Los totales ya calculados deben salir del resumen completo.

**Caso E: Streamlit muestra un mensaje de guardado y cierras el navegador.** El documento permanece en Atlas porque hubo una inserción persistente. El mensaje y los filtros de la sesión pertenecen a otro tipo de estado; no son la base de datos.

Si puedes explicar esos cinco casos, seguir una petición GET y una POST hasta MongoDB, relacionar una gráfica con su denominador y describir exactamente qué contexto recibe Gemini, comprendes las relaciones centrales del proyecto. Para los detalles de sintaxis, utiliza los capítulos de código y sus enlaces a documentación oficial.
