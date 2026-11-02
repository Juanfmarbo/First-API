# Publicar el proyecto para el bono

El README docente contempla el bono por desplegar la API y/o el dashboard en la nube y entregar la URL pública. Para dejar disponible la aplicación completa, nuestro objetivo es disponer de dos enlaces: uno para la API en Render y otro para el dashboard en Streamlit Community Cloud. Los datos continúan en MongoDB Atlas.

**Preparado** significa que el repositorio contiene el código y la configuración necesarios. **Desplegado y comprobado** significa que ambos servicios tienen una URL real y que las verificaciones del apartado 5 funcionan. Tener este documento o `render.yaml` en GitHub todavía no demuestra que la aplicación esté publicada.

## 1. Antes de comenzar

En el repositorio [Juanfmarbo/First-API](https://github.com/Juanfmarbo/First-API), confirma que la rama `main` contiene `api.py`, `dashboard.py`, `requirements.txt`, `.python-version` y `render.yaml`. Si estos cambios siguen únicamente en otra rama, primero deben incorporarse a `main`.

Ten disponible la conexión privada de Atlas que utiliza el proyecto. Su valor se configura en Render. Las contraseñas no se escriben en este documento, en `render.yaml` ni en el repositorio.

El archivo `.python-version` selecciona Python **3.12**. Render permite indicar la versión mayor y menor en ese archivo y selecciona el parche correspondiente. No hace falta añadir `PYTHON_VERSION` como variable de entorno. Véase [configuración de Python en Render](https://render.com/docs/python-version).

## 2. Configurar la API en Render

### Trabajar con un único servicio

El proyecto necesita un servicio web de Render para la API. Si ya se creó desde la integración de Render o desde su panel, abre ese servicio y revisa su configuración. El dashboard se publica por separado en Streamlit.

Solo cuando todavía no exista el servicio:

1. Entra en [Render](https://dashboard.render.com/) y conecta la cuenta de GitHub que tiene acceso al repositorio.
2. Selecciona **New → Web Service** y conecta `Juanfmarbo/First-API`.
3. Selecciona la rama **main** y completa los valores de la tabla siguiente.
4. Elige el plan de cómputo **Free** y configura las variables descritas más abajo.
5. Pulsa **Create Web Service** y revisa el registro de construcción hasta que arranque.

Este es el flujo de [creación de un servicio web de Render](https://render.com/docs/web-services). La configuración del servicio y la plantilla incluida deben coincidir:

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
| Health Check Path | `/` |

Estos campos corresponden a la [referencia oficial de Blueprints](https://render.com/docs/blueprint-spec). La [guía de FastAPI en Render](https://render.com/docs/deploy-fastapi) utiliza el mismo patrón de arranque; aquí el módulo se llama `api`. El comando de producción no lleva `--reload`.

### Qué hace render.yaml

`render.yaml` conserva una plantilla reproducible con esa configuración. Tenerlo en GitHub no vincula automáticamente el servicio a un Blueprint. **Si la API ya existe, continúa con ese servicio; no crees otra API desde New → Blueprint.**

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

Cuando el servicio esté creado, **copia la URL HTTPS que muestre Render**. El nombre del servicio no garantiza una dirección exacta; utiliza la que realmente te entregue la plataforma.

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

La plantilla `render.yaml` configura `/` como chequeo HTTP y confirma que la API responde. Si el servicio se creó directamente, revisa **Settings → Health Check Path** para comprobar su configuración real: sin una ruta HTTP, Render utiliza su chequeo TCP predeterminado. `/salud` comprueba además el acceso a MongoDB. Usar `/` como chequeo HTTP evita que una conexión inicial lenta a la base supere los cinco segundos que admite el [health check de Render](https://render.com/docs/health-checks). Para dar por terminada la conexión, debe funcionar `/salud`, aunque Render ya indique que el servicio está activo.

## 3. Crear el dashboard en Streamlit Community Cloud

Entra en [Streamlit Community Cloud](https://share.streamlit.io/) con la cuenta de GitHub y selecciona **Create app**. La documentación oficial muestra cómo [elegir repositorio, archivo y configuración](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

Completa:

| Campo | Valor |
|---|---|
| Repository | `Juanfmarbo/First-API` |
| Branch | `main` |
| Main file path | `dashboard.py` |
| Advanced settings → Python version | **3.12** |

En **Advanced settings → Secrets**, introduce esta clave en el nivel principal. Sustituye el texto entre comillas por la URL HTTPS real que copiaste de Render:

```toml
API_BASE_URL = "URL_HTTPS_REAL_COPIADA_DE_RENDER"
```

Ese texto es un marcador para reemplazar, no una dirección publicada. La URL debe apuntar a la raíz del servicio: no agregues `/docs`, `/salud` ni `/datos`.

Conserva las comillas de TOML y no coloques la clave dentro de una sección como `[api]`. Streamlit expone los secretos del nivel principal como variables de entorno, de modo que el `os.getenv` de `dashboard.py` recibe el valor. Consulta [gestión de secretos de Streamlit](https://docs.streamlit.io/develop/concepts/connections/secrets-management).

El dashboard utiliza únicamente la URL de la API. La conexión y la contraseña de MongoDB se configuran en Render.

Guarda la configuración y despliega. Streamlit instalará las dependencias de `requirements.txt`. Cuando termine, copia la URL pública real del dashboard. Si cambias la URL de la API, actualiza `API_BASE_URL` en los ajustes de secretos y reinicia el dashboard si sigue usando el valor anterior. Véase [secretos en Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## 4. Preparar la primera visita y la sustentación

Render Free suspende el servicio después de 15 minutos sin tráfico y puede tardar alrededor de un minuto en arrancar al recibir una nueva solicitud. El dashboard espera 20 segundos por petición, por lo que podría mostrar un mensaje de espera en esa primera visita. Esta limitación está documentada en [Render Free](https://render.com/docs/free).

Antes de la demostración:

1. Abre primero la URL de la API en el navegador.
2. Espera a que responda y comprueba `/salud`.
3. Abre el dashboard o vuelve a cargarlo si lo habías abierto antes.

La configuración de esta guía contempla una instancia **Free** de Render y [Streamlit Community Cloud gratuito](https://docs.streamlit.io/deploy/streamlit-community-cloud). Conserva esos planes. Las instancias Free de Render están sujetas a límites; si la cuenta tiene un medio de pago, ciertos excesos de uso pueden generar cobros. Revisa las condiciones de [Render Free](https://render.com/docs/free) al configurar la cuenta.

## 5. Verificar que el despliegue quedó completo

Realiza estas comprobaciones desde las direcciones públicas:

| Comprobación | Evidencia esperada |
|---|---|
| Raíz de la API | Respuesta con la presentación y las rutas del proyecto. |
| `/salud` | `estado: ok`, base y colección correctas, cantidad coherente con Atlas. |
| `/datos?por_pagina=1` | Una página de datos y el total de la selección. |
| `/estadisticas` | Respuesta con las cuatro preguntas y sus resultados. |
| Dashboard | Preguntas, catálogo y formulario visibles. |
| Filtro del dashboard | Tabla, métricas y gráficas corresponden a la misma selección. |
| Creación manual | Un registro de prueba identificado como manual se guarda y puede consultarse después. |

Para la creación, utiliza un nombre de prueba reconocible y los campos obligatorios. Deja como desconocidas las magnitudes que no correspondan a una observación real. El backend identifica esas capturas como **Registro manual del proyecto**. El catálogo NASA puede consultarse por separado con el filtro de origen.

Para el despliegue completo que estamos preparando, entregaremos **las URLs verificadas de ambos servicios**. El README docente permite presentar la API y/o el dashboard; el requisito del bono es el despliegue en la nube con URL pública. Guarda los enlaces que realmente entregaron las plataformas y la fecha de la verificación. Tener el repositorio preparado o una construcción terminada no demuestra por sí solo que la aplicación funciona públicamente.

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
