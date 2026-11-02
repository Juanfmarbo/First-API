# First-API: explorador de exoplanetas

Aplicación del proyecto final de Programación Aplicada que continúa el trabajo del segundo corte sobre exoplanetas con datos de NASA. Los datos limpios se guardan en MongoDB Atlas, una API con FastAPI los consulta y un dashboard de Streamlit permite trabajar con ellos desde el navegador.

## Cómo se conectan las partes

El usuario utiliza el dashboard. El dashboard envía solicitudes HTTP a la API. La API valida las solicitudes, consulta o escribe en MongoDB y devuelve una respuesta JSON. El dashboard presenta esa respuesta como una tabla, indicadores o gráficas.

La API es el único componente que se conecta directamente a MongoDB. La contraseña de la base de datos se configura en el entorno del backend.

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

El proyecto utiliza las siete librerías del archivo entregado en clase:

| Librería | Uso |
|---|---|
| `pymongo` | Conectar el backend con MongoDB y consultar o insertar documentos. |
| `pandas` | Organizar las respuestas de la API en tablas para mostrarlas. |
| `fastapi` | Definir las rutas y respuestas del backend. |
| `uvicorn` | Ejecutar el servidor de la API. |
| `streamlit` | Construir la interfaz que se abre en el navegador. |
| `requests` | Enviar solicitudes del dashboard a la API. |
| `python-dotenv` | Cargar la configuración local desde `.env`. |

Pydantic se instala como dependencia de FastAPI y se utiliza para validar los registros. No se añade una octava librería al archivo de requisitos. Los módulos incluidos en Python tampoco requieren una instalación aparte.

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
| `API_BASE_URL` | `http://localhost:8000` en local; URL pública del backend al desplegar. |

La detección busca, en este orden, `exoplanetas_presentacion`, `exoplanetas_clase` y `exoplanetas`. Si escribes un nombre en `MONGO_COLLECTION`, se utiliza esa colección. La API normaliza los nombres de campos al formato final del proyecto sin reemplazar los documentos originales.

La colección original `exoplanetas` puede carecer de los indicadores `limite_*`. La API conserva esa ausencia y no supone que valgan `0`; por ello, algunas preguntas pueden quedar sin registros evaluables en esa versión.

## Ejecutar: se necesitan dos terminales

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

## Usar el dashboard

- En la barra lateral, selecciona nombre, método, procedencia o años y pulsa **Aplicar filtros**.
- **Preguntas del proyecto** muestra los cuatro análisis. Las cifras se calculan sobre toda la selección.
- **Catálogo** muestra páginas de 25, 50 o 100 registros. El CSV descarga solo la página visible.
- **Agregar registro** contiene los cuatro campos obligatorios y las medidas opcionales. Al guardar, la aplicación busca el registro manual recién creado para comprobarlo.
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

Filtros de lectura y estadísticas: `metodo`, `nombre`, `anio_min`, `anio_max`, `solo_candidatos` y `origen` (`todos`, `nasa` o `manual`). En `/datos`, `pagina` y `por_pagina` controlan la porción de la tabla que se devuelve. Las estadísticas corresponden a la selección completa, no únicamente a la página visible.

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

## Archivos del proyecto

| Archivo | Contenido |
|---|---|
| `api.py` | Conexión con MongoDB, filtros, estadísticas y creación de registros. |
| `dashboard.py` | Interfaz de consulta, visualización y creación. |
| `requirements.txt` | Las siete dependencias directas utilizadas en clase. |
| `.env.example` | Plantilla de configuración sin credenciales reales. |
| `.gitignore` | Exclusiones para evitar subir secretos y el entorno virtual. |
| `README.md` | Instalación, ejecución, uso y comprobaciones. |
| `GUIA_CODIGO.md` | Recorrido de funciones e importaciones, validación, consultas y estado de la interfaz. |
| `GUIA_SUSTENTACION.md` | Guion de demostración y explicación del código. |
| `PRUEBAS_REALIZADAS.md` | Resultado de la verificación local, su alcance y comprobaciones pendientes. |

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

## Git y credenciales

Revisa los archivos antes de cada commit:

```bash
git status
git diff
git check-ignore .env
```

Si `.env` existe y está excluido, el último comando muestra su nombre. La exclusión evita incorporar archivos nuevos, pero no elimina un secreto que ya se hubiera publicado en un commit anterior. Una credencial publicada debe reemplazarse en Atlas.

Guarda avances con mensajes concretos, por ejemplo, `Agrega filtros por categoría`. Comprueba en GitHub que `.env` y `venv/` no aparecen y que `.env.example` solo contiene valores de ejemplo.

### Subir la carpeta descargada al repositorio del proyecto

El ZIP contiene los archivos de trabajo y no incluye el historial interno de Git.
Si comienzas desde esa carpeta descargada, ejecuta:

```bash
git init
git add .
git commit -m "Completa proyecto de exoplanetas"
git branch -M main
git remote add origin https://github.com/Juanfmarbo/First-API.git
git push -u origin main
```

Si Git todavía no tiene tu identidad configurada, completa primero `git config
--global user.name "Tu nombre"` y `git config --global user.email "Tu correo"`.
La subida requiere iniciar sesión en tu cuenta de GitHub. Si ya trabajas en una
copia clonada de ese repositorio, conserva su configuración remota y usa el
ciclo habitual `add`, `commit` y `push`.

## Despliegue para el bono

El material de clase propone Render para la API y Streamlit Community Cloud para el dashboard. Antes de utilizarlos, revisa las condiciones y los recursos disponibles de cada servicio.

Para el backend, conecta el repositorio, instala las dependencias con:

```bash
pip install -r requirements.txt
```

Y configura el comando de inicio:

```bash
uvicorn api:app --host 0.0.0.0 --port $PORT
```

Configura las variables de MongoDB en el servicio, sin escribirlas en el código. Revisa también el acceso de red de Atlas. Para el dashboard, selecciona `dashboard.py` y configura `API_BASE_URL` con la dirección pública de la API. Una dirección `localhost` identifica el equipo o servicio donde se ejecuta el programa, por lo que no conecta dos servicios distintos en internet.

Comprueba la URL pública con una consulta, una estadística y una creación válida antes de utilizarla en la sustentación. El despliegue es una etapa adicional; la aplicación también puede ejecutarse localmente con las dos terminales.

## Errores frecuentes

| Síntoma | Qué revisar |
|---|---|
| Falta un módulo | Que la instalación y la ejecución usen el mismo entorno virtual. |
| No se conecta a MongoDB | Cadena de conexión, credenciales, nombres de base y colección, y acceso de red en Atlas. |
| El dashboard no conecta | Que la API siga ejecutándose y que su dirección sea correcta. |
| No aparecen resultados | Filtros seleccionados, base y colección configuradas, y existencia de datos. |
| El puerto 8000 está ocupado | Detener el proceso anterior o elegir otro puerto y actualizar la dirección usada por el dashboard. |
| Un registro es rechazado | Leer el detalle de validación y corregir los campos indicados. |

## Verificación realizada

La integración local completó **112 comprobaciones con 0 fallos**, utilizando MongoDB real local, solicitudes HTTP y AppTest de Streamlit con datos ficticios. Incluyen verificaciones de estado y de contenido, no 112 casos independientes. El alcance y las limitaciones están en [PRUEBAS_REALIZADAS.md](PRUEBAS_REALIZADAS.md).

La conexión con Atlas debe comprobarse desde el equipo del usuario. El plan manual de la guía de sustentación permite repetir el recorrido con su configuración y sus datos reales.
