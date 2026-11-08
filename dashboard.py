"""Interfaz del proyecto de exoplanetas, construida con Streamlit.

Este archivo pide datos a nuestra API con requests. La API es la encargada
de consultar y escribir en MongoDB; el dashboard no conoce su contraseña.

Ejecutar en una terminal distinta de la API:
    python -m streamlit run dashboard.py

Los bloques siguen el recorrido de la pantalla: conexión, filtros,
indicadores, preguntas del proyecto, catálogo, formulario de creación y asistente IA.
"""

import math
import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv


# La dirección puede cambiar al desplegar, sin modificar el resto del código.
load_dotenv()
API = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
ANIO_ACTUAL = datetime.now().year

st.set_page_config(
    page_title="Explorador de exoplanetas",
    page_icon="🪐",
    layout="wide",
)

# Las etiquetas son visibles; los valores son los que entiende la API.
ORIGENES = {
    "Todos los registros": "todos",
    "Solo catálogo NASA": "nasa",
    "Solo registros manuales": "manual",
}
INDICADORES = {
    "Desconocido": None,
    "Valor puntual (0)": 0,
    "Límite superior (1)": 1,
    "Límite inferior (-1)": -1,
}
NOMBRES_COLUMNAS = {
    "planeta": "Planeta",
    "estrella": "Estrella",
    "metodo_descubrimiento": "Método",
    "anio_descubrimiento": "Año",
    "radio_tierras": "Radio (Tierras)",
    "insolacion_tierra": "Insolación (Tierra = 1)",
    "distancia_sistema_parsec": "Distancia (pc)",
    "temperatura_planeta_k": "Temperatura (K)",
    "periodo_orbital_dias": "Período orbital (días)",
    "masa_tierras": "Masa (Tierras)",
    "tipo_masa": "Procedencia de la masa",
    "fuente.nombre": "Fuente",
    "fuente.tabla": "Tabla de origen",
    "distancia_anios_luz": "Distancia (años luz)",
    "viaje_anios": "Viaje a 17 km/s (años)",
    "origen_radio": "Procedencia del radio",
}


def pedir_api(ruta, parametros=None, registro=None, espera=20):
    """Hace GET o POST y devuelve un diccionario; ante un error devuelve None."""
    try:
        if registro is None:
            respuesta = requests.get(
                f"{API}{ruta}", params=parametros, timeout=espera
            )
        else:
            respuesta = requests.post(
                f"{API}{ruta}", params=parametros, json=registro, timeout=espera
            )
    except requests.Timeout:
        st.error(
            "La consulta tardó demasiado. Si el servidor acaba de despertar, "
            "espera unos segundos y vuelve a intentarlo."
        )
        return None
    except requests.ConnectionError:
        st.error(
            "No fue posible conectar con el servicio de datos. "
            "Comprueba que la API esté encendida y vuelve a intentarlo."
        )
        return None
    except requests.RequestException:
        st.error("La petición no se pudo completar. Revisa la conexión e inténtalo otra vez.")
        return None

    try:
        contenido = respuesta.json()
    except ValueError:
        st.error("El servicio respondió en un formato inesperado. No se usaron esos datos.")
        return None

    if not respuesta.ok:
        if ruta == "/preguntar":
            detalle = contenido.get("detail") if isinstance(contenido, dict) else None
            st.error(
                detalle if isinstance(detalle, str)
                else "No se pudo responder la pregunta. Revisa el texto e inténtalo otra vez."
            )
            return None
        mensajes = {
            409: "Ya existe un planeta con ese nombre. Revisa el catálogo antes de crearlo.",
            422: "Hay campos que no cumplen las condiciones del formulario.",
            503: "El servicio no pudo consultar la base de datos. Inténtalo más tarde.",
        }
        st.error(mensajes.get(respuesta.status_code, "No se pudo completar la operación."))
        # FastAPI devuelve una lista de errores cuando Pydantic rechaza un campo.
        if respuesta.status_code == 422 and isinstance(contenido, dict):
            detalle = contenido.get("detail", [])
            if isinstance(detalle, list):
                for error in detalle:
                    campo = ".".join(str(parte) for parte in error.get("loc", [])[1:])
                    st.caption(f"{campo}: {error.get('msg', 'Valor no válido')}")
            elif isinstance(detalle, str):
                st.caption(detalle)
        return None

    if not isinstance(contenido, dict):
        st.error("La respuesta no tiene la estructura esperada para esta aplicación.")
        return None
    return contenido


def numero(valor, decimales=0):
    """Presenta números en español y conserva la diferencia entre cero y ausencia."""
    if valor is None:
        return "Sin dato"
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def preparar_tabla(registros, columnas):
    """Aplana fuente, conserva las columnas solicitadas y les pone títulos legibles."""
    tabla = pd.json_normalize(registros)
    presentes = [columna for columna in columnas if columna in tabla.columns]
    return tabla[presentes].rename(columns=NOMBRES_COLUMNAS)


def mostrar_preguntas(resumen):
    """Responde las cuatro preguntas usando agregaciones de toda la selección."""
    st.subheader("1. ¿Cuántos planetas parecidos a la Tierra conocemos?")
    st.write(
        "Seleccionamos radios entre **0,8 y 1,6 Tierras** e insolaciones entre "
        "**0,35 y 1,5 veces la terrestre**, incluidos los extremos. Ambos valores "
        "deben ser positivos y estar identificados como valores puntuales."
    )
    st.caption(
        "Es una comparación exploratoria de tamaño y energía recibida. "
        "Cumplir estos intervalos no demuestra habitabilidad ni presencia de vida."
    )
    candidatos = resumen["candidatos"]
    evaluables = resumen["evaluables"]
    if resumen["total"] > 0 and evaluables == 0:
        st.info(
            "Esta selección no tiene registros evaluables con la regla del proyecto. "
            "Pueden faltar el radio, la insolación o sus indicadores de valor puntual. "
            "Eso impide clasificar los registros; no significa que se haya descartado "
            "su semejanza con la Tierra."
        )
    clasificacion = pd.DataFrame({
        "Resultado": ["Cumplen ambos criterios", "No cumplen ambos", "Sin información suficiente"],
        "Planetas": [candidatos, evaluables - candidatos, resumen["sin_informacion"]],
    })
    izquierda, derecha = st.columns([2, 1])
    with izquierda:
        st.bar_chart(clasificacion, x="Resultado", y="Planetas", sort=False)
    with derecha:
        porcentaje = resumen["porcentaje_candidatos"]
        texto_porcentaje = "No calculable" if porcentaje is None else f"{numero(porcentaje, 1)} %"
        st.metric("Cumplen entre los evaluables", texto_porcentaje)
        st.write(f"**{numero(candidatos)}** cumplen entre **{numero(evaluables)}** evaluables.")
        st.caption("El denominador excluye los casos sin información suficiente.")

    st.divider()
    st.subheader("2. ¿Qué tan lejos están y cuánto tardaríamos en llegar?")
    st.write(
        "Comparamos hasta diez candidatos con la menor distancia conocida "
        "dentro de la selección actual."
    )
    cercanos = resumen["cercanos"]
    if cercanos:
        tabla = preparar_tabla(cercanos, [
            "planeta", "distancia_anios_luz", "viaje_anios", "radio_tierras",
            "insolacion_tierra", "origen_radio", "fuente.nombre",
        ])
        st.bar_chart(
            tabla, x="Planeta", y="Distancia (años luz)",
            horizontal=True, sort=False,
        )
        st.dataframe(tabla, use_container_width=True, hide_index=True)
        st.caption(
            f"Hay {numero(resumen['candidatos_con_distancia'])} candidatos con distancia "
            "conocida en esta selección. La tabla presenta como máximo los diez más cercanos."
        )
    else:
        st.info("No hay candidatos con distancia disponible bajo los filtros actuales.")
    st.caption(
        "Un año luz es una distancia. Usamos 1 pc ≈ 3,26 años luz y "
        "años de viaje = distancia en años luz × (299.792,458 / 17). "
        "El viaje supone 17 km/s constantes y no incluye aceleración ni frenado."
    )

    st.divider()
    st.subheader('3. ¿Qué tan lejos puede "ver" cada método de descubrimiento?')
    st.write(
        "La comparación describe distancias de descubrimientos registrados. "
        "No establece el alcance máximo de un instrumento ni cuál método es mejor."
    )
    distancias = pd.DataFrame(resumen["distancias_por_metodo"])
    if not distancias.empty:
        distancias = distancias.rename(columns={
            "metodo": "Método", "cantidad": "Datos con distancia",
            "minima": "Mínima (años luz)", "mediana": "Mediana (años luz)",
            "maxima": "Máxima (años luz)",
        })
        medida = st.radio(
            "Distancia que quieres comparar", ["Mediana (años luz)", "Máxima (años luz)"],
            horizontal=True, key="medida_distancia",
        )
        st.bar_chart(
            distancias.sort_values(medida), x="Método", y=medida,
            horizontal=True, sort=False,
        )
        st.dataframe(distancias, use_container_width=True, hide_index=True)
        st.caption("La mediana resume el centro. La máxima identifica el registro más lejano de cada grupo.")
    else:
        st.info("No hay distancias y métodos disponibles para esta comparación.")

    st.divider()
    st.subheader("4. ¿Qué tan extremos pueden ser los planetas y con qué método se encuentran?")
    st.caption(
        "Infierno: T > 2.000 K · Relámpago: período < 1 día · Congelado: T < 100 K · "
        "Supergigante: masa catalogada > 13 × 317,8 masas terrestres. "
        "Son etiquetas del proyecto; sus categorías pueden coincidir."
    )
    if "planetas_con_extremos" in resumen:
        st.write(
            f"**{numero(resumen['planetas_con_extremos'])} planetas** tienen al menos "
            "uno de los extremos. Cada planeta se cuenta una vez en esta cifra."
        )
    extremos = pd.DataFrame(resumen["extremos"])
    if not extremos.empty:
        extremos = extremos.rename(columns={
            "tipo": "Criterio", "casos": "Casos", "evaluables": "Evaluables",
        })
        # Una división entre cero no debe producir un porcentaje aparentemente válido.
        extremos["Porcentaje entre evaluables"] = [
            100 * casos / disponibles if disponibles else None
            for casos, disponibles in zip(extremos["Casos"], extremos["Evaluables"])
        ]
        st.dataframe(extremos, use_container_width=True, hide_index=True)
    por_metodo = pd.DataFrame(resumen["extremos_por_metodo"])
    if not por_metodo.empty:
        criterio = st.selectbox(
            "Comparar un extremo entre métodos",
            ["Infierno", "Relámpago", "Congelado", "Supergigante"], key="criterio_extremo",
        )
        por_metodo = por_metodo.rename(columns={"metodo": "Método"})
        if criterio in por_metodo.columns:
            st.bar_chart(
                por_metodo, x="Método", y=criterio, horizontal=True, sort=False,
            )
            st.caption("Las barras son conteos de casos. Los grupos pueden tener tamaños distintos.")
            denominadores = pd.DataFrame(resumen.get("evaluables_extremos_por_metodo", []))
            if not denominadores.empty and criterio in denominadores.columns:
                casos_metodo = por_metodo[["Método", criterio]].rename(columns={criterio: "Casos"})
                denominadores = denominadores[["metodo", criterio]].rename(
                    columns={"metodo": "Método", criterio: "Evaluables"}
                )
                comparacion = casos_metodo.merge(denominadores, on="Método", how="left")
                comparacion["Porcentaje entre evaluables"] = [
                    100 * casos / disponibles if pd.notna(disponibles) and disponibles > 0 else None
                    for casos, disponibles in zip(comparacion["Casos"], comparacion["Evaluables"])
                ]
                st.dataframe(comparacion, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos para comparar extremos por método en esta selección.")
    st.caption(
        "Cada criterio tiene su propio número de evaluables. Excluimos valores "
        "reportados como límites y, en extremos térmicos, el método Imaging. "
        "La masa catalogada puede tener distintas procedencias."
    )


def mostrar_catalogo(filtros, resumen):
    """Consulta solo la página visible, sin confundirla con el total de coincidencias."""
    st.subheader("Catálogo de la selección")
    cantidad = st.selectbox("Registros por página", [25, 50, 100], key="por_pagina")
    paginas = max(1, math.ceil(resumen["total"] / cantidad))
    # El cambio de filtros o del tamaño de página puede reducir el número de páginas.
    if st.session_state["pagina"] > paginas:
        st.session_state["pagina"] = paginas
    pagina = st.number_input(
        "Página", min_value=1, max_value=paginas, step=1, key="pagina",
    )
    parametros = dict(filtros)
    parametros.update({"pagina": int(pagina), "por_pagina": cantidad})
    respuesta = pedir_api("/datos", parametros=parametros)
    if respuesta is None:
        return
    registros = respuesta["datos"]
    if registros:
        tabla = preparar_tabla(registros, [
            "planeta", "estrella", "metodo_descubrimiento", "anio_descubrimiento",
            "radio_tierras", "insolacion_tierra", "distancia_sistema_parsec",
            "temperatura_planeta_k", "periodo_orbital_dias", "masa_tierras",
            "fuente.nombre", "fuente.tabla",
        ])
        st.dataframe(tabla, use_container_width=True, hide_index=True)
        st.caption(
            f"Página {respuesta['pagina']} de {max(1, respuesta['paginas'])}: "
            f"{len(registros)} filas visibles de {numero(respuesta['total'])} coincidencias. "
            "La columna Fuente identifica la procedencia."
        )
        st.download_button(
            "Descargar esta página en CSV",
            data=tabla.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"exoplanetas_pagina_{pagina}.csv", mime="text/csv",
        )
        with st.expander("Consultar todos los campos de esta página"):
            st.dataframe(pd.json_normalize(registros), use_container_width=True, hide_index=True)
    else:
        st.info("No hay registros que cumplan estos filtros. Puedes cambiar la selección o agregar uno.")

    with st.expander("Distribución de toda la selección"):
        por_metodo = pd.DataFrame(resumen["por_metodo"])
        if not por_metodo.empty:
            por_metodo = por_metodo.rename(columns={"metodo": "Método", "conteo": "Planetas"})
            st.write("**Registros por método de descubrimiento**")
            st.bar_chart(por_metodo, x="Método", y="Planetas", horizontal=True)
        por_anio = pd.DataFrame(resumen["por_anio"])
        if not por_anio.empty:
            por_anio = por_anio.rename(columns={"anio": "Año", "conteo": "Planetas"})
            por_anio = por_anio.sort_values("Año")
            st.write("**Registros por año de descubrimiento**")
            st.line_chart(por_anio, x="Año", y="Planetas")
            st.caption(
                "Se cuentan los registros actuales que tienen año conocido. "
                "El año en curso puede estar incompleto. No es una reconstrucción histórica del archivo."
            )


def campo_medida(etiqueta, clave, con_indicador=True):
    """Crea un campo numérico opcional y, cuando corresponde, su indicador de límite."""
    valor = st.number_input(
        etiqueta, min_value=0.0, value=None, step=0.01,
        format="%.6f", key=f"nuevo_{clave}",
    )
    indicador = None
    if con_indicador:
        opcion = st.selectbox(
            f"Tipo de dato: {etiqueta}", list(INDICADORES), key=f"indicador_{clave}",
        )
        indicador = INDICADORES[opcion]
    return valor, indicador


def mostrar_formulario(metodos):
    """Valida entradas sencillas y envía el registro completo a POST /datos."""
    st.subheader("Agregar un registro manual")
    st.write(
        "Los cuatro campos con * son obligatorios. Los demás pueden quedar vacíos. "
        "El nuevo registro se identifica como **manual** para distinguirlo del catálogo NASA."
    )
    with st.form("nuevo_registro"):
        izquierda, derecha = st.columns(2)
        with izquierda:
            planeta = st.text_input("Nombre del planeta *", max_chars=150, key="nuevo_planeta")
            metodo = st.selectbox(
                "Método de descubrimiento *", ["Seleccionar"] + metodos, key="nuevo_metodo",
            )
            otro_metodo = st.text_input(
                "Otro método, si no aparece en la lista", max_chars=100, key="nuevo_otro_metodo",
            )
        with derecha:
            estrella = st.text_input("Nombre de la estrella *", max_chars=150, key="nuevo_estrella")
            anio = st.number_input(
                "Año de descubrimiento *", min_value=1, max_value=ANIO_ACTUAL,
                value=ANIO_ACTUAL, step=1, key="nuevo_anio",
            )
        with st.expander("Tamaño y energía recibida"):
            st.caption(
                "Deja el indicador en Desconocido si no tienes esa información. "
                "Un número disponible no garantiza que sea un valor puntual."
            )
            izquierda, derecha = st.columns(2)
            with izquierda:
                radio, limite_radio = campo_medida("Radio (Tierras)", "radio")
            with derecha:
                insolacion, limite_insolacion = campo_medida("Insolación (Tierra = 1)", "insolacion")
            referencia = st.text_input(
                "Referencia del radio, si se conoce", max_chars=2000, key="nuevo_referencia",
            )
        with st.expander("Distancia y órbita"):
            izquierda, derecha = st.columns(2)
            with izquierda:
                distancia, _ = campo_medida("Distancia al sistema (parsecs)", "distancia", False)
            with derecha:
                periodo, limite_periodo = campo_medida("Período orbital (días)", "periodo")
        with st.expander("Temperatura, masa y otros datos"):
            izquierda, derecha = st.columns(2)
            with izquierda:
                temperatura, limite_temperatura = campo_medida("Temperatura del catálogo (K)", "temperatura")
                densidad, _ = campo_medida("Densidad (g/cm³)", "densidad", False)
                lugar = st.text_input(
                    "Lugar del descubrimiento, si se conoce", max_chars=100, key="nuevo_lugar",
                )
            with derecha:
                masa, limite_masa = campo_medida("Masa catalogada (Tierras)", "masa")
                tipo_masa = st.text_input(
                    "Procedencia de la masa, si se conoce", max_chars=100, key="nuevo_tipo_masa",
                )
        enviar = st.form_submit_button("Guardar registro", type="primary")

    if not enviar:
        return
    metodo_final = otro_metodo.strip() or (metodo if metodo != "Seleccionar" else "")
    if not planeta.strip() or not estrella.strip() or not metodo_final:
        st.error("Completa el nombre del planeta, la estrella y el método de descubrimiento.")
        return
    magnitudes = {
        "radio_tierras": radio, "insolacion_tierra": insolacion,
        "distancia_sistema_parsec": distancia, "temperatura_planeta_k": temperatura,
        "periodo_orbital_dias": periodo, "masa_tierras": masa, "densidad_planeta": densidad,
    }
    for campo, valor in magnitudes.items():
        if valor is not None and (not math.isfinite(valor) or valor <= 0):
            st.error(f"{NOMBRES_COLUMNAS.get(campo, campo)} debe ser mayor que cero o quedar vacío.")
            return
    indicadores = {
        "limite_radio": limite_radio, "limite_insolacion": limite_insolacion,
        "limite_temperatura": limite_temperatura, "limite_periodo": limite_periodo,
        "limite_masa": limite_masa,
    }
    # Un campo vacío queda como None. No lo convertimos en un cero físico.
    registro = {
        "planeta": planeta.strip(), "estrella": estrella.strip(),
        "metodo_descubrimiento": metodo_final, "anio_descubrimiento": int(anio),
        "lugar_descubrimiento": lugar.strip() or None,
        "tipo_masa": tipo_masa.strip() or None,
        "referencia_radio": referencia.strip() or None,
        **magnitudes, **indicadores,
    }
    respuesta = pedir_api("/datos", registro=registro)
    if respuesta is not None:
        st.session_state["mensaje_exito"] = (
            f"Se guardó {registro['planeta']} como registro manual. "
            "La selección ahora muestra su nombre para que puedas comprobarlo en el catálogo."
        )
        # El cambio se aplica antes de dibujar los widgets en la siguiente ejecución.
        st.session_state["buscar_recien_creado"] = registro["planeta"]
        st.rerun()


def mostrar_ia(filtros):
    """Envía una pregunta al backend y conserva la respuesta durante la consulta."""
    st.subheader("🤖 Pregúntale a tus datos")
    st.write(
        "Pregunta sobre las cifras de la selección actual o las reglas del proyecto. "
        "Por ejemplo: ¿cuántos cumplen ambos criterios?, ¿qué método tiene más registros? "
        "o ¿cuál de los candidatos está más cerca?"
    )
    st.caption(
        "Se envían a Gemini tu pregunta, las estadísticas de toda la selección y una "
        "muestra de hasta 30 registros. Para consultar un planeta concreto, búscalo "
        "por nombre en la barra lateral y pulsa Aplicar filtros."
    )
    with st.form("formulario_ia"):
        pregunta = st.text_input(
            "Escribe tu pregunta", max_chars=1000, key="pregunta_ia",
            placeholder="¿Cuántos planetas cumplen los criterios del proyecto?",
        )
        enviar = st.form_submit_button("Preguntar", type="primary")

    if enviar:
        st.session_state.pop("respuesta_ia", None)
        if not pregunta.strip():
            st.warning("Escribe una pregunta antes de pulsar Preguntar.")
        else:
            with st.spinner("Pensando..."):
                resultado = pedir_api(
                    "/preguntar", parametros=filtros,
                    registro={"pregunta": pregunta.strip()}, espera=60,
                )
            if resultado is not None:
                respuesta = resultado.get("respuesta")
                if isinstance(respuesta, str) and respuesta.strip():
                    st.session_state["respuesta_ia"] = {
                        "pregunta": pregunta.strip(), "filtros": dict(filtros),
                        **resultado,
                    }
                else:
                    st.error("La API no devolvió una respuesta de texto válida.")

    guardada = st.session_state.get("respuesta_ia")
    if guardada and guardada["filtros"] == filtros:
        st.write(f"**Pregunta respondida:** {guardada['pregunta']}")
        st.success(guardada["respuesta"])
        st.caption(
            f"Modelo: {guardada['modelo']} · Resumen de "
            f"{numero(guardada['total_registros'])} registros · "
            f"{guardada['tamano_muestra']} ejemplos enviados. "
            "Comprueba las cifras con las tablas y gráficas del proyecto."
        )


# --------------------- Inicio del recorrido de la pantalla ---------------------

st.title("🪐 Explorador de exoplanetas")
st.write("### ¿Hay otras Tierras y qué tan lejos están?")
st.write(
    "Explora los registros del proyecto, compara las cuatro preguntas, "
    "agrega nuevos datos con su procedencia identificada y pregúntale a Gemini."
)

if "filtros" not in st.session_state:
    st.session_state["filtros"] = {"origen": "todos"}
if "pagina" not in st.session_state:
    st.session_state["pagina"] = 1

opciones = pedir_api("/opciones")
if opciones is None:
    st.button("Volver a intentar")
    st.stop()

metodos = sorted(opciones["metodos"])
for advertencia in opciones.get("advertencias", []):
    st.warning(advertencia)
# Si se añadió un registro, sincronizamos filtros y widgets antes de crearlos.
if "buscar_recien_creado" in st.session_state:
    st.session_state.pop("respuesta_ia", None)
    nombre_nuevo = st.session_state.pop("buscar_recien_creado")
    st.session_state["filtros"] = {"nombre": nombre_nuevo, "origen": "manual"}
    st.session_state["f_nombre"] = nombre_nuevo
    st.session_state["f_metodo"] = "Todos"
    st.session_state["f_origen"] = "Solo registros manuales"
    st.session_state["f_candidatos"] = False
    st.session_state["f_usar_anios"] = False
    st.session_state["pagina"] = 1

if "mensaje_exito" in st.session_state:
    st.success(st.session_state.pop("mensaje_exito"))

with st.sidebar:
    st.header("Selecciona los datos")
    st.caption("Estos filtros se aplican a los indicadores, las gráficas y el catálogo.")
    with st.form("formulario_filtros"):
        nombre_filtro = st.text_input("Nombre del planeta o estrella", key="f_nombre")
        metodo_filtro = st.selectbox("Método", ["Todos"] + metodos, key="f_metodo")
        origen_filtro = st.selectbox("Procedencia", list(ORIGENES), key="f_origen")
        solo_candidatos = st.checkbox("Solo cumplen radio e insolación", key="f_candidatos")
        usar_anios = st.checkbox("Aplicar intervalo de años", key="f_usar_anios")
        anio_minimo = st.number_input(
            "Desde", min_value=1, max_value=ANIO_ACTUAL,
            value=min(ANIO_ACTUAL, max(1, int(opciones.get("anio_min") or 1990))),
            step=1, key="f_anio_min",
        )
        anio_maximo = st.number_input(
            "Hasta", min_value=1, max_value=ANIO_ACTUAL,
            value=min(ANIO_ACTUAL, max(1, int(opciones.get("anio_max") or ANIO_ACTUAL))),
            step=1, key="f_anio_max",
        )
        aplicar = st.form_submit_button("Aplicar filtros", type="primary")
    if aplicar:
        if usar_anios and anio_minimo > anio_maximo:
            st.error("El año inicial no puede superar al año final. Se conserva la selección anterior.")
        else:
            filtros = {"origen": ORIGENES[origen_filtro], "solo_candidatos": solo_candidatos}
            if nombre_filtro.strip():
                filtros["nombre"] = nombre_filtro.strip()
            if metodo_filtro != "Todos":
                filtros["metodo"] = metodo_filtro
            if usar_anios:
                filtros.update({"anio_min": int(anio_minimo), "anio_max": int(anio_maximo)})
            st.session_state["filtros"] = filtros
            st.session_state["pagina"] = 1
            st.session_state.pop("respuesta_ia", None)
    if st.button("Actualizar datos"):
        st.session_state.pop("respuesta_ia", None)
    st.caption("Para ver únicamente el catálogo original, elige Solo catálogo NASA.")

filtros = st.session_state["filtros"]
resumen = pedir_api("/estadisticas", parametros=filtros)
if resumen is None:
    st.stop()

columna1, columna2, columna3, columna4 = st.columns(4)
columna1.metric("Registros en toda la colección", numero(resumen["total_coleccion"]))
columna2.metric("Registros de la selección", numero(resumen["total"]))
columna3.metric("Evaluables para radio e insolación", numero(resumen["evaluables"]))
columna4.metric("Cumplen ambos criterios", numero(resumen["candidatos"]))
st.caption(
    "La primera cifra corresponde a toda la colección. Las otras cifras y todas las "
    "gráficas corresponden a la selección completa, no solo a la página visible."
)
if filtros.get("solo_candidatos"):
    st.info(
        "Está activo el filtro de candidatos: en esta selección todos cumplen. "
        "Desactívalo para comparar cumplen, no cumplen y sin información."
    )
if resumen["total_coleccion"] == 0:
    st.info("La colección está vacía. El formulario sigue disponible para crear el primer registro.")

preguntas, catalogo, agregar, ia = st.tabs([
    "Preguntas del proyecto", "Catálogo", "Agregar registro", "Pregúntale a tus datos",
])
with preguntas:
    mostrar_preguntas(resumen)
with catalogo:
    mostrar_catalogo(filtros, resumen)
with agregar:
    mostrar_formulario(metodos)
with ia:
    mostrar_ia(filtros)

st.caption(
    "Fuente del catálogo: NASA Exoplanet Archive, tabla pscomppars. "
    "Los registros ingresados desde esta aplicación conservan una procedencia manual."
)
