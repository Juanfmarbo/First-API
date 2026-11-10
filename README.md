# First-API: explorador de exoplanetas

Proyecto final de **Programación Aplicada** que convierte el análisis de exoplanetas del segundo corte en una aplicación web. **MongoDB Atlas** conserva los documentos; **FastAPI** permite consultarlos, calcular estadísticas y crear registros; **Streamlit** presenta filtros, tablas, gráficas y un formulario. El extra de **Gemini** permite hacer preguntas en español sobre la selección de datos.

Este repositorio tiene dos documentos: este README para entender, configurar y usar el proyecto, y [presentacion-sustentacioln.md](presentacion-sustentacioln.md) para estudiar y defender su implementación en detalle. El segundo explica las funciones, las decisiones, los cálculos, el despliegue, las comprobaciones realizadas y las posibles preguntas del profesor.

## Acceso al proyecto

| Componente | Enlace |
|---|---|
| Dashboard en Streamlit Community Cloud | [exoplanetasproyecto.streamlit.app](https://exoplanetasproyecto.streamlit.app/) |
| API en Render | [exoplanetas-api-juanfmarbo.onrender.com](https://exoplanetas-api-juanfmarbo.onrender.com) |
| Documentación interactiva de la API | [Swagger: /docs](https://exoplanetas-api-juanfmarbo.onrender.com/docs) |
| Comprobación de conexión con MongoDB | [/salud](https://exoplanetas-api-juanfmarbo.onrender.com/salud) |
| Código e historial | [Juanfmarbo/First-API](https://github.com/Juanfmarbo/First-API) |

La última comprobación pública documentada es del **8 de noviembre de 2026**: API versión **1.1.0**, conexión con Atlas correcta y cuatro pestañas visibles. En esa comprobación, enviar una pregunta devolvió que faltaba `GEMINI_API_KEY` en el backend; se verificó la integración y su diagnóstico, pero **no una respuesta real de Google**. El estado de la clave puede cambiar después de esa fecha. El [apartado de verificación](presentacion-sustentacioln.md#verificacion) diferencia pruebas locales, simuladas y públicas.

## Qué permite hacer

- Buscar planetas o estrellas y filtrar por método, años, procedencia y criterios del proyecto.
- Consultar el catálogo por páginas y descargar como CSV **la página visible**.
- Responder las cuatro preguntas del segundo corte mediante estadísticas y gráficas.
- Crear registros identificados como manuales, con validación antes de guardarlos en Atlas.
- Preguntar a Gemini sobre los datos de la selección y las reglas del proyecto.

Las cuatro preguntas son:

1. **¿Cuántos planetas parecidos a la Tierra conocemos?** Se buscan radios entre 0,8 y 1,6 radios terrestres e insolaciones entre 0,35 y 1,5 veces la terrestre. Ambos indicadores de límite deben valer `0`.
2. **¿Qué tan lejos están y cuánto tardaríamos en llegar?** Se convierten parsecs a años luz y se calcula un viaje idealizado a 17 km/s; se muestran hasta diez candidatos más cercanos con distancia conocida.
3. **¿Qué tan lejos puede “ver” cada método?** Se comparan distancias mínimas, medianas y máximas de los registros disponibles por método. Esto describe el catálogo, no una capacidad instrumental universal.
4. **¿Qué tan extremos pueden ser?** Se cuentan las categorías Infierno, Congelado, Relámpago y Supergigante, cada una con sus condiciones y datos evaluables.

Los candidatos cumplen dos intervalos exploratorios; **no son una demostración de habitabilidad o de vida**. Los datos ausentes no se reemplazan por cero. Las categorías extremas pueden superponerse.

## Arquitectura y tecnologías

El navegador muestra Streamlit. El proceso de Streamlit usa `requests` para hablar por HTTP con FastAPI. La API valida parámetros, utiliza PyMongo para leer o escribir en Atlas y devuelve JSON. Streamlit organiza las respuestas con pandas y dibuja sus gráficas nativas.

Para una pregunta de IA, el backend prepara las reglas del proyecto, las estadísticas de **toda la selección** y los primeros **hasta 30 registros**, ordenados por nombre, como ejemplos. Envía ese contexto a Gemini. Google no recibe acceso directo a MongoDB. Las credenciales de Atlas y Gemini pertenecen al backend.

Se conservan las siete dependencias directas del enfoque trabajado en clase:

| Dependencia | Versión fijada | Para qué se usa |
|---|---|---|
| `pymongo` | `4.19.0` | Conexión, consultas, agregaciones e inserciones en MongoDB. |
| `pandas` | `3.1.0` | Tablas, transformación de respuestas y CSV. |
| `fastapi` | `0.162.0` | Rutas HTTP, parámetros y documentación de la API. |
| `uvicorn` | `0.54.0` | Servidor que ejecuta FastAPI. |
| `streamlit` | `1.66.1` | Interfaz, formularios, estado de sesión y gráficas. |
| `requests` | `2.34.2` | Solicitudes a la API del proyecto y a Gemini. |
| `python-dotenv` | `1.2.4` | Carga local de variables desde `.env`. |

Pydantic llega como dependencia de FastAPI y valida los modelos. `certifi` llega como dependencia de `requests` y aporta certificados para Atlas. Gemini reutiliza `requests`; no se añadió un SDK de IA. Los módulos de la biblioteca estándar de Python tampoco se instalan por separado.

| Archivo | Responsabilidad |
|---|---|
| [api.py](api.py) | MongoDB, normalización, filtros, estadísticas, creación y Gemini. |
| [dashboard.py](dashboard.py) | Interfaz, consumo de la API, tablas, gráficas, formulario y preguntas. |
| [requirements.txt](requirements.txt) | Dependencias directas con versiones fijadas. |
| [.env.example](.env.example) | Plantilla sin credenciales reales. |
| [.gitignore](.gitignore) | Exclusión de secretos locales, entornos y archivos generados. |
| [.python-version](.python-version) | Python 3.12, versión validada y utilizada en Render. |
| [render.yaml](render.yaml) | Plantilla declarativa del servicio de API en Render. |
| [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) | Configuración de VS Code/Codespaces; usa Python 3.11 y arranca solo Streamlit. Sus diferencias se explican en la sustentación. |
| [presentacion-sustentacioln.md](presentacion-sustentacioln.md) | Explicación completa para estudiar, demostrar y defender el proyecto. |

## Preparación local

Se necesita Python, acceso al repositorio y la colección limpia del segundo corte en Atlas. **Usa Python 3.12 para reproducir el entorno validado**. La guía de clase admite Python 3.11 o superior; eso no equivale a haber probado todas esas versiones con estas dependencias.

Para una copia nueva en Mac o Linux:

```bash
git clone https://github.com/Juanfmarbo/First-API.git
cd First-API
python3 --version
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Comprueba la versión antes de crear el entorno. Si tienes varias instalaciones, puedes usar `python3.12 -m venv venv`. Si ya tienes el proyecto, trabaja en su carpeta existente y conserva tu `.env`; no necesitas volver a clonar ni sobrescribirlo.

En Windows, los pasos equivalentes del entorno son:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Si PowerShell bloquea la activación, utiliza directamente `.\venv\Scripts\python.exe` en lugar de `python` en los comandos.

### Configuración de .env

Completa `.env` junto a `api.py`:

| Variable | Configuración |
|---|---|
| `MONGO_URI` | Cadena de conexión privada de Atlas. |
| `MONGO_DB` | `proyecto_segundo_corte`, salvo que tu base tenga otro nombre. |
| `MONGO_COLLECTION` | Nombre explícito; vacío para detección automática. |
| `API_BASE_URL` | `http://localhost:8000` para backend local o la URL pública de Render. |
| `GEMINI_API_KEY` | Clave privada de Google AI Studio. |
| `MODELO_IA` | `gemini-3.6-flash`, predeterminado del código. |

En `.env` puedes usar `MONGO_URI="tu_cadena_real"`; `python-dotenv` interpreta las comillas. En el panel de variables de Render introduce el valor sin comillas añadidas. En los secretos TOML de Streamlit los textos sí llevan comillas.

La detección automática busca la primera colección no vacía entre `exoplanetas_presentacion`, `exoplanetas_clase` y `exoplanetas`. Un nombre explícito tiene prioridad. La API reconoce las variantes del segundo corte y devuelve nombres uniformes sin reescribir los documentos originales. Los indicadores `limite_*` ausentes se conservan como desconocidos.

Para URI `mongodb+srv://`, PyMongo utiliza `tlsCAFile=certifi.where()`. Esto aporta certificados de confianza; **no es un intermediario de red**. También deben ser correctos usuario, contraseña, DNS y acceso de red de Atlas. Consulta la [documentación de TLS de PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/security/tls/).

### Ejecutar: dos terminales

En cada terminal, entra en la carpeta del proyecto y activa el entorno. En la primera ejecuta la API:

```bash
python -m uvicorn api:app --reload
```

Comprueba [http://localhost:8000/salud](http://localhost:8000/salud) y abre [http://localhost:8000/docs](http://localhost:8000/docs). En la segunda ejecuta el dashboard:

```bash
python -m streamlit run dashboard.py
```

Abre [http://localhost:8501](http://localhost:8501). Mantén ambos procesos funcionando; `Ctrl + C` detiene cada uno. Reinicia Uvicorn después de cambiar variables del backend.

Puedes ejecutar solo el dashboard local usando `API_BASE_URL=https://exoplanetas-api-juanfmarbo.onrender.com`; el backend funciona entonces en Render.

## Uso y rutas de la API

Aplica filtros en la barra lateral y recorre **Preguntas del proyecto**, **Catálogo**, **Agregar registro** y **Pregúntale a tus datos**. Las estadísticas usan toda la selección; la tabla muestra páginas de 25, 50 o 100 filas. Para analizar únicamente el catálogo original selecciona **Solo catálogo NASA**.

| Método y ruta | Función |
|---|---|
| `GET /` | Presentar la API y sus rutas. |
| `GET /salud` | Comprobar conexión, colección y cantidad de documentos. |
| `GET /opciones` | Obtener opciones y advertencias sobre indicadores. |
| `GET /datos` | Devolver registros filtrados y paginados. |
| `GET /estadisticas` | Calcular distribuciones y las cuatro preguntas. |
| `POST /datos` | Validar y guardar un registro manual. |
| `POST /preguntar` | Responder sobre la selección mediante Gemini. |

Los filtros compartidos son `metodo`, `nombre`, `anio_min`, `anio_max`, `solo_candidatos` y `origen`. Ejemplo:

```text
http://localhost:8000/datos?metodo=Transit&anio_min=2020&pagina=1&por_pagina=25
```

Para crear se requieren `planeta`, `estrella`, `metodo_descubrimiento` y `anio_descubrimiento`. Las magnitudes desconocidas se omiten o se dejan en `null`; los indicadores admiten `-1`, `0`, `1` o `null`. La fuente manual la establece el servidor. Una creación correcta responde `201`; un duplicado detectado, `409`; una entrada inválida, `422`.

En Swagger elige una operación, pulsa **Try it out**, completa los campos y pulsa **Execute**. Un POST válido guarda un documento real: usa un nombre identificable como demostración. La sustentación incluye ejemplos explicados.

## Activar Gemini y publicar

Obtén una clave en [Google AI Studio](https://aistudio.google.com/apikey) y configúrala como `GEMINI_API_KEY` en el **backend**: `.env` en local o **Environment de Render** para la API pública. Aplica el cambio y reinicia o despliega según el entorno. El dashboard necesita la URL de la API, no la clave de Google.

La llamada utiliza [generateContent](https://ai.google.dev/api/generate-content) y la cabecera `x-goog-api-key`. El modelo se configura con `MODELO_IA`. La pregunta tiene un máximo de 1.000 caracteres. Para preguntar por un planeta concreto, filtra su nombre: los treinta ejemplos no contienen necesariamente todos los objetos.

Gemini puede razonar sobre las cifras recibidas; las instrucciones le piden reconocer lo que no está respaldado. No hay búsqueda web, entrenamiento propio ni ejecución de código generado. Contrasta sus explicaciones con las estadísticas calculadas por la API.

Render instala `requirements.txt` y ejecuta:

```bash
python -m uvicorn api:app --host 0.0.0.0 --port $PORT
```

Streamlit Cloud utiliza `dashboard.py` y este secreto de nivel raíz:

```toml
API_BASE_URL = "https://exoplanetas-api-juanfmarbo.onrender.com"
```

`render.yaml` es una plantilla: su presencia en GitHub no configura por sí sola un servicio creado manualmente. El [capítulo de instalación y despliegue](presentacion-sustentacioln.md#despliegue) detalla los pasos y el estado verificado. Las URLs públicas no dependen de mantener abierto un puerto de tu Mac o de VS Code.

## Diagnóstico rápido

| Problema | Revisión |
|---|---|
| `venv/bin/activate` no existe | Carpeta correcta y entorno creado antes de activarlo. |
| `No module named streamlit` | Instala requisitos con el mismo Python que utilizas para ejecutar. |
| MongoDB no conecta | Variables, base, colección, credenciales, DNS, certificados y Network Access. |
| Dashboard sin conexión | `/salud`, URL base y proceso de API funcionando. |
| Sin resultados | Filtros y colección; una selección vacía puede ser válida. |
| IA devuelve `503` | Lee el detalle: clave ausente o configuración del modelo, entre otras causas. |
| IA devuelve `429`, `504` o `502` | Cuota/límite, espera agotada o fallo/respuesta no utilizable del proveedor, respectivamente. |

`.env`, `.streamlit/secrets.toml` y los entornos virtuales están excluidos de Git. `.gitignore` no elimina credenciales ya publicadas: una credencial expuesta debe reemplazarse en su proveedor.

## Preparar la sustentación

Estudia [presentacion-sustentacioln.md](presentacion-sustentacioln.md). Contiene el recorrido función por función, los fundamentos de GET y POST, MongoDB, validación, fórmulas, gráficas, estado de Streamlit, IA, despliegue, verificaciones y un guion con preguntas y respuestas.

La rúbrica suministrada distribuye 5,0 puntos entre lectura de API, escritura, dashboard, integración/calidad y sustentación; contempla un bono de hasta 0,3 por despliegue. Gemini es una ampliación posterior sin puntaje adicional especificado en el material disponible. Consulta la [correspondencia con la rúbrica](presentacion-sustentacioln.md#rubrica).
