# Guía de sustentación: exoplanetas

## Estado que podemos demostrar

El [dashboard público](https://exoplanetasproyecto.streamlit.app/) abre sin login y muestra las tres pestañas, las cuatro preguntas con gráficas, filtros y paginación verificados. Su formulario también se comprobó: una captura manual se guardó, apareció en el catálogo y se verificó mediante la API. Están disponibles la [API pública en Render](https://exoplanetas-api-juanfmarbo.onrender.com), su [documentación](https://exoplanetas-api-juanfmarbo.onrender.com/docs) y la respuesta de [salud y conexión con Atlas](https://exoplanetas-api-juanfmarbo.onrender.com/salud). La implementación y el despliegue están listos para la entrega técnica y la sustentación.

Para la demostración, abre primero la API y espera su respuesta si Render necesita arrancar. Después abre el dashboard público. La copia local queda como alternativa: si apunta a Render mediante `API_BASE_URL`, basta con ejecutar Streamlit en el equipo. Las pruebas realizadas y sus límites están en `PRUEBAS_REALIZADAS.md`.

## 1. Qué hicimos

> Continuamos el proyecto del segundo corte sobre exoplanetas con datos de NASA. Los datos limpios se guardan en MongoDB Atlas. Creamos una API con FastAPI para consultarlos y agregar registros, y un dashboard con Streamlit para utilizar esas funciones desde el navegador.

Antes de presentar, consulta los conteos actuales y selecciona **Solo catálogo NASA** para explicar resultados del catálogo. Las capturas técnicas de verificación se identifican como manuales y no representan observaciones astronómicas. El registro de pruebas distingue la integración local, la confirmación del usuario en Mac, la API pública y la interfaz pública.

## 2. Cómo viajan los datos

1. El usuario selecciona filtros en el dashboard.
2. `requests` envía la consulta a la API.
3. FastAPI recibe la solicitud y consulta MongoDB mediante `pymongo`.
4. La API responde en JSON, un formato con claves y valores.
5. Streamlit muestra la respuesta como tabla, indicadores o gráficas.

Para crear un registro, el formulario envía un `POST`. Pydantic comprueba sus campos y el backend lo guarda solo si cumple las reglas. Pydantic viene como dependencia de FastAPI.

**La conexión a MongoDB pertenece al backend.** El dashboard se comunica con la API y no necesita la contraseña de Atlas.

## Criterios de las cuatro preguntas

| Pregunta | Criterio conservado del notebook |
|---|---|
| Parecidos a la Tierra | Radio entre 0.8 y 1.6 Tierras e insolación entre 0.35 y 1.5 Tierras; ambos indicadores de límite iguales a 0. |
| Distancia y viaje | Distancia en años luz = parsecs × 3.26. Años de viaje = años luz × 299792.458 / 17, suponiendo 17 km/s constantes. |
| Distancia por método | Comparar las distancias registradas en el catálogo, incluyendo cantidad disponible y resúmenes por método. |
| Extremos | Infierno: temperatura > 2000 K; Congelado: temperatura < 100 K; Relámpago: período < 1 día; Supergigante: masa > 13 × 317.8 Tierras. |

**Cómo interpretar:** parecerse en tamaño e insolación no demuestra habitabilidad. El viaje es un cálculo idealizado. La máxima distancia registrada no es el límite físico de un instrumento. Las categorías de extremos son etiquetas del proyecto y pueden superponerse.

Los extremos requieren una magnitud positiva y un indicador de límite igual a `0`. Los dos filtros de temperatura excluyen `Imaging`, como en el notebook. Un dato ausente o reportado como límite no se considera una medición puntual.

La interfaz permite separar registros NASA y manuales. Los registros de demostración deben identificarse como pruebas al interpretar las cifras.

## 3. Orden de la demostración

1. **Contexto:** explicar qué representa un registro y de dónde vienen los datos.
2. **Consulta:** mostrar la tabla, aplicar un filtro y explicar por qué cambian los resultados.
3. **Estadísticas:** explicar qué mide una gráfica, sus unidades y los datos incluidos.
4. **Validación:** enviar una entrada inválida desde `/docs` y explicar el mensaje recibido.
5. **Creación:** agregar un registro de prueba válido desde el dashboard y volver a consultarlo.
6. **Código:** mostrar una consulta del backend, su validación y una llamada del dashboard.
7. **GitHub:** mostrar el historial y explicar por qué `.env` no está publicado.

Prepara el registro de demostración con un nombre reconocible. Explica que es una prueba y evita presentarlo como un descubrimiento real. No abras la cadena de conexión ni la contraseña durante la exposición.

## 4. Preguntas para practicar

| Pregunta | Respuesta breve |
|---|---|
| ¿Qué es una API? | Una interfaz que define qué solicitudes recibe el backend y cómo responde. |
| ¿Qué es un endpoint? | Una ruta de la API que realiza una operación concreta. |
| ¿Para qué sirve GET? | Para consultar datos. |
| ¿Para qué sirve POST? | En este proyecto, para crear un documento nuevo. |
| ¿Qué diferencia hay entre filtro y agregación? | El filtro selecciona documentos; la agregación calcula un resumen de un conjunto de documentos. |
| ¿Por qué validar también en la API? | Porque recibe solicitudes desde el dashboard, `/docs` y otros clientes. Debe comprobarlas todas. |
| ¿Por qué dos terminales al ejecutar todo localmente? | Una mantiene activo FastAPI y la otra ejecuta Streamlit. Si el dashboard usa la API de Render, el backend ya se ejecuta allí. |
| ¿Para qué sirve Uvicorn? | Para ejecutar el servidor FastAPI. |
| ¿Qué aporta pandas? | Organiza las respuestas en tablas para presentarlas. |
| ¿Qué pasa al cerrar el dashboard? | Los documentos permanecen en MongoDB; la interfaz no es donde se almacenan. |
| ¿Qué diferencia hay entre Git y GitHub? | Git registra versiones; GitHub aloja el repositorio remoto. |
| ¿Qué hace .gitignore? | Excluye archivos nuevos del seguimiento, como `.env` y `venv/`. No elimina secretos ya publicados. |
| ¿Qué aporta el entorno virtual? | Mantiene juntas las dependencias de este proyecto y separadas de otras instalaciones. |

## 5. Pruebas manuales y evidencia

Esta tabla es un **plan para repetir la demostración**. Las verificaciones de cada entorno están separadas en `PRUEBAS_REALIZADAS.md`. La interfaz pública ya se comprobó para consulta, filtros, paginación y creación persistente. Repite las operaciones que mostrarás en la presentación y explica sus resultados; las pruebas técnicas no sustituyen la defensa del trabajo.

| Comprobación | Resultado esperado | Evidencia |
|---|---|---|
| Abrir API y dashboard | Los dos funcionan usando las instrucciones del README. | Terminales y página de inicio. |
| Consultar sin filtros | Registros de la colección correcta. | Respuesta y tabla. |
| Aplicar un filtro | Todos los resultados cumplen la condición. | Parámetros y registros. |
| Buscar sin coincidencias | Estado vacío claro; el programa sigue funcionando. | Respuesta y mensaje. |
| Revisar una estadística | Coincide con una comprobación independiente sobre los mismos documentos. | Respuesta y cálculo. |
| Crear un registro válido | Respuesta `201` y registro al consultar `origen=manual`. | Confirmación y consulta posterior. |
| Repetir un nombre | Respuesta `409`, sin un segundo documento con ese nombre. | Respuesta y consulta. |
| Enviar una entrada inválida | Respuesta `422` con detalle; no se inserta ese registro. | Respuesta de validación. |
| Detener temporalmente la API | El dashboard informa la falla de conexión. | Mensaje de error. |
| Revisar GitHub | No aparecen `.env`, contraseñas ni el entorno virtual. | Lista de archivos. |
| Repetir la comprobación de la API pública | Consulta, estadísticas y creación funcionan mediante la API de Render. | URL y resultados. |
| Repetir las operaciones del dashboard público | Sus filtros y formulario se comunican con la API y guardan correctamente. | URL de Streamlit y resultados observados. |

Una gráfica visible necesita cifras comprobables. Un mensaje de creación necesita una consulta posterior que confirme la persistencia.

## 6. Qué valora la rúbrica

- Lectura, filtros y agregación: **1.2**.
- Creación, validación y códigos de estado: **1.0**.
- Dashboard que consume la API: **1.4**.
- Integración, calidad y seguridad: **0.8**.
- Sustentación: **0.6**.

Total: **5.0**. La guía permite un bono de hasta **0.3** por despliegue y penaliza las credenciales expuestas. Cada integrante debe poder seguir una solicitud de principio a fin y explicar una decisión técnica.

Fuente de los criterios: `GUIA_PROYECTO_FINAL.md`, material suministrado por el docente.
