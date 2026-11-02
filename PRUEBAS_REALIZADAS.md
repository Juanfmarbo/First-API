# Pruebas realizadas

## Resultado y entorno

La verificación inicial de integración local terminó con **112 comprobaciones y 0 fallos**. Son comprobaciones de condiciones concretas, incluidos códigos HTTP y valores de respuesta; **no representan 112 casos de prueba independientes**.

Se utilizó MongoDB real, versión **8.0.17**, en una instancia local temporal en el puerto 27018. FastAPI se ejecutó con Uvicorn y se consultó mediante HTTP. La interfaz se verificó con **AppTest**, la herramienta oficial incluida en Streamlit.

El conjunto inicial contenía **235 registros ficticios**. Superar 200 permitió comprobar que la paginación y las estadísticas no confundieran una página con toda la selección. Esas cifras pertenecen al entorno de prueba y no son resultados científicos del catálogo NASA. Los registros ficticios no se incluyen como datos del proyecto.

## Qué se comprobó

- Reconocimiento de los tres esquemas del segundo corte: final, clase y borrador; selección de colección y comportamiento con una colección vacía.
- Filtros, páginas y estadísticas de las cuatro preguntas, comparando respuestas con resultados conocidos del conjunto sintético.
- Tratamiento de datos ausentes, NaN, infinitos e indicadores de límite, conservando la diferencia entre información desconocida y valor puntual.
- Creación con respuesta `201` y persistencia comprobada mediante consulta posterior; duplicados con `409`; diez entradas inválidas con `422`, sin inserciones correspondientes.
- Manejo de la API apagada y de MongoDB apagado; respuestas `503` cuando correspondía y mensajes sin cadenas privadas de conexión.
- Interfaz con tres pestañas, filtrado, selección vacía y formulario. Crear desde el formulario guardó el documento, volvió a ejecutar la interfaz y mostró el registro con su confirmación. También se revisaron duplicados y campos obligatorios vacíos sin excepciones de la aplicación.
- Sintaxis válida de Python, ausencia de tabulaciones y sangría de cuatro espacios.

## Ajuste de certificados para Atlas

Se recuperó el uso de `certifi.where()` del notebook del segundo corte para las URI `mongodb+srv://`. En una comprobación posterior se ejecutó `obtener_coleccion` con el cliente real de PyMongo, simulando las respuestas DNS y la lectura inicial para evitar conexiones externas. Se verificó que el contexto TLS utiliza el conjunto de certificados de `certifi`, exige un certificado válido, comprueba el nombre del servidor y conserva los tres tiempos de espera. También se comprobó que una URI local `mongodb://` sigue sin activar TLS por este ajuste.

Esta comprobación aislada y la revisión de sintaxis finalizaron correctamente. La suite inicial de 112 comprobaciones no se repitió para este cambio. El ajuste todavía debe comprobarse con Atlas desde el Mac del usuario.

## Alcance y límites

Estas pruebas verificaron integración con **MongoDB local**, no con la cuenta de Atlas del usuario. Los intentos de conexión a Atlas desde el entorno de trabajo encontraron fallas de resolución DNS y de conexión TCP; por ello, no se afirma acceso autenticado ni verificación de los documentos reales.

La comprobación pendiente en el equipo del usuario consiste en completar `.env`, ejecutar ambos servicios y revisar `/salud`, el catálogo y una consulta representativa. Tampoco se verificó un despliegue en internet. Publicar el código en GitHub y ejecutar correctamente una URL pública son comprobaciones diferentes.

El plan de pruebas manuales para repetir la demostración está en `GUIA_SUSTENTACION.md`. La instalación y los comandos se encuentran en `README.md`.
