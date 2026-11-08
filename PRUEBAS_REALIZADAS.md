# Pruebas realizadas

## 1. Verificación inicial con MongoDB local

La verificación inicial de integración local terminó con **112 comprobaciones y 0 fallos**. Son comprobaciones de condiciones concretas, incluidos códigos HTTP y valores de respuesta; **no representan 112 casos de prueba independientes**.

Se utilizó MongoDB real, versión **8.0.17**, en una instancia local temporal en el puerto 27018. FastAPI se ejecutó con Uvicorn y se consultó mediante HTTP. La interfaz se verificó con **AppTest**, la herramienta oficial incluida en Streamlit.

El conjunto inicial contenía **235 registros ficticios**. Superar 200 permitió comprobar que la paginación y las estadísticas no confundieran una página con toda la selección. Esas cifras pertenecen al entorno de prueba y no son resultados científicos del catálogo NASA. Los registros ficticios no se incluyen como datos del proyecto.

### Qué se comprobó localmente

- Reconocimiento de los tres esquemas del segundo corte: final, clase y borrador; selección de colección y comportamiento con una colección vacía.
- Filtros, páginas y estadísticas de las cuatro preguntas, comparando respuestas con resultados conocidos del conjunto sintético.
- Tratamiento de datos ausentes, NaN, infinitos e indicadores de límite, conservando la diferencia entre información desconocida y valor puntual.
- Creación con respuesta `201` y persistencia comprobada mediante consulta posterior; duplicados con `409`; diez entradas inválidas con `422`, sin inserciones correspondientes.
- Manejo de la API apagada y de MongoDB apagado; respuestas `503` cuando correspondía y mensajes sin cadenas privadas de conexión.
- Interfaz con tres pestañas, filtrado, selección vacía y formulario. Crear desde el formulario guardó el documento, volvió a ejecutar la interfaz y mostró el registro con su confirmación. También se revisaron duplicados y campos obligatorios vacíos sin excepciones de la aplicación.
- Sintaxis válida de Python, ausencia de tabulaciones y sangría de cuatro espacios.

## 2. Certificados y confirmación del usuario en Mac

Se recuperó el uso de `certifi.where()` del notebook del segundo corte para las URI `mongodb+srv://`. En una comprobación posterior se ejecutó `obtener_coleccion` con el cliente real de PyMongo, simulando las respuestas DNS y la lectura inicial para evitar conexiones externas. Se verificó que el contexto TLS utiliza el conjunto de certificados de `certifi`, exige un certificado válido, comprueba el nombre del servidor y conserva los tres tiempos de espera. También se comprobó que una URI local `mongodb://` sigue sin activar TLS por este ajuste.

Esta comprobación aislada y la revisión de sintaxis finalizaron correctamente. La suite inicial de 112 comprobaciones no se repitió para este cambio.

Posteriormente, **el usuario confirmó que `/salud` devolvió `ok` y que el dashboard funcionó en su Mac** después de instalar las dependencias. Esta es una confirmación del usuario en su equipo; no se presenta como una ejecución adicional de nuestra suite ni como comprobación individual de todas las funciones.

## 3. Verificación de la API pública con Atlas

El servicio [exoplanetas-api-juanfmarbo](https://exoplanetas-api-juanfmarbo.onrender.com) está publicado en Render **Free**, región **Virginia**. El despliegue utilizado en esta verificación inicial, `dep-dbkeqjl9fdbs739v25og`, del commit `54e134e04deed0487f7b5775f107ef1d17133c32`, terminó el **2 de noviembre de 2026 a las 15:07:50, hora de Bogotá**, con estado `live`.

Se realizaron **12 solicitudes GET y un único POST**, con **31 comprobaciones correctas y 0 fallos**: 22 de lectura y coherencia de resultados, y 9 de creación y persistencia. Son condiciones verificadas sobre las respuestas, no 31 casos independientes. Este registro se mantiene separado de las 112 comprobaciones locales.

Las consultas públicas comprobaron la raíz, `/salud`, `/opciones`, paginación, filtros por procedencia y candidatos, y las estadísticas de las cuatro preguntas. La [documentación interactiva `/docs`](https://exoplanetas-api-juanfmarbo.onrender.com/docs) también se abrió en el navegador. `/salud` confirmó la conexión con `proyecto_segundo_corte`, colección `exoplanetas_presentacion`, esquema `final`.

### Conteos observados antes del POST técnico

| Consulta o alcance | Resultado |
|---|---:|
| Total de documentos de la colección | 6.376 |
| Registros con procedencia NASA | 6.375 |
| Registros manuales existentes | 1 |
| Evaluables para radio e insolación, dentro de NASA | 5.693 |
| Cumplen los dos intervalos del proyecto, dentro de NASA | 27 |
| Información insuficiente para esos dos criterios, dentro de NASA | 682 |
| Métodos disponibles en `/opciones`, antes de la captura técnica | 11 |

`/opciones` no devolvió advertencias en esa lectura. Los conteos son una captura de la colección consultada en esa fecha. La selección de 27 objetos aplica los criterios exploratorios del proyecto y no demuestra habitabilidad.

### Creación y persistencia públicas

El **2 de noviembre de 2026 a las 15:11:14, hora de Bogotá**, se creó `PRUEBA_TECNICA_BONO_20261102_151114`. El POST respondió **201** con identificador `6ae8ee62bf712b90da55d501`. Las consultas posteriores comprobaron que existía exactamente una captura con ese nombre y que el identificador coincidía.

El backend estableció la fuente **Registro manual del proyecto**. Todas las magnitudes e indicadores quedaron en `null`; la captura no añadió candidatos ni extremos y quedó excluida de las consultas con `origen=nasa`. El total de la colección observado después aumentó de **6.376 a 6.377**. El registro técnico permanece identificado como prueba y no representa una observación astronómica.

Los errores `409` y `422` se comprobaron en el entorno local; no se repitieron públicamente en esta fase, que utilizó una sola solicitud POST.

## 4. Verificación del dashboard público en el navegador

El **2 de noviembre de 2026, hora de Bogotá**, se abrió [https://exoplanetasproyecto.streamlit.app/](https://exoplanetasproyecto.streamlit.app/) sin iniciar sesión. Se observó la pantalla completa con **tres pestañas** y las **cuatro preguntas con sus gráficas**.

Antes de la prueba de creación mediante formulario, la interfaz mostró **6.377 documentos en toda la colección**. Se verificaron las siguientes selecciones:

| Operación en la interfaz | Resultado observado |
|---|---|
| Elegir «Solo catálogo NASA» | 6.375 registros, 5.693 evaluables para radio e insolación y 27 candidatos. |
| Activar «Solo cumplen radio e insolación» | 27 registros seleccionados, 27 evaluables y 27 candidatos. |
| Abrir la primera página del catálogo de candidatos | 25 filas. |
| Ir a la segunda página de la misma selección | 2 filas; ambas páginas completan los 27 registros. |

Estos resultados se contrastaron con la API pública, que continuaba disponible con el commit de la verificación inicial y las mismas estadísticas. Las observaciones del navegador se registran por separado de las 112 comprobaciones locales y las 31 comprobaciones iniciales de la API.

### Formulario público

Se efectuó **un único envío desde el formulario público** con el nombre `PRUEBA_DASHBOARD_PUBLICO_1793651649279`. Las consultas de comprobación previas y posteriores al envío se realizaron el **2 de noviembre de 2026 entre las 15:34:56 y las 15:36:00, hora de Bogotá**.

El navegador mostró el mensaje de creación correcta, cambió la procedencia a manual, buscó el nombre recién guardado, desactivó el filtro de candidatos y reinició la página a 1. El catálogo mostró exactamente una fila con ese nombre.

Una comprobación separada utilizó **6 solicitudes GET**, incluida la consulta previa al envío, y obtuvo **12 comprobaciones correctas y 0 fallos**. Este verificador no realizó solicitudes POST. La API confirmó:

- Un registro persistente con identificador `6ae8f3fabf712b90da55d502` y los campos enviados desde el formulario.
- Procedencia **Registro manual del proyecto**, siete magnitudes y cinco indicadores en `null`.
- Ausencia del registro en las consultas con `origen=nasa`.
- Selección de un registro, cero evaluables, cero candidatos y uno sin información suficiente.
- Acceso vigente a Atlas y aumento del total de la colección de **6.377 a 6.378** documentos.

Las 12 comprobaciones de respuesta se distinguen de las acciones observadas en el navegador y de las 31 comprobaciones iniciales de la API. No se afirma que se haya repetido la suite local completa en producción.

### Capturas técnicas conservadas

| Vía de creación | Nombre identificado como prueba |
|---|---|
| API pública | `PRUEBA_TECNICA_BONO_20261102_151114` |
| Formulario del dashboard público | `PRUEBA_DASHBOARD_PUBLICO_1793651649279` |

Estas dos capturas creadas durante la verificación permanecen como registros manuales, con magnitudes desconocidas. No son observaciones astronómicas y quedan fuera del filtro NASA. El total de la colección y el total NASA pueden diferir porque también existen capturas manuales.

## 5. Extra de Gemini: verificación local del 8 de noviembre de 2026

La integración de `POST /preguntar` y la cuarta pestaña del dashboard se comprobó
el **8 de noviembre de 2026 a las 10:19:12, hora de Bogotá**, con **20 métodos de
prueba automatizados, 39 subcasos parametrizados incluidos, 0 fallos y 0 errores**.
Los subcasos forman parte de esos métodos; no se suman como una suite separada.

Las respuestas de Google y las consultas de datos estuvieron **simuladas**.
Se usaron FastAPI `TestClient` y Streamlit `AppTest` para ejecutar la API y la
interfaz reales con esas dependencias externas sustituidas. Esta fase no consumió
una clave real, no llamó a Google y no consultó ni modificó MongoDB.

| Comprobación | Resultado |
|---|---|
| Ruta y contrato | `/preguntar` aparece en OpenAPI y devuelve `respuesta`, `modelo`, `total_registros` y `tamano_muestra`. |
| Validación | Se rechazan preguntas vacías, de solo espacios, mayores de 1.000 caracteres, tipos incorrectos y campos adicionales. |
| Filtros | La muestra y el resumen reciben los mismos filtros validados; se rechazan filtros inválidos. |
| Alcance de los datos | Un caso ficticio con 1.234 registros y 30 ejemplos conserva la diferencia entre total y muestra en el contexto. |
| Credenciales | La clave ficticia aparece en la cabecera de autenticación, sin incorporarse a la URL ni al prompt. |
| Falta de clave | Devuelve `503` antes de consultar datos o llamar a Google. |
| Texto de Gemini | Se unen las partes de texto final y se excluyen las marcadas como `thought`. |
| Errores externos | Se comprobaron HTTP 400, 401, 403, 404, 429 y 500, timeout y fallo de conexión, con mensajes propios. |
| Respuestas no utilizables | JSON inválido, candidatos o partes ausentes, texto vacío, bloqueos y truncamiento producen errores controlados. |
| Interfaz | Aparecen las cuatro pestañas y se conservan los indicadores existentes. |
| Envío del formulario | Una pregunta vacía no se envía; una válida utiliza los filtros y el `timeout=60` configurado. |
| Estado de la respuesta | Una nueva ejecución de la interfaz conserva la respuesta sin otra llamada; aplicar filtros o fallar una pregunta nueva limpia la anterior. |
| Errores visibles | La falta de `GEMINI_API_KEY` y el timeout se muestran sin romper las métricas del dashboard. |

**Alcance pendiente de una clave válida:** obtener una respuesta real de Gemini,
comprobar los permisos y la cuota de la cuenta y contrastar su explicación con las
estadísticas de la selección. Las pruebas simuladas no acreditan esos puntos.
Los pasos para activarlo están en `GUIA_DESPLIEGUE.md`.

## 6. Extra de Gemini: despliegue y formulario públicos

El commit `a4ae5d07c1b4c0c17b5b7607a591a1e47f7d4a65` se desplegó en el servicio
existente de Render. El despliegue `dep-dbo98be7bikc7389t25g` quedó **live el
8 de noviembre de 2026 a las 10:25:43, hora de Bogotá**. La API informa la
versión **1.1.0**.

Entre las **10:26:27 y las 10:26:34 de Bogotá** se hicieron **3 solicitudes GET**
de comprobación y se verificaron **6 condiciones correctas**, sin POST en ese
verificador:

| Consulta | Resultado observado |
|---|---|
| `GET /openapi.json` | HTTP 200; documenta `POST /preguntar` y la versión 1.1.0. |
| `GET /salud` | HTTP 200; `estado: ok`, colección `exoplanetas_presentacion` y 6.379 documentos. |
| `GET /estadisticas?origen=nasa` | HTTP 200; 6.375 registros NASA, 5.693 evaluables, 27 candidatos, 682 sin información suficiente y 462 con algún extremo. |

Por separado, se abrió la web pública, se reactivó tras la suspensión por
inactividad y se comprobó que presenta las cuatro pestañas. Se aplicó el filtro
**Solo catálogo NASA** y se envió una sola pregunta desde **Pregúntale a tus datos**:

> ¿Cuántos planetas cumplen los criterios de radio e insolación y qué significa ese resultado?

La interfaz mostró el mensaje del backend:

> Falta configurar GEMINI_API_KEY en el servidor de la API (Render o .env local).

Esto verifica que el formulario público llega a la nueva ruta y presenta el
diagnóstico previsto de configuración. **No es una respuesta generada por Gemini**:
la clave todavía no está configurada y el backend detiene esta operación antes de
llamar a Google. Los indicadores permanecieron visibles con la selección NASA.
Durante esta ampliación no se crearon registros de prueba en MongoDB.

## 7. Alcance de la entrega técnica

La API y el dashboard del proyecto base están publicados y verificados. Se comprobaron lectura, filtros, paginación y creación persistente desde la interfaz pública, completando el recorrido dashboard → API → Atlas. El extra de Gemini está implementado, publicado y comprobado con servicios simulados; su formulario público presenta correctamente la falta de clave. Requiere activar esa clave y verificar una respuesta real antes de presentarlo como operativo.

El alcance de cada fase queda documentado por separado: integración local, confirmación del usuario en Mac, verificación de la API pública, verificación del dashboard público, pruebas locales de Gemini y comprobación pública de su despliegue y formulario. La sustentación, la calificación y el bono corresponden a la evaluación académica del docente.

El plan de pruebas manuales para repetir la demostración está en `GUIA_SUSTENTACION.md`. La instalación y los comandos se encuentran en `README.md`.
