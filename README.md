# First-API: explorador de exoplanetas

Aplicación del proyecto final de Programación Aplicada que continúa el trabajo del segundo corte sobre exoplanetas con datos de NASA. Los datos limpios se guardan en MongoDB Atlas, una API con FastAPI los consulta y un dashboard de Streamlit permite trabajar con ellos desde el navegador.

## Proyecto base: estado comprobado al 2 de noviembre de 2026

**Las funciones del proyecto base y su despliegue están completos y verificados.** El dashboard abre sin iniciar sesión y permite consultar el catálogo, aplicar filtros, recorrer páginas, explorar las cuatro preguntas y guardar registros manuales. Se comprobó el recorrido completo desde el formulario público hasta la API y MongoDB Atlas. La sustentación y la asignación de la nota corresponden al docente.

| Componente | Enlace y estado |
|---|---|
| Dashboard público | [Abrir Explorador de exoplanetas](https://exoplanetasproyecto.streamlit.app/) — consulta, filtros, paginación y creación persistente verificados. |
| API pública | [Abrir API](https://exoplanetas-api-juanfmarbo.onrender.com) — lectura y creación verificadas. |
| Documentación de la API | [Abrir /docs](https://exoplanetas-api-juanfmarbo.onrender.com/docs). |
| Conexión con Atlas | [Consultar /salud](https://exoplanetas-api-juanfmarbo.onrender.com/salud) — devolvió `estado: ok`. |
| Dashboard local | Funcionamiento confirmado por el usuario en su Mac. |

El despliegue de la API utilizado en su verificación inicial terminó el **2 de noviembre de 2026 a las 15:07:50, hora de Bogotá**, sobre el commit [54e134e](https://github.com/Juanfmarbo/First-API/commit/54e134e04deed0487f7b5775f107ef1d17133c32). Se comprobaron **12 solicitudes GET y 1 POST**, con **31 comprobaciones correctas y 0 fallos**. La verificación posterior del dashboard público se documenta de forma separada en [PRUEBAS_REALIZADAS.md](PRUEBAS_REALIZADAS.md).

### Extra de Gemini añadido el 8 de noviembre de 2026

Está implementada la cuarta pestaña **Pregúntale a tus datos** y la ruta **`POST /preguntar`**, siguiendo la llamada REST enseñada en clase. Para obtener respuestas reales de Gemini hay que configurar **`GEMINI_API_KEY` en el backend**. Esta ampliación se distingue de las verificaciones anteriores: una prueba con respuestas simuladas no acredita una llamada real a Google. El alcance de las comprobaciones se registra en [PRUEBAS_REALIZADAS.md](PRUEBAS_REALIZADAS.md).

La versión **1.1.0** quedó activa en Render el **8 de noviembre a las 10:25:43, hora de Bogotá**, con el commit `a4ae5d07c1b4c0c17b5b7607a591a1e47f7d4a65`. Se comprobó la nueva pestaña en la web pública y se envió una pregunta desde su formulario. La API informó que falta `GEMINI_API_KEY`; ese es el paso pendiente de activación. Las consultas públicas de salud y estadísticas respondieron correctamente, con 6.375 registros NASA y 27 candidatos.

## Cómo se conectan las partes

El usuario utiliza el dashboard. El dashboard envía solicitudes HTTP a la API. La API valida las solicitudes, consulta o escribe en MongoDB y devuelve una respuesta JSON. El dashboard presenta esa respuesta como una tabla, indicadores o gráficas.

La API es el único componente que se conecta directamente a MongoDB. La contraseña de la base de datos se configura en el entorno del backend. Para la pregunta de IA, la API prepara el contexto de la selección y lo envía a Gemini; después devuelve su respuesta al dashboard. La clave de Gemini también pertenece al backend.

## Qué conserva del segundo corte

La aplicación mantiene las cuatro preguntas del proyecto:

1. ¿Cuántos planetas parecidos a la Tierra conocemos?
2. ¿Qué tan lejos están y cuánto tardaríamos en llegar?
3. ¿Qué tan lejos puede "ver" cada método de descubrimiento?
4. ¿Qué tan extremos pueden ser los planetas y con qué método se encuentran?

Los filtros exploratorios y sus límites se explican en la guía de sustentación. Los registros creados desde la aplicación quedan identificados como **manuales** para distinguirlos del catálogo NASA.

## Requisitos

- Python 3.11 o superior.
- Git y una cuenta en GitHub.
- VS Code con la extensión de Python, si se sigue el entorno propuesto en clase.
- Una base de datos y una colección en MongoDB Atlas con los datos limpios del segundo corte.
- Acceso de red permitido en Atlas para el equipo o servicio donde se ejecute la API.
- Para activar el extra de IA: una clave de [Google AI Studio](https://aistudio.google.com/apikey) con acceso al modelo configurado.

El proyecto utiliza las siete librerías del archivo entregado en clase:

| Librería | Uso |
|---|---|
| `pymongo` | Conectar el backend con MongoDB y consultar o insertar documentos. |
| `pandas` | Organizar las respuestas de la API en tablas para mostrarlas. |
| `fastapi` | Definir las rutas y respuestas del backend. |
| `uvicorn` | Ejecutar el servidor de la API. |
| `streamlit` | Construir la interfaz que se abre en el navegador. |
| `requests` | Enviar solicitudes del dashboard a la API y de la API a Gemini. |
| `python-dotenv` | Cargar la configuración local desde `.env`. |

Pydantic se instala como dependencia de FastAPI y se utiliza para validar los registros y las preguntas. `certifi` se instala como dependencia de `requests` y aporta certificados de confianza para la conexión con Atlas, como en el notebook del segundo corte. Se mantienen las siete entradas del archivo de requisitos; el extra de Gemini reutiliza `requests`. Los módulos incluidos en Python tampoco requieren una instalación aparte.

## Instalación en Mac o Linux

Abre una terminal dentro de la carpeta del proyecto:

```bash
python3 --version
git --version
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Abre `.env` y completa los valores con la conexión, la base de datos y la colección de tu proyecto. Conserva la plantilla `.env.example` sin contraseñas reales.

## Instalación en Windows

Abre PowerShell dentro de la carpeta del proyecto:

```powershell
py --version
git --version
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Completa `.env` con los valores de tu proyecto. Si PowerShell impide activar el entorno, puedes ejecutar el Python del entorno directamente, por ejemplo:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Ese mismo prefijo puede sustituir a `python` en los comandos de ejecución siguientes.

## Configuración de .env

| Variable | Valor o uso |
|---|---|
| `MONGO_URI` | Tu cadena de conexión real de Atlas. Solo se configura en el backend. |
| `MONGO_DB` | `proyecto_segundo_corte`. |
| `MONGO_COLLECTION` | Puedes dejarla vacía para detectar una colección conocida no vacía. |
| `API_BASE_URL` | `http://localhost:8000` para una API local; `https://exoplanetas-api-juanfmarbo.onrender.com` para utilizar la API publicada. |
| `GEMINI_API_KEY` | Clave privada de Google AI Studio. Se configura en el backend para habilitar `/preguntar`. |
| `MODELO_IA` | `gemini-3.6-flash` por defecto, igual que en el ejemplo de clase. |

La detección busca, en este orden, `exoplanetas_presentacion`, `exoplanetas_clase` y `exoplanetas`. Si escribes un nombre en `MONGO_COLLECTION`, se utiliza esa colección. La API normaliza los nombres de campos al formato final del proyecto sin reemplazar los documentos originales.

La colección original `exoplanetas` puede carecer de los indicadores `limite_*`. La API conserva esa ausencia y no supone que valgan `0`; por ello, algunas preguntas pueden quedar sin registros evaluables en esa versión.

Después de cambiar `GEMINI_API_KEY` o `MODELO_IA` en `.env`, reinicia Uvicorn para que lea los nuevos valores. La ausencia de la clave de Gemini afecta a `/preguntar`; las consultas, gráficas y capturas del proyecto base conservan su configuración habitual.

### Certificados de MongoDB en Mac

Para una conexión `mongodb+srv://`, la API utiliza `tlsCAFile=certifi.where()`. Esto proporciona a Python el archivo de certificados de confianza y ayuda cuando la instalación de Python no encuentra los certificados necesarios para validar Atlas. `certifi` ya se utilizaba en el notebook del segundo corte y no actúa como servidor intermediario.

La conexión conserva la verificación del certificado y del nombre del servidor. El ajuste se aplica a las URI SRV; las conexiones locales `mongodb://` conservan sus opciones originales. La referencia técnica está en la [documentación oficial de TLS de PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/security/tls/).

Si aparece `Configura MONGO_URI y MONGO_DB en el archivo .env.`, alguna variable está vacía antes de intentar la conexión: revisa el archivo `.env` junto a `api.py`, guarda y reinicia Uvicorn. El ajuste de certificados no corrige una configuración vacía, una contraseña incorrecta, un problema DNS ni una IP sin acceso en Atlas.

## Ejecutar ambos servicios localmente: dos terminales

Las dos terminales deben estar dentro de la carpeta del proyecto y utilizar el entorno virtual.

### Terminal 1: backend

Activa el entorno:

- Mac o Linux: `source venv/bin/activate`
- Windows: `.\venv\Scripts\Activate.ps1`

Ejecuta:

```bash
python -m uvicorn api:app --reload
```

La documentación interactiva se abre en [http://localhost:8000/docs](http://localhost:8000/docs). Comprueba la conexión en [http://localhost:8000/salud](http://localhost:8000/salud): debe devolver `estado: "ok"` y los nombres correctos de base y colección. Deja esta terminal funcionando mientras utilizas el dashboard.

### Terminal 2: dashboard

Activa el mismo entorno en una segunda terminal y ejecuta:

```bash
python -m streamlit run dashboard.py
```

La interfaz se abre en [http://localhost:8501](http://localhost:8501). Para detener cada programa, utiliza `Ctrl + C` en su terminal.

Para ejecutar el dashboard local utilizando la API publicada, configura `API_BASE_URL=https://exoplanetas-api-juanfmarbo.onrender.com` y ejecuta solamente Streamlit. En ese modo, el backend funciona en Render y la conexión privada con MongoDB se configura allí.

## Usar el dashboard

- En la barra lateral, selecciona nombre, método, procedencia o años y pulsa **Aplicar filtros**.
- **Preguntas del proyecto** muestra los cuatro análisis. Las cifras se calculan sobre toda la selección.
- **Catálogo** muestra páginas de 25, 50 o 100 registros. El CSV descarga solo la página visible.
- **Agregar registro** contiene los cuatro campos obligatorios y las medidas opcionales. Al guardar, la aplicación busca el registro manual recién creado para comprobarlo.
- **Pregúntale a tus datos** recibe una pregunta de hasta 1.000 caracteres y utiliza la selección de filtros aplicada. Conserva la respuesta en la sesión; aplicar filtros, pulsar **Actualizar datos** o seleccionar automáticamente un registro recién creado la limpia para que vuelvas a preguntar sobre los datos actuales.
- Para analizar únicamente los registros originales, selecciona **Solo catálogo NASA**. Deja una medida o su indicador vacíos cuando sean desconocidos.

## Endpoints y uso

Prueba las rutas desde [http://localhost:8000/docs](http://localhost:8000/docs): selecciona una ruta, pulsa **Try it out**, completa los valores y pulsa **Execute**.

| Método y ruta | Función |
|---|---|
| `GET /salud` | Comprobar disponibilidad del backend y conexión a MongoDB. |
| `GET /opciones` | Consultar métodos de descubrimiento y metadatos de la colección. |
| `GET /datos` | Consultar documentos con filtros y paginación. |
| `GET /estadisticas` | Calcular las estadísticas para la selección. |
| `POST /datos` | Validar y guardar un registro manual. |
| `POST /preguntar` | Enviar a Gemini una pregunta sobre el proyecto y los datos de la selección. |

Filtros de lectura, estadísticas y preguntas de IA: `metodo`, `nombre`, `anio_min`, `anio_max`, `solo_candidatos` y `origen` (`todos`, `nasa` o `manual`). En `/datos`, `pagina` y `por_pagina` controlan la porción de la tabla que se devuelve. Las estadísticas y el resumen utilizado por `/preguntar` corresponden a la selección completa, no únicamente a la página visible.

Ejemplo de consulta:

```text
http://localhost:8000/datos?metodo=Transit&anio_min=2020&pagina=1&por_pagina=25
```

Para crear, son obligatorios `planeta`, `estrella`, `metodo_descubrimiento` y `anio_descubrimiento`. Las magnitudes y sus indicadores pueden omitirse cuando no se conocen. Los indicadores de límite admiten `-1`, `0`, `1` o `null`; los análisis que requieren valores puntuales utilizan `0`.

Ejemplo **sintético para pruebas**, que no representa un descubrimiento real:

```json
{
  "planeta": "DEMO-PROYECTO-001",
  "estrella": "Estrella de demostración",
  "metodo_descubrimiento": "Transit",
  "anio_descubrimiento": 2026,
  "radio_tierras": 1.2,
  "insolacion_tierra": 1.0,
  "distancia_sistema_parsec": 10.0,
  "limite_radio": 0,
  "limite_insolacion": 0
}
```

Una creación correcta responde `201`. Un nombre duplicado responde `409`; una entrada inválida, `422`; una base no disponible, `503`. La API fija la procedencia manual de los registros nuevos. Después de crear, consulta `/datos?origen=manual&nombre=DEMO-PROYECTO-001` para verificar la persistencia.

## Extra: preguntar a los datos con Gemini

La integración conserva las herramientas del ejemplo del profesor: `BaseModel` valida la pregunta, FastAPI atiende `POST /preguntar`, `requests.post` llama a la API REST de Gemini y Streamlit muestra la respuesta. El modelo predeterminado es [Gemini 3.6 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash?hl=en).

El backend entrega a Gemini tres tipos de contexto:

1. Una descripción del proyecto y las reglas de las cuatro preguntas.
2. Las estadísticas calculadas por `estadisticas(filtros)` sobre **toda la selección**.
3. Una muestra de **hasta 30 registros** de esa selección para describir ejemplos concretos.

Los totales proceden del resumen completo. La muestra no es toda la colección y no permite concluir que un planeta ausente no exista. Para preguntar por un planeta concreto, busca su nombre en la barra lateral y pulsa **Aplicar filtros** antes de enviar la pregunta. Los valores desconocidos se conservan como desconocidos y los candidatos por radio e insolación no se presentan como habitabilidad demostrada.

Ejemplo para `/docs`: en `POST /preguntar`, selecciona `origen=nasa` y utiliza este cuerpo JSON:

```json
{
  "pregunta": "¿Cuántos candidatos cumplen radio e insolación y qué significa ese resultado?"
}
```

Una respuesta correcta contiene `respuesta`, `modelo`, `total_registros` y `tamano_muestra`. Los dos últimos campos indican el tamaño de la selección y el de la muestra enviada. La pregunta utiliza los filtros de la URL; no se envían `pagina` ni `por_pagina` para limitar el resumen a una página.

En local, configura la clave en `.env` y reinicia la API. Para la aplicación publicada, añádela en **Environment** del servicio de Render, como se explica en [GUIA_DESPLIEGUE.md](GUIA_DESPLIEGUE.md). Streamlit continúa utilizando únicamente `API_BASE_URL`.

La clave viaja a Google en la cabecera `x-goog-api-key`. La API utiliza el endpoint REST [generateContent](https://ai.google.dev/api/generate-content?hl=en), comprueba la respuesta y devuelve mensajes propios ante errores. La operación consulta datos y produce una explicación: no guarda la pregunta en MongoDB ni ejecuta código generado por Gemini. Contrasta las respuestas con las tablas y gráficas del proyecto.

## Archivos del proyecto

| Archivo | Contenido |
|---|---|
| `api.py` | Conexión con MongoDB, filtros, estadísticas, creación de registros y consulta a Gemini. |
| `dashboard.py` | Interfaz de consulta, visualización, creación y preguntas de IA. |
| `requirements.txt` | Las siete dependencias directas utilizadas en clase. |
| `.env.example` | Plantilla de configuración sin credenciales reales. |
| `.gitignore` | Exclusiones para evitar subir secretos y el entorno virtual. |
| `README.md` | Instalación, ejecución, uso y comprobaciones. |
| `GUIA_CODIGO.md` | Recorrido de funciones e importaciones, validación, consultas y estado de la interfaz. |
| `GUIA_SUSTENTACION.md` | Guion de demostración y explicación del código. |
| `PRUEBAS_REALIZADAS.md` | Pruebas locales, confirmación en Mac y verificaciones de la API y el dashboard públicos. |
| `render.yaml` | Plantilla del servicio de la API en Render Free, sin credenciales. |
| `.python-version` | Versión de Python utilizada para construir la API en Render. |
| `GUIA_DESPLIEGUE.md` | Configuración de Render y Streamlit Cloud, conexión con Atlas y verificación de las URLs públicas. |

El archivo `.env` se crea únicamente en el equipo donde se ejecuta el proyecto. No forma parte del repositorio.

## Correspondencia con la rúbrica

La distribución siguiente procede de `GUIA_PROYECTO_FINAL.md`, incluida en el material de clase.

| Componente evaluado | Puntos | Evidencia que se debe demostrar |
|---|---:|---|
| API de lectura: filtros y agregación | 1.2 | Consultas que devuelven datos correctos y estadísticas calculadas sobre el conjunto correspondiente. |
| API de escritura: POST, validación y códigos de estado | 1.0 | Creación de un registro válido y rechazo de una entrada inválida. |
| Dashboard: consume la API, filtra, grafica y crea | 1.4 | Tabla, filtros, gráficas y formulario conectados al backend. |
| Integración, calidad de código y seguridad de credenciales | 0.8 | Recorrido completo entre interfaz, API y MongoDB; código organizado y secretos excluidos. |
| Sustentación y defensa | 0.6 | Explicación del recorrido de los datos y de las decisiones del proyecto. |
| **Total ordinario** | **5.0** | |

La guía contempla un bono de hasta **0.3** por despliegue con URL pública y una penalización de **0.3 a 0.5** por credenciales expuestas. La asignación de la nota corresponde al docente.

El extra de Gemini fue añadido posteriormente por el profesor. Se documenta como una ampliación; no se le asigna un puntaje nuevo sin una indicación del docente.

## Git y credenciales

Revisa los archivos antes de cada commit:

```bash
git status
git diff
git check-ignore .env
```

Si `.env` existe y está excluido, el último comando muestra su nombre. La exclusión evita incorporar archivos nuevos, pero no elimina un secreto que ya se hubiera publicado en un commit anterior. Una credencial publicada debe reemplazarse en su proveedor: Atlas para la base de datos o Google AI Studio para Gemini.

Guarda avances con mensajes concretos, por ejemplo, `Agrega filtros por categoría`. Comprueba en GitHub que `.env` y `venv/` no aparecen y que `.env.example` solo contiene valores de ejemplo.

### Obtener o actualizar el repositorio existente

El repositorio ya tiene historial. Para obtener una copia nueva, ejecuta estos comandos desde la carpeta donde quieras guardarla:

```bash
git clone https://github.com/Juanfmarbo/First-API.git
cd First-API
```

Si ya tienes una copia clonada, revisa tus cambios antes de actualizarla:

```bash
git status
git pull --ff-only
```

Si hay modificaciones locales, revísalas y guárdalas antes de actualizar. El ZIP contiene archivos de trabajo sin el historial de Git; puedes conservarlo como copia o trasladar tus cambios a una copia clonada. Conserva el historial y la configuración remota del repositorio existente.

Para guardar cambios propios, utiliza el ciclo habitual `add`, `commit` y `push`. Configura tu identidad de Git si todavía hace falta. Publicar cambios requiere acceso autenticado a GitHub.

## Despliegue para el bono

La API funciona en Render Free y el dashboard está disponible en Streamlit Community Cloud. El README docente permite presentar la API y/o el dashboard para el bono; este proyecto dispone de ambas URLs. La sustentación y la asignación de la nota corresponden a la evaluación del docente.

La [guía de despliegue](GUIA_DESPLIEGUE.md) detalla los valores de configuración, los secretos y las comprobaciones finales. El archivo `render.yaml` conserva una plantilla del backend. Si ya existe un servicio para esta API, continúa con ese servicio para evitar crear otro.

Para reproducir la configuración del backend, instala las dependencias con:

```bash
python -m pip install -r requirements.txt
```

Y configura el comando de inicio:

```bash
python -m uvicorn api:app --host 0.0.0.0 --port $PORT
```

Configura las variables de MongoDB en el servicio, sin escribirlas en el código. Revisa también el acceso de red de Atlas. Para el dashboard, selecciona `dashboard.py` y configura `API_BASE_URL` con la dirección pública de la API. Una dirección `localhost` identifica el equipo o servicio donde se ejecuta el programa, por lo que no conecta dos servicios distintos en internet.

Las consultas, estadísticas y una creación manual se verificaron en la API pública. En el dashboard público se comprobaron la pantalla completa, los filtros, la paginación y el envío de una captura manual que quedó guardada en Atlas y visible en el catálogo. La aplicación también puede ejecutarse localmente.

## Errores frecuentes

| Síntoma | Qué revisar |
|---|---|
| Falta un módulo | Que la instalación y la ejecución usen el mismo entorno virtual. |
| No se conecta a MongoDB | Cadena de conexión, credenciales, nombres de base y colección, y acceso de red en Atlas. |
| El dashboard no conecta | Que la API siga ejecutándose y que su dirección sea correcta. |
| No aparecen resultados | Filtros seleccionados, base y colección configuradas, y existencia de datos. |
| El puerto 8000 está ocupado | Detener el proceso anterior o elegir otro puerto y actualizar la dirección usada por el dashboard. |
| Un registro es rechazado | Leer el detalle de validación y corregir los campos indicados. |
| `/preguntar` responde `503` | Configurar `GEMINI_API_KEY`, revisar permisos y `MODELO_IA`, y reiniciar o desplegar la API. Google puede rechazar la configuración con `400`, `401`, `403` o `404`; nuestra API lo comunica como `503` con un mensaje propio. |
| Gemini responde `429` | Revisar la cuota disponible en Google AI Studio y esperar antes de volver a preguntar. |
| La pregunta devuelve `504` | La llamada a Gemini superó el tiempo de espera; intentar de nuevo con una pregunta más concreta. |
| La pregunta devuelve `502` | La llamada a Google falló o no produjo una respuesta utilizable; leer el mensaje y volver a intentarlo. |

## Verificación realizada

La integración local completó **112 comprobaciones con 0 fallos**, utilizando MongoDB real local, solicitudes HTTP y AppTest de Streamlit con datos ficticios. Incluyen verificaciones de estado y de contenido, no 112 casos independientes. El alcance y las limitaciones están en [PRUEBAS_REALIZADAS.md](PRUEBAS_REALIZADAS.md).

Posteriormente, el usuario confirmó `/salud = ok` y el funcionamiento del dashboard en su Mac. Esta confirmación se distingue de nuestras pruebas automatizadas.

La API pública completó otras **31 comprobaciones con 0 fallos**, mediante **12 GET y un único POST** contra Atlas. La captura técnica quedó identificada como manual, con magnitudes desconocidas, y se confirmó su persistencia y exclusión del catálogo NASA. Estas cifras corresponden a la prueba inicial de la API, no a una repetición pública de la suite local.

El dashboard público se abrió posteriormente en el navegador, sin login. Se verificaron las tres pestañas de la versión del 2 de noviembre, las cuatro preguntas con gráficas, el filtro NASA y el filtro de candidatos. La selección de 27 candidatos se mostró en dos páginas de 25 y 2 filas.

Se guardó una captura técnica mediante un único envío del formulario público. La interfaz confirmó la creación y mostró exactamente una fila con el nombre guardado. Una verificación separada mediante **6 GET y 12 comprobaciones correctas, con 0 fallos**, confirmó persistencia, procedencia manual, valores desconocidos y exclusión de NASA. La verificación mediante estas consultas terminó el **2 de noviembre de 2026 a las 15:36:00, hora de Bogotá**. Sus comprobaciones se mantienen separadas de las acciones visuales y de las verificaciones anteriores.

La ampliación de Gemini del **8 de noviembre** tiene su propia verificación en `PRUEBAS_REALIZADAS.md`. Las pruebas anteriores no incluyen una respuesta del modelo. Para acreditar una llamada real, debe configurarse la clave, enviar una pregunta y contrastar la respuesta con las estadísticas de la misma selección.
