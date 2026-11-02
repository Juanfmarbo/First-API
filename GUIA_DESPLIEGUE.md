# Publicar el proyecto para el bono

El README docente contempla el bono por desplegar la API y/o el dashboard en la nube y entregar la URL pública. El proyecto dispone de dos enlaces: uno para la API en Render y otro para el dashboard en Streamlit Community Cloud. Los datos continúan en MongoDB Atlas.

## Estado real al 2 de noviembre de 2026

La **API está desplegada y verificada** en [https://exoplanetas-api-juanfmarbo.onrender.com](https://exoplanetas-api-juanfmarbo.onrender.com). El **dashboard público está disponible y verificado** en [https://exoplanetasproyecto.streamlit.app/](https://exoplanetasproyecto.streamlit.app/) y abre sin iniciar sesión. Se comprobaron las tres pestañas, las cuatro preguntas con sus gráficas, filtros, paginación y creación desde el formulario público, con persistencia en Atlas.

El servicio de Render es `exoplanetas-api-juanfmarbo`, plan **Free**, región **Virginia**. El despliegue utilizado en la verificación inicial, `dep-dbkeqjl9fdbs739v25og`, del commit `54e134e04deed0487f7b5775f107ef1d17133c32`, terminó el **2 de noviembre de 2026 a las 15:07:50, hora de Bogotá**. Su estado se comprobó como `live`; además se verificaron las respuestas de la API y la conexión con Atlas.

Las instrucciones siguientes permiten mantener o reproducir la configuración de los servicios publicados. El detalle de las verificaciones, separado por entorno y etapa, está en `PRUEBAS_REALIZADAS.md`.

## 1. Antes de comenzar

En el repositorio [Juanfmarbo/First-API](https://github.com/Juanfmarbo/First-API), confirma que la rama `main` contiene `api.py`, `dashboard.py`, `requirements.txt`, `.python-version` y `render.yaml`. Si estos cambios siguen únicamente en otra rama, primero deben incorporarse a `main`.

Ten disponible la conexión privada de Atlas que utiliza el proyecto. Su valor se configura en Render. Las contraseñas no se escriben en este documento, en `render.yaml` ni en el repositorio.

El archivo `.python-version` selecciona Python **3.12**. Render permite indicar la versión mayor y menor en ese archivo y selecciona el parche correspondiente. No hace falta añadir `PYTHON_VERSION` como variable de entorno. Véase [configuración de Python en Render](https://render.com/docs/python-version).

## 2. Configurar la API en Render

### Continuar con el servicio existente

La API ya utiliza el servicio `exoplanetas-api-juanfmarbo`. Continúa con él para revisar variables, registros y nuevos despliegues. El dashboard se publica por separado en Streamlit.

Solo cuando todavía no exista el servicio:

1. Entra en [Render](https://dashboard.render.com/) y conecta la cuenta de GitHub que tiene acceso al repositorio.
2. Selecciona **New → Web Service** y conecta `Juanfmarbo/First-API`.
3. Selecciona la rama **main** y completa los valores de la tabla siguiente.
4. Elige el plan de cómputo **Free** y configura las variables descritas más abajo.
5. Pulsa **Create Web Service** y revisa el registro de construcción hasta que arranque.

Este es el flujo de [creación de un servicio web de Render](https://render.com/docs/web-services). La configuración efectiva del servicio publicado es:

| Configuración | Valor |
|---|---|
| Tipo | Web Service |
| Nombre | `exoplanetas-api-juanfmarbo` |
| Runtime | Python |
| Plan de cómputo | Free |
| Región | Virginia, identificada como `virginia` |
| Rama | `main` |
| Directorio raíz | Raíz del repositorio |
| Build Command | `python -m pip install -r requirements.txt` |
| Start Command | `python -m uvicorn api:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | Vacío: chequeo TCP predeterminado. |

Estos campos corresponden a la [referencia oficial de Blueprints](https://render.com/docs/blueprint-spec). La [guía de FastAPI en Render](https://render.com/docs/deploy-fastapi) utiliza el mismo patrón de arranque; aquí el módulo se llama `api`. El comando de producción no lleva `--reload`.

### Qué hace render.yaml

`render.yaml` conserva una plantilla reproducible del backend. Existe una diferencia explícita: la plantilla propone un chequeo HTTP en `/`, mientras que el servicio publicado tiene la ruta vacía y utiliza TCP. Tener el archivo en GitHub no vincula automáticamente el servicio a un Blueprint. **Continúa con la API existente; no crees otra desde New → Blueprint.**

Si en el futuro se decide gestionar el servicio mediante un Blueprint, primero hay que identificar el recurso existente y revisar qué cambios propone Render. A partir de ese momento, las sincronizaciones pueden aplicar la configuración del archivo al servicio. El procedimiento está en [Render Blueprints](https://render.com/docs/infrastructure-as-code).

### Variables de la API

| Variable | Configuración |
|---|---|
| `MONGO_URI` | Conexión privada introducida en **Environment** de Render. |
| `MONGO_DB` | `proyecto_segundo_corte`; revisar que esté definido en el servicio. |
| `MONGO_COLLECTION` | Se omite para utilizar la detección automática de la API. |

Introduce la conexión como valor de `MONGO_URI`, sin escribir `MONGO_URI=` delante. La API busca la primera colección con documentos entre `exoplanetas_presentacion`, `exoplanetas_clase` y `exoplanetas`. Si necesitas una colección específica, agrega `MONGO_COLLECTION` en **Environment** con su nombre real.

En la plantilla, `sync: false` permite solicitar el secreto durante una creación mediante Blueprint, sin guardarlo en GitHub. Para un servicio creado directamente, configura el valor en **Environment**. Si lo corriges después, elige **Save and deploy**. La opción **Save only** guarda el cambio, pero el proceso no lo utiliza hasta el siguiente despliegue. Consulta [variables y secretos en Render](https://render.com/docs/configure-environment-variables).

El `.env` de tu Mac no se copia automáticamente al servicio. Render proporciona las variables directamente al proceso, por lo que no necesitas subir ese archivo.

La URL HTTPS verificada de este servicio es [https://exoplanetas-api-juanfmarbo.onrender.com](https://exoplanetas-api-juanfmarbo.onrender.com). Si se crea otro servicio en el futuro, utiliza la dirección que realmente entregue Render; el nombre por sí solo no garantiza la URL.

### Permitir que Render consulte Atlas

La conexión ahora sale de Render. Si Atlas solo admite la IP del Mac, hay que agregar los rangos correspondientes al servicio:

1. Abre los detalles del servicio en Render.
2. En **Connect → Outbound**, copia los rangos de direcciones de salida.
3. En el proyecto de Atlas, abre **Network Access** y agrega esos rangos a la lista de acceso IP. Conserva las entradas que todavía necesitas para tu equipo.
4. Espera a que las entradas estén activas y vuelve a consultar `/salud`.

Render explica dónde obtener los rangos en [Outbound IP Addresses](https://render.com/docs/outbound-ip-addresses). Atlas admite direcciones individuales y rangos CIDR en su [lista de acceso IP](https://www.mongodb.com/docs/atlas/security/ip-access-list/).

### Comprobar la conexión real

Abre la URL pública de la API y agrega `/salud` al final. La respuesta correcta contiene:

- `estado`: `ok`.
- `base`: la base configurada.
- `coleccion`: la colección seleccionada.
- `esquema`: `final`, `clase` o `borrador`, según los datos.
- `total`: la cantidad real de documentos.

El servicio publicado utiliza **TCP**, con **Health Check Path vacío**. La plantilla propone `/` como alternativa HTTP. `/salud` comprueba además el acceso a MongoDB y devolvió `estado: ok`, base `proyecto_segundo_corte`, colección `exoplanetas_presentacion` y esquema `final`. Las diferencias entre estos chequeos se describen en la [documentación de Render](https://render.com/docs/health-checks).

## 3. Dashboard publicado en Streamlit Community Cloud

La aplicación está publicada en **[https://exoplanetasproyecto.streamlit.app/](https://exoplanetasproyecto.streamlit.app/)**. Para mantenerla, utiliza los ajustes de esa aplicación existente. El procedimiento siguiente sirve para reproducir la instalación en otra aplicación cuando sea necesario.

Para una instalación nueva, entra en [Streamlit Community Cloud](https://share.streamlit.io/) con la cuenta de GitHub y selecciona **Create app**. La documentación oficial muestra cómo [elegir repositorio, archivo y configuración](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

Completa:

| Campo | Valor |
|---|---|
| Repository | `Juanfmarbo/First-API` |
| Branch | `main` |
| Main file path | `dashboard.py` |
| Advanced settings → Python version | **3.12** |

En **Advanced settings → Secrets**, introduce esta clave en el nivel principal con la URL verificada de la API:

```toml
API_BASE_URL = "https://exoplanetas-api-juanfmarbo.onrender.com"
```

La URL apunta a la raíz del servicio publicado: no agregues `/docs`, `/salud` ni `/datos`.

Conserva las comillas de TOML y no coloques la clave dentro de una sección como `[api]`. Streamlit expone los secretos del nivel principal como variables de entorno, de modo que el `os.getenv` de `dashboard.py` recibe el valor. Consulta [gestión de secretos de Streamlit](https://docs.streamlit.io/develop/concepts/connections/secrets-management).

El dashboard utiliza únicamente la URL de la API. La conexión y la contraseña de MongoDB se configuran en Render.

En una instalación nueva, guarda la configuración y despliega; Streamlit instalará las dependencias de `requirements.txt`. En la aplicación existente, si cambias la URL de la API, actualiza `API_BASE_URL` en los ajustes de secretos y reinicia el dashboard si sigue usando el valor anterior. Véase [secretos en Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## 4. Preparar la primera visita y la sustentación

Render Free suspende el servicio después de 15 minutos sin tráfico y puede tardar alrededor de un minuto en arrancar al recibir una nueva solicitud. El dashboard espera 20 segundos por petición, por lo que podría mostrar un mensaje de espera en esa primera visita. Esta limitación está documentada en [Render Free](https://render.com/docs/free).

Antes de la demostración:

1. Abre primero la URL de la API en el navegador.
2. Espera a que responda y comprueba `/salud`.
3. Abre el dashboard o vuelve a cargarlo si lo habías abierto antes.

La API utiliza una instancia **Free** de Render y la interfaz se publica en [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud). Conserva esos planes. Las instancias Free de Render están sujetas a límites; si la cuenta tiene un medio de pago, ciertos excesos de uso pueden generar cobros. Revisa las condiciones de [Render Free](https://render.com/docs/free) al configurar la cuenta.

## 5. Verificar que el despliegue quedó completo

La API pública completó **31 comprobaciones correctas y 0 fallos** mediante **12 GET y 1 POST**. Posteriormente se verificó la interfaz pública y se guardó una captura desde su formulario. La comprobación de esa captura utilizó **6 GET y 12 comprobaciones correctas, con 0 fallos**, y terminó a las **15:36:00 del 2 de noviembre de 2026, hora de Bogotá**. El detalle de cada fase está en [PRUEBAS_REALIZADAS.md](PRUEBAS_REALIZADAS.md).

| Comprobación | Estado y evidencia |
|---|---|
| Raíz de la API | Verificada: HTTP 200 con la presentación y las rutas. |
| `/salud` | Verificada: HTTP 200 y `estado: ok`, con base, colección y esquema correctos. |
| `/datos` | Verificada: paginación y filtros NASA, manual y candidatos. |
| `/estadisticas` | Verificada: respuestas de las cuatro preguntas y coherencia de conteos. |
| POST manual de la API | Verificado: HTTP 201, persistencia y exclusión del catálogo NASA. |
| Dashboard público | Verificado: abre sin login y muestra tres pestañas y las cuatro preguntas con gráficas. |
| Filtros del dashboard | Verificados: NASA muestra 6.375 registros; candidatos muestra 27, todos evaluables. |
| Paginación del dashboard | Verificada: la selección de 27 candidatos ocupa páginas de 25 y 2 filas. |
| Creación desde el formulario público | Verificada: mensaje de éxito, filtro automático por nombre y origen manual, una fila en el catálogo y persistencia comprobada mediante la API. |

Para la creación, utiliza un nombre de prueba reconocible y los campos obligatorios. Deja como desconocidas las magnitudes que no correspondan a una observación real. El backend identifica esas capturas como **Registro manual del proyecto**. El catálogo NASA puede consultarse por separado con el filtro de origen.

Las dos URLs están disponibles y el recorrido completo de consulta y creación está verificado. La implementación y el despliegue quedan listos para entregar y sustentar. El README docente permite presentar la API y/o el dashboard; la sustentación, la nota y la asignación del bono corresponden a la evaluación del docente.

## 6. Si algo no funciona

| Lo que aparece | Qué revisar primero |
|---|---|
| Error durante la instalación | El registro de construcción, la rama `main`, `requirements.txt` y Python 3.12. |
| Render no detecta un puerto | Que el Start Command conserve `--host 0.0.0.0 --port $PORT`. |
| La API pide configurar MongoDB | Que `MONGO_URI` y `MONGO_DB` estén definidos en **Environment** y que se haya desplegado después del cambio. |
| `/salud` responde `503` | La conexión de Atlas, las credenciales, los rangos Outbound permitidos y los nombres de base o colección. |
| El dashboard intenta usar `localhost` | Que `API_BASE_URL` esté en la raíz de **Secrets**, con la URL pública de Render. |
| El primer acceso tarda demasiado | Despertar primero la API y volver a abrir el dashboard cuando `/salud` responda. |
| Hay datos, pero no casos evaluables | Los indicadores `limite_*` de la colección; el borrador puede no incluirlos. |

Los errores de conexión deben resolverse conservando la verificación de certificados TLS. La documentación del código y de los criterios del proyecto está en `GUIA_CODIGO.md` y `GUIA_SUSTENTACION.md`.
