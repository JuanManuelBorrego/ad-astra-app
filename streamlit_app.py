import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import random
import os

from db import query, execute
from clases import Alumno

# --- 1. CONFIGURACIÓN DE PÁGINA (SIEMPRE PRIMERO) ---

st.set_page_config(
    page_title="ASTRA", 
    layout="centered", 
    page_icon="✨" 
)

def aplicar_interfaz_cientifica():
    # 1. DISEÑO VISUAL (CSS) - ASTRA FINAL REINFORCED
    st.markdown("""
        <style>
        /* --- ELIMINAR RECTÁNGULO BLANCO SUPERIOR (Solo el fondo) --- */
        header {
            background-color: rgba(0,0,0,0) !important;
            border-bottom: none !important;
        }
        
        /* Reducir espacio superior */
        .main .block-container {
            padding-top: 1rem !important;
        }

        /* --- FIX PARA LA FLECHITA DEL SIDEBAR (Blanca) --- */
        button[data-testid="stSidebarCollapse"] svg {
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }

        /* --- LOGO DEL SIDEBAR CIRCULAR --- */
        [data-testid="stSidebar"] [data-testid="stImage"] img {
            border-radius: 50%;
            border: 2px solid #00E5FF;
            object-fit: cover;
            width: 150px !important;
            height: 150px !important;
            margin-left: auto;
            margin-right: auto;
            display: block;
        }

        /* --- FONDO Y APP GENERAL --- */
        .stApp {
            background: radial-gradient(circle at top, #1B263B 0%, #0D1B2A 100%);
            background-attachment: fixed;
            color: #FFFFFF !important;
        }

        /* --- TEXTO GENERAL --- */
        label, .stMarkdown p, .stWidgetLabel, h1, h2, h3, .stText, p, span, li {
            color: #FFFFFF !important;
        }

        /* --- FIX SELECTBOX (Texto seleccionado oscuro) --- */
        div[data-baseweb="select"] div {
            color: #0D1B2A !important;
            font-weight: bold !important;
        }

        /* --- MENÚS DESPLEGABLES --- */
        div[data-baseweb="popover"] div, div[data-baseweb="menu"], ul {
            background-color: #1B263B !important;
        }
        div[data-baseweb="popover"] li, [role="option"] {
            color: #FFFFFF !important;
            background-color: #1B263B !important;
        }
        div[data-baseweb="popover"] li:hover, [role="option"]:hover {
            background-color: #FF7043 !important;
            color: #FFFFFF !important;
        }

        /* --- TARJETAS GLASSMORPHISM --- */
        div[data-testid="stForm"], div.stCard, .stExpander {
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(12px);
            padding: 2.5rem;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* --- SIDEBAR --- */
        section[data-testid="stSidebar"] {
            background-color: #0D1B2A !important;
            border-right: 1px solid #1B263B;
        }
        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }

        /* --- BOTONES NARANJA --- */
        .stButton>button {
            background-color: #FF7043 !important;
            color: white !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            text-transform: uppercase;
        }

        /* --- FOOTER --- */
        .footer {
            position: fixed;
            left: 0; bottom: 0; width: 100%;
            background-color: rgba(13, 27, 42, 0.95);
            color: #00E5FF !important;
            text-align: center;
            padding: 12px 0px;
            font-size: 13px;
            border-top: 1px solid #1B263B;
            z-index: 999;
        }
        </style>
    """, unsafe_allow_html=True)

    # LEYENDAS
    st.markdown('<p style="color: #00E5FF; font-size: 12px; text-align: right; font-style: italic; font-weight: bold;">ASTRA: Misión Educativa v1.0</p>', unsafe_allow_html=True)
    st.markdown("""<div class="footer">© 2026 - Proyecto <b>Ad Astra</b> | Prof. Juan Manuel Borrego<br><b>Centro de Navegación de Datos & Didáctica Matemática</b></div>""", unsafe_allow_html=True)

# --- LLAMADA INICIAL ---
aplicar_interfaz_cientifica()

# --- CARGA DE LOGO ---
# Reemplaza 'logo.png' por el nombre real de tu archivo
nombre_logo = "logo.png" 
if os.path.exists(nombre_logo):
    st.sidebar.image(nombre_logo)

# --- EL RESTO DE TU CÓDIGO ---
st.title("✨ ASTRA")
st.caption("Navegación Académica Predictiva")
#-------------------------------------------------------------------------------------------------------------------------
#PARA EL CIERRE DE SESIÓN LUEGO DEL EXAMEN (DESDE EL USUARIO PROFESOR). ESTO SE TERMINA DE EJECUTAR USANDO EL CÓDIGO EN LA SECCIÓN DE CIERRE DENTRO DEL USUARIO PROFESOR

@st.dialog("Confirmar Cierre de Jornada")
def confirmar_cierre_dialog(id_clase, curso):
    st.warning(f"⚠️ Estás por cerrar la **Clase {id_clase}** para el curso **{curso}**.")
    st.write("Esta acción asignará un **1.0** a todos los alumnos que no tengan nota registrada.")
    st.write("¿Estás seguro de continuar?")
    
    col_si, col_no = st.columns(2)
    if col_si.button("Sí, ejecutar cierre", use_container_width=True, type="primary"):
        st.session_state.ejecutar_cierre_real = True
        st.rerun()
    if col_no.button("Cancelar", use_container_width=True):
        st.rerun()

# --- LÓGICA DE SESIÓN (SIN CONFIGURACIONES REPETIDAS) ---
if 'estudiante' not in st.session_state:
    st.session_state.estudiante = None
if 'id_clase_hoy' not in st.session_state:
    st.session_state.id_clase_hoy = None
if 'en_examen' not in st.session_state:
    st.session_state.en_examen = False
if 'respuestas_temporales' not in st.session_state:
    st.session_state.respuestas_temporales = {}
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# --- HASTA AQUÍ ---
# --- SIDEBAR (Selector de modo) ---
with st.sidebar:
    # --- LOGO EN EL SIDEBAR ---
    # use_container_width asegura que se adapte al ancho del menú lateral
    st.sidebar.image("logo_astra.png", use_container_width=True)

    # Un pequeño espacio o línea divisoria para separar el logo de las opciones
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.title("🛡️ Acceso ASTRA") # Actualizamos el nombre aquí también
    modo = st.radio("Sección:", ["Estudiantes", "Profesor"])
    
    if st.session_state.estudiante:
        st.divider()
        # El cambio a st.info le da el toque tecnológico y estelar
        # El toque azul espacial para el nombre
        st.markdown(f"🚀 **Astro:** <span style='color: #004085;'>{st.session_state.estudiante.nombre}</span>", unsafe_allow_html=True) 
        if st.button("Cerrar Sesión"):
            st.session_state.estudiante = None
            st.rerun()
    
    if st.session_state["autenticado"] and modo == "Profesor":
        st.divider()
        if st.button("Cerrar Sesión Docente"):
            st.session_state["autenticado"] = False
            st.rerun()

# ==================================================================================================
# SECCIÓN ESTUDIANTES
# ==================================================================================================
if modo == "Estudiantes":
    if not st.session_state.estudiante:
        st.header("🔑 Identificación de Alumno")
        nombre_ingresado = st.text_input("Ingresá tu nombre exacto:")
        
        # ... dentro de if modo == "Estudiantes" ...
        if st.button("Ingresar al Dashboard"):
            try:
                res = query(
                    "SELECT id_alumno, nombre, curso FROM alumnos WHERE nombre = ?",
                    (nombre_ingresado,)
                )

                if res:
                    fila = res[0]
                    st.session_state.estudiante = Alumno(fila[0], fila[1], fila[2])
                    
                    # ¡IMPORTANTE!: Buscamos la clase activa para el curso de ESTE alumno
                    clase_hoy = obtener_clase_activa(res[2]) 
                    st.session_state.id_clase_hoy = clase_hoy
                    
                    if clase_hoy:
                        st.success(f"Conectado a Clase ID: {clase_hoy}")
                    else:
                        st.warning(f"No hay clase configurada para el curso {res[2]}")
                        
                    st.rerun()
                else:
                    st.error("Alumno no encontrado.")
            except Exception as e:
                st.error(f"Error: {e}")
    
    else:
        # --- CABECERA ---
        st.title(f"👨‍🚀 Astro: {st.session_state.estudiante.nombre}")
        st.divider()

        # --- LÓGICA DE DATOS ---
        notas_anuales = []
        labels_anuales = ['1° Trim', '2° Trim', '3° Trim']
        
        for t in ['1', '2', '3']:
            st.session_state.estudiante.sincronizar_historial_por_trimestre(t)
            
            # 1. Calculamos la tendencia real de ese trimestre para obtener m_esf y m_efi
            res_graf = st.session_state.estudiante.graficar_tendencia()
            
            if isinstance(res_graf, tuple):
                m_esf, m_efi = res_graf
                # 2. Calculamos la nota con los ajustes reales
                res = st.session_state.estudiante.calcular_nota_trimestral(m_esf, m_efi)
                notas_anuales.append(res['total_entero'])
            else:
                # Si no hay datos (res_graf es un mensaje), la nota es 0 o lo que haya en DB
                notas_anuales.append(0)

        # --- VISUALIZACIÓN ---
        col_graf, col_info = st.columns([2, 1])

        with col_graf:
            st.subheader("📊 Rendimiento Anual")
            fig, ax = plt.subplots(figsize=(8, 4))
            colores = ['#3498db', '#9b59b6', '#2ecc71']
            barras = ax.bar(labels_anuales, notas_anuales, color=colores, edgecolor='black')
            ax.axhline(y=6, color='red', linestyle='--', label='Aprobación (6)')
            ax.set_ylim(0, 11)
            
            for bar in barras:
                yval = bar.get_height()
                if yval > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha='center', fontweight='bold')
            
            ax.legend()
            st.pyplot(fig)

        with col_info:
            st.subheader("📝 Estado Académico")
            puntos_totales = sum(notas_anuales)
            st.metric("Puntos Acumulados", f"{puntos_totales} / 18")
            
            if puntos_totales >= 18 and notas_anuales[2] >= 6:
                st.success("✨ ¡Estado: APROBADO EL AÑO!")
            else:
                faltan = 18 - puntos_totales
                if faltan > 0:
                    st.warning(f"Necesitás {faltan} puntos más para aprobar el año.")
                else:
                    st.info("Promedio alcanzado, pero recordá que el 3er trimestre debe ser >= 6.")

        st.divider()
        # --- BOTONES DE ACCIÓN ---
        st.subheader("🎮 Acciones Disponibles")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            # --- 1. VALIDACIÓN: ¿YA EXISTE NOTA EN DB? ---
            ya_rindio = False
            if st.session_state.id_clase_hoy:
                try:
                resultado = query(
                    """
                    SELECT COUNT(*) FROM reportes_diarios 
                    WHERE id_alumno = ? AND id_clase = ?
                    """,
                    (st.session_state.estudiante.id, st.session_state.id_clase_hoy)
                )

                if resultado and resultado[0][0] > 0:
                    ya_rindio = True

            except Exception as e:
                st.error(f"Error de validación: {e}")

            # --- 2. LÓGICA DE ACCESO (EL CORAZÓN DEL CAMBIO) ---
            if ya_rindio:
                st.success("✅ EXAMEN COMPLETADO")
                st.info("Ya tienes un reporte registrado para esta clase.")
                st.session_state.en_examen = False 
            else:
                if st.button("🚀 RENDIR EXAMEN"):
                    if st.session_state.id_clase_hoy:
                        # VALIDAMOS SI EL PROFESOR TIENE EL SWITCH ABIERTO
                        if st.session_state.estudiante.clase_esta_activa():
                            st.session_state.en_examen = True
                            st.rerun()
                        else:
                            # SOLO CARTEL, SIN GUARDAR NADA
                            st.error("🚫 El examen del día no está disponible en este momento.")
                    else:
                        st.warning("⚠️ No hay una clase activa hoy.")

            # --- 3. BLOQUE DE EXAMEN (DURANTE LA RESOLUCIÓN) ---
            if st.session_state.get('en_examen', False) and not ya_rindio:
                st.markdown("---")
                
                # Si el profesor cierra el examen mientras el alumno está respondiendo
                if not st.session_state.estudiante.clase_esta_activa():
                    st.error("🛑 ¡TIEMPO AGOTADO! El profesor ha cerrado el acceso.")
                    st.session_state.en_examen = False
                    st.session_state.respuestas_temporales = {}
                    # NO llamamos a registrar_clase, solo ponemos un botón para salir
                    if st.button("Regresar al Panel"):
                        st.rerun()
                else:
                    # RENDERIZADO DEL FORMULARIO DE PREGUNTAS
                    try:
                        filas = query(
                            """
                            SELECT id_pregunta, enunciado, opc_a, opc_b, opc_c, opc_d, correcta 
                            FROM preguntas 
                            WHERE id_clase = ?
                            """,
                            (st.session_state.id_clase_hoy,)
                        )

                        df_preguntas = pd.DataFrame(
                            filas,
                            columns=[
                                "id_pregunta", "enunciado", 
                                "opc_a", "opc_b", "opc_c", "opc_d", "correcta"
                            ]
                        )
                    
                        with st.form("examen_web"):
                            st.subheader(f"📝 Examen Clase {st.session_state.id_clase_hoy}")
                            
                            for idx, fila in df_preguntas.iterrows():
                                # AGREGAMOS LA OPCIÓN NEUTRAL
                                opciones = [fila['opc_a'], fila['opc_b'], fila['opc_c'], fila['opc_d'], "⚪ No lo sé / No responder"]
                                
                                # El mapeo ahora incluye la opción 'N' (Nula/Ninguna)
                                mapeo = {
                                    fila['opc_a']:'A', 
                                    fila['opc_b']:'B', 
                                    fila['opc_c']:'C', 
                                    fila['opc_d']:'D', 
                                    "⚪ No lo sé / No responder":'N'
                                }
                                
                                # index=4 hace que aparezca seleccionada por defecto la opción "No lo sé"
                                sel = st.radio(f"{idx+1}. {fila['enunciado']}", opciones, index=4, key=f"pregunta_{fila['id_pregunta']}")
                                st.session_state.respuestas_temporales[fila['id_pregunta']] = mapeo[sel]
                    
                            if st.form_submit_button("Finalizar y Entregar"):
                                aciertos = 0
                                completados = 0  # <--- NUEVA VARIABLE
                                
                                for _, f in df_preguntas.iterrows():
                                    rta = st.session_state.respuestas_temporales.get(f['id_pregunta'])
                                    
                                    # REGLA: Solo cuenta como completado si la respuesta NO es 'N'
                                    if rta != 'N':
                                        completados += 1
                                        if rta == f['correcta']:
                                            aciertos += 1
                                
                                # Ahora enviamos 'completados' en lugar de 'len(df_preguntas)'
                                nota = st.session_state.estudiante.registrar_clase(
                                    st.session_state.id_clase_hoy, completados, aciertos
                                )
                    
                                # --- EFECTOS NATIVOS ---
                                st.balloons() 
                                st.success(f"✅ ¡Entregado! Nota: {nota}")
                                
                                import time
                                time.sleep(2)
                                
                                st.session_state.en_examen = False
                                st.session_state.respuestas_temporales = {}
                                st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error al cargar examen: {e}")
        with c2:
            if st.button("📚 REPASAR CLASES"):
                st.session_state.ver_historial = not st.session_state.get('ver_historial', False)

            if st.session_state.get('ver_historial', False):
                st.markdown("---")
                st.subheader("📖 Tu Historial de Aprendizaje")
                
                try:
                    id_actual = st.session_state.estudiante.id
                    
                    # 1. Definimos la Query con la Opción B y el redondeo
                    sql_repaso= """
                        SELECT 
                            c.fecha as 'Fecha', 
                            c.tema as 'Tema', 
                            r.asistencia as 'Asistencia',
                            CAST(c.ejercicios_totales AS INTEGER) as 'Ejercicios del día',
                            CAST(r.ejercicios_completados AS INTEGER) as 'Total resueltos',
                            CAST(r.ejercicios_correctos AS INTEGER) as 'Total correctos',
                            r.nota_oral as 'Nota examen Oral',
                            ROUND(
                                CASE 
                                    WHEN r.nota_oral > 0 THEN r.nota_oral
                                    WHEN r.ejercicios_completados = 0 THEN 1.0
                                    ELSE (
                                        (CAST(r.ejercicios_completados AS REAL) / c.ejercicios_totales) + 
                                        (CAST(r.ejercicios_correctos AS REAL) / r.ejercicios_completados)
                                    ) / 2 * 10
                                END, 2
                            ) as 'Nota final de la clase'
                        FROM reportes_diarios r
                        JOIN clases c ON r.id_clase = c.id_clase
                        WHERE r.id_alumno = ?
                        ORDER BY c.fecha DESC
                    """

                    filas = query(sql_repaso, (id_actual,))
                    df_repaso = pd.DataFrame(
                        filas,
                        columns=[
                            "Fecha",
                            "Tema",
                            "Asistencia",
                            "Ejercicios del día",
                            "Total resueltos",
                            "Total correctos",
                            "Nota examen Oral",
                            "Nota final de la clase"
                        ]
                    )
                    # 2. Procesamos y mostramos la tabla
                    if not df_repaso.empty:
                        # Forzamos los enteros para que no aparezca el .0
                        cols_int = ['Ejercicios del día', 'Total resueltos', 'Total correctos']
                        for col in cols_int:
                            df_repaso[col] = pd.to_numeric(df_repaso[col], errors='coerce').fillna(0).astype(int)

                        st.dataframe(
                            df_repaso.style.applymap(
                                lambda x: 'color: #FF4B4B; font-weight: bold' if x == 'AUSENTE' else 'color: #28a745',
                                subset=['Asistencia']
                            ).background_gradient(
                                subset=['Nota final de la clase'], 
                                cmap='RdYlGn', vmin=1, vmax=10
                            ).format({
                                "Nota examen Oral": "{:.2f}", 
                                "Nota final de la clase": "{:.2f}",
                                "Ejercicios del día": "{:d}",
                                "Total resueltos": "{:d}",
                                "Total correctos": "{:d}"
                            }, na_rep="-"), 
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("Aún no tienes registros para mostrar.")
                
                except Exception as e:
                    st.error(f"Error al procesar historial: {e}")
        with c3:
            trim_sel = st.selectbox("Ver detalle de trimestre:", [1, 2, 3], index=2)
    
        # --- DETALLE DEL TRIMESTRE SELECCIONADO ---
        st.header(f"📍 Detalle: {trim_sel}° Trimestre")
        st.session_state.estudiante.sincronizar_historial_por_trimestre(str(trim_sel))
        
        if len(st.session_state.estudiante.historial) == 0:
            st.info(f"Todavía no hay registros cargados para el {trim_sel}° trimestre.")
        else:
            col_ia, col_notas = st.columns([1, 1])
            res_graf = st.session_state.estudiante.graficar_tendencia()
            
            with col_ia:
                st.subheader("🤖 Tutor Virtual")
                if isinstance(res_graf, tuple):
                    m_esf, m_efi = res_graf
                    mensaje_ia = st.session_state.estudiante.interpretar_tendencia(m_efi, m_esf)
                    st.info(mensaje_ia)
                    st.pyplot(plt.gcf()) 
                else:
                    st.write(res_graf)

            with col_notas:
                st.subheader("🚩 Nota Proyectada")
                if isinstance(res_graf, tuple):
                    dt = st.session_state.estudiante.calcular_nota_trimestral(m_esf, m_efi)
                    desglose = {
                        "Concepto": ["Promedio Base", "Ajuste Esfuerzo", "Ajuste Concentración", "TOTAL DECIMAL"],
                        "Valor": [f"{dt['promedio']:.2f}", f"{dt['ajuste_esfuerzo']}", f"{dt['ajuste_eficacia']}", f"{dt['total_decimal']}"]
                    }
                    st.table(pd.DataFrame(desglose))
                    st.metric("NOTA FINAL (SAGE)", dt['total_entero'])
                    
                    if dt['total_entero'] >= 6:
                        st.success("✅ Si terminase hoy el trimestre, estarías aprobando ¡¡A no bajar la guardia!!")
                    else:
                        st.error("❌ Por debajo de la nota de aprobación.")
                        
# ==================================================================================================
# SECCIÓN DEL PROFESOR (Protegida por login y modo)
# ==================================================================================================

elif modo == "Profesor":
    if not st.session_state["autenticado"]:
        st.markdown("<h1 style='text-align: center;'>🔐 Acceso Docente</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            clave = st.text_input("Ingrese Clave de Administrador:", type="password")
            if st.button("Ingresar", use_container_width=True):
                if clave == "35445771": # Tu clave actual
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("❌ Clave incorrecta.")
    else:
        # --- SIDEBAR: ESTADO ACTUAL (LECTURA) ---
        st.sidebar.title("🍎 Panel de Control")
        st.sidebar.write(f"**Bienvenido, Profesor**")
        st.sidebar.divider()
        
        # Consultamos el estado actual para mostrarlo en la lateral
        try:
            resultado = query(
                "SELECT id_clase_actual, curso, feedback_visible, examen_activo FROM configuracion_clase WHERE id = 1"
            )

            if resultado:
                id_c, cur_c, feed_c, act_c = resultado[0]

                st.sidebar.subheader("📊 Estado de la Clase")
                st.sidebar.info(f"**Clase Activa:** № {id_c}\n\n**Curso:** {cur_c}")

                # Indicadores visuales rápidos
                status_exam = "🟢 ABIERTO" if act_c == 1 else "🔴 CERRADO"
                status_feed = "👁️ VISIBLE" if feed_c == 1 else "🚫 OCULTO"

                st.sidebar.write(f"**Examen:** {status_exam}")
                st.sidebar.write(f"**Feedback:** {status_feed}")
            else:
                st.sidebar.warning("⚠️ Sin configuración activa")

        except:
            st.sidebar.error("Error al cargar estado")

        st.sidebar.divider()
    
        # --- CUERPO PRINCIPAL: GESTIÓN DE CLASE ---
        st.title("Gestión Académica")
        
        with st.expander("⚙️ Configurar Clase y Curso Actual", expanded=True):
            # Usamos los mismos valores 'res' obtenidos arriba para los inputs
            clase_act_val = res[0] if res else 1
            curso_act_val = res[1] if res else "5TO A"
            feedback_val = res[2] if res else 0
            activo_val = res[3] if res else 0

            col_id, col_cur = st.columns(2)
            id_clase_input = col_id.number_input("ID de Clase a dictar:", min_value=1, value=clase_act_val)
            
            opciones_cursos = ["4TO A", "4TO C", "5TO A", "5TO C", "5TO A NATURALES"]
            idx = opciones_cursos.index(curso_act_val) if curso_act_val in opciones_cursos else 0
            curso_seleccionado = col_cur.selectbox("Curso que rinde hoy:", opciones_cursos, index=idx)
            
            st.divider()
            col_feed, col_status = st.columns(2)

            # Toggles dinámicos
            nuevo_feed = col_feed.toggle("Habilitar Ver Respuestas", value=(feedback_val == 1))
            nuevo_activo = col_status.toggle("Abrir Acceso al Examen", value=(activo_val == 1))

            if st.button("💾 GUARDAR Y APLICAR CAMBIOS", use_container_width=True):
                execute(
                    """
                    INSERT INTO configuracion_clase 
                    (id, id_clase_actual, curso, feedback_visible, examen_activo)
                    VALUES (1, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        id_clase_actual = excluded.id_clase_actual,
                        curso = excluded.curso,
                        feedback_visible = excluded.feedback_visible,
                        examen_activo = excluded.examen_activo
                    """,
                    (
                        id_clase_input,
                        curso_seleccionado,
                        1 if nuevo_feed else 0,
                        1 if nuevo_activo else 0
                    )
                )

                st.success("✅ ¡Configuración actualizada en todo el sistema!")
                st.rerun()
        
        # --- 3. CIERRE DE JORNADA (REEMPLAZO TOTAL) ---
        st.divider()
        st.subheader("🔒 Finalización de Clase")
        
        try:
            resultado = query(
                "SELECT id_clase_actual, curso FROM configuracion_clase WHERE id = 1"
            )

            config = resultado[0] if resultado else None
        
            if config and config[1]:
                clase_id_activa, curso_activo = config[0], config[1]
                
                # Información previa al botón
                st.info(f"Configuración actual: **Clase {clase_id_activa}** | Curso: **{curso_activo}**.")
                
                # Botón principal: Dispara la primera confirmación (el cartel)
                if st.button(f"🔴 EJECUTAR CIERRE DE JORNADA", use_container_width=True):
                    confirmar_cierre_dialog(clase_id_activa, curso_activo)
        
                # Lógica que se dispara SOLO si el usuario confirmó en el cartel emergente
                if st.session_state.get('ejecutar_cierre_real', False):
                    try:
                        # 1. Registrar la fecha real de hoy en la tabla clases
                        fecha_actual = datetime.date.today().strftime("%d/%m/%Y")

                        execute(
                            """
                            UPDATE clases SET fecha = ? WHERE id_clase = ?
                            """,
                            (fecha_actual, clase_id_activa)
                        )

                        # 2. Buscamos alumnos del curso
                        alumnos_del_curso = query(
                            "SELECT id_alumno, nombre FROM alumnos WHERE UPPER(curso) = UPPER(?)",
                            (curso_activo,)
                        )

                        contador_ausentes = 0
                        nombres_ausentes = []

                        for id_al, nombre_al in alumnos_del_curso:
                            # Verificamos si ya tiene nota registrada
                            resultado = query(
                                "SELECT COUNT(*) FROM reportes_diarios WHERE id_alumno = ? AND id_clase = ?",
                                (id_al, clase_id_activa)
                            )

                            if not resultado or resultado[0][0] == 0:
                                # REGLA 21/02: Grabamos el AUSENTE y el 1.0 reglamentario
                                execute(
                                    """
                                    INSERT INTO reportes_diarios 
                                    (id_alumno, id_clase, ejercicios_completados, ejercicios_correctos, nota_final, asistencia)
                                    VALUES (?, ?, 0, 0, 1.0, 'AUSENTE')
                                    """,
                                    (id_al, clase_id_activa)
                                )

                                contador_ausentes += 1
                                nombres_ausentes.append(nombre_al)

                        # 3. Cerramos el acceso al examen
                        execute(
                            "UPDATE configuracion_clase SET examen_activo = 0 WHERE id = 1"
                        )
                        
                        # Feedback visual final
                        st.success(f"✅ ¡Cierre exitoso! Clase registrada con fecha: {fecha_actual}")
                        st.balloons()
                        
                        if nombres_ausentes:
                            with st.expander(f"📍 {contador_ausentes} alumnos calificados con 1.0 (Ausentes)"):
                                for n in nombres_ausentes: st.write(f"• {n}")
                        
                        # Limpieza y reinicio
                        st.session_state.ejecutar_cierre_real = False
                        import time
                        time.sleep(3)
                        st.rerun()
        
                    except Exception as e:
                        st.error(f"❌ Error en el proceso de cierre: {e}")
                        st.session_state.ejecutar_cierre_real = False
            else:
                st.warning("⚠️ No hay un curso configurado para cerrar.")
        
        except Exception as e:
            st.error(f"❌ Error al conectar con la base de datos: {e}")
        
        # --- 4. SORTEADOR DE ALUMNOS (ORALES) ---
        st.divider()
        st.subheader("🎲 Sorteador para Orales")
        
        # Usamos el mismo curso_objetivo que ya definimos arriba desde la configuración
        with st.container(border=True):
            col_sort_info, col_sort_btn = st.columns([2, 1])
            
            with col_sort_info:
                st.write(f"Sorteo aleatorio entre los alumnos de **{curso_seleccionado}**")
            
            if col_sort_btn.button("🎰 SORTEAR ALUMNO", use_container_width=True):
                try:
                    # Buscamos a los alumnos del curso configurado actualmente
                    resultado = query(
                        "SELECT nombre FROM alumnos WHERE UPPER(curso) = UPPER(?)",
                        (curso_seleccionado,)
                    )

                    lista_alumnos = [fila[0] for fila in resultado] if resultado else []

                    if lista_alumnos:
                        st.session_state.ganador = random.choice(lista_alumnos)
                    else:
                        st.session_state.ganador = "No hay alumnos en este curso"

                except Exception as e:
                    st.error(f"Error en el sorteo: {e}")

            # Mostrar el resultado con estilo
            if 'ganador' in st.session_state:
                st.markdown(f"""
                    <div style="background-color: #2e3136; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; text-align: center;">
                        <h2 style="color: white; margin: 0;">🎯 Seleccionado:</h2>
                        <h1 style="color: #ff4b4b; margin: 10px 0;">{st.session_state.ganador}</h1>
                    </div>
                """, unsafe_allow_html=True)
                
        # --- 5. CARGA DE NOTA ORAL (SOBREESCRIBE NOTA FINAL) ---
        st.divider()
        st.subheader("📝 Calificación Oral / Definitiva")

        with st.container(border=True):
            nombre_por_defecto = st.session_state.ganador if ('ganador' in st.session_state and st.session_state.ganador != "No hay alumnos en este curso") else ""
            
            col_al, col_nota = st.columns([2, 1])
            
            with col_al:
                resultado = query(
                    "SELECT nombre FROM alumnos WHERE UPPER(TRIM(curso)) = UPPER(TRIM(?)) ORDER BY nombre ASC",
                    (curso_seleccionado,)
                )

                lista_nombres = [f[0] for f in resultado] if resultado else []

                alumno_a_calificar = st.selectbox(
                    "Seleccionar Alumno",
                    lista_nombres,
                    index=lista_nombres.index(nombre_por_defecto)
                    if nombre_por_defecto in lista_nombres
                    else 0
                )
            
            with col_nota:
                nota_input = st.number_input("Nota Final", min_value=1.0, max_value=10.0, value=7.0, step=0.5)

            if st.button("💾 GUARDAR NOTA ORAL", use_container_width=True):
                try:
                    # 1. Obtenemos el ID del alumno
                    resultado_id = query(
                        "SELECT id_alumno FROM alumnos WHERE nombre = ?",
                        (alumno_a_calificar,)
                    )

                    if resultado_id:
                        id_al = resultado_id[0][0]

                        # 2. Verificamos si ya existe el registro para esa clase
                        resultado_existe = query(
                            "SELECT COUNT(*) FROM reportes_diarios WHERE id_alumno = ? AND id_clase = ?",
                            (id_al, id_clase_input)
                        )

                        existe = resultado_existe[0][0] if resultado_existe else 0

                        if existe > 0:
                            execute(
                                """
                                UPDATE reportes_diarios 
                                SET nota_oral = ?, nota_final = ? 
                                WHERE id_alumno = ? AND id_clase = ?
                                """,
                                (nota_input, nota_input, id_al, id_clase_input)
                            )
                        else:
                            execute(
                                """
                                INSERT INTO reportes_diarios 
                                (id_alumno, id_clase, ejercicios_completados, ejercicios_correctos, nota_oral, nota_final)
                                VALUES (?, ?, 0, 0, ?, ?)
                                """,
                                (id_al, id_clase_input, nota_input, nota_input)
                            )

                        st.toast(f"✅ Nota {nota_input} guardada para {alumno_a_calificar}", icon="🔥")
                        st.success(f"Cambios registrados para {alumno_a_calificar}.")

                    else:
                        st.error("No se pudo encontrar el ID del alumno.")

                except Exception as e:
                    st.error(f"Error al guardar la nota: {e}")
                    
        # --- 6. JUSTIFICAR INASISTENCIA (Versión con Registro de Ausencia Permanente) ---
        st.divider()
        st.subheader("🏥 Justificar Inasistencia")
        
        with st.expander("Abrir panel de justificación"):
            st.info("Esta acción mantendrá el registro de 'AUSENTE' pero eliminará la nota 1.0 para que el alumno pueda rendir.")
            
            busqueda = st.text_input("Buscar alumno por nombre o apellido:", key="input_justificar")
            resultados = []
            
            if busqueda:
                try:
                    resultados = query(
                        "SELECT id_alumno, nombre, curso FROM alumnos WHERE nombre LIKE ?",
                        (f"%{busqueda}%",)
                    )

                except Exception as e:
                    st.error(f"Error en la búsqueda: {e}")

            if resultados:
                opciones_alumnos = {f"{r[1]} ({r[2]})": r[0] for r in resultados}
                seleccion = st.selectbox("Seleccioná el alumno correcto:", opciones_alumnos.keys())
                id_al_elegido = opciones_alumnos[seleccion]
                
                # Asumimos que id_clase_input viene de la configuración de arriba
                id_clase_justificar = st.number_input("ID de Clase a justificar:", value=id_clase_input, key="nro_clase_just")
                
                if st.button("⚠️ JUSTIFICAR Y LIMPIAR NOTAS", use_container_width=True):
                    try:
                        # UPDATE en lugar de DELETE
                        # Seteamos notas y ejercicios en NULL para que el sistema lo vea como "no rendido"
                        # pero NO tocamos la columna 'asistencia' (que seguirá siendo 'AUSENTE')
                        execute(
                            """
                            UPDATE reportes_diarios 
                            SET ejercicios_completados = NULL, 
                                ejercicios_correctos = NULL, 
                                nota_final = NULL 
                            WHERE id_alumno = ? AND id_clase = ?
                            """,
                            (id_al_elegido, id_clase_justificar)
                        )

                        st.session_state.msg_justificar = f"✅ Inasistencia justificada para {seleccion}. Registro histórico mantenido."
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error al justificar: {e}")
            elif busqueda:
                st.warning("No se encontraron coincidencias.")

        if 'msg_justificar' in st.session_state:
            st.success(st.session_state.msg_justificar)
            del st.session_state.msg_justificar
        
        # --- 7. MONITOR EN TIEMPO REAL (LECTURA DIRECTA DE DB) ---
        st.divider()
        st.subheader(f"📈 Reportes en DB: {curso_seleccionado} - Clase № {id_clase_input}")

        try:
            # Consulta adaptada a Turso
            query_monitor = """
                SELECT 
                    a.nombre AS Alumno, 
                    r.asistencia AS Asistencia,
                    r.ejercicios_completados AS Hechos, 
                    r.ejercicios_correctos AS Correctos, 
                    r.nota_oral AS Nota_Oral,
                    r.nota_final AS Nota_Final
                FROM reportes_diarios r
                INNER JOIN alumnos a ON r.id_alumno = a.id_alumno
                WHERE r.id_clase = ? 
                AND UPPER(TRIM(a.curso)) = UPPER(TRIM(?))
                ORDER BY a.nombre ASC
            """

            resultados = query(query_monitor, (id_clase_input, curso_seleccionado))

            if resultados:
                columnas = [
                    "Alumno",
                    "Asistencia",
                    "Hechos",
                    "Correctos",
                    "Nota Oral",
                    "Nota Final"
                ]

                df_mon = pd.DataFrame(resultados, columns=columnas)

                # --- FUNCIÓN DE ESTILO PARA RESALTAR AUSENCIAS ---
                def resaltar_ausencia(val):
                    color = '#FF4B4B' if val == 'AUSENTE' else '#28a745'
                    return f'color: {color}; font-weight: bold'

                df_estilado = df_mon.style.applymap(resaltar_ausencia, subset=['Asistencia'])

                st.dataframe(df_estilado, use_container_width=True, hide_index=True)
                st.caption(f"✅ Mostrando {len(df_mon)} registros encontrados en la tabla reportes_diarios.")

            else:
                st.info(
                    f"Empty Set: No hay registros grabados en la base de datos para el curso {curso_seleccionado} en la clase {id_clase_input}."
                )

        except Exception as e:
            st.error(f"Error al consultar la base de datos: {e}")

        # --- 8. REPORTE TRIMESTRAL (Cálculo de Tendencias y Notas) ---
        st.divider()
        st.subheader("📊 Generador de Notas Trimestrales")

        with st.expander("Calcular Acta del Trimestre", expanded=False):
            trimestre_n = st.selectbox("Seleccione el Trimestre:", ["1", "2", "3"], key="trim_sel")
            
            if st.button("🚀 GENERAR REPORTE", use_container_width=True):
                try:
                    import numpy as np
                    import pandas as pd

                    # 1️⃣ Traer alumnos del curso activo
                    alumnos = query(
                        "SELECT id_alumno, nombre FROM alumnos WHERE UPPER(curso) = UPPER(?)",
                        (curso_seleccionado,)
                    )

                    if not alumnos:
                        st.warning("No hay alumnos en este curso.")
                    else:
                        datos_reporte = []

                        for id_al, nombre_al in alumnos:

                            # 2️⃣ Traer historial del trimestre
                            query_hist = """
                                SELECT 
                                    r.ejercicios_completados as esfuerzo, 
                                    r.ejercicios_correctos as eficacia, 
                                    r.nota_final 
                                FROM reportes_diarios r
                                JOIN clases c ON r.id_clase = c.id_clase
                                WHERE r.id_alumno = ? 
                                AND c.trimestre = ? 
                                AND r.nota_final IS NOT NULL
                                ORDER BY r.id_clase ASC
                            """

                            registros = query(query_hist, (id_al, int(trimestre_n)))

                            if not registros:
                                prom_base, adj_esf, adj_efi, nota_f = "---", "---", "---", "---"
                            else:
                                df_hist = pd.DataFrame(registros, columns=["esfuerzo", "eficacia", "nota_final"])

                                p = df_hist["nota_final"].mean()

                                if len(df_hist) >= 2:
                                    x = np.arange(len(df_hist))
                                    m_esf, _ = np.polyfit(x, df_hist["esfuerzo"], 1)
                                    m_efi, _ = np.polyfit(x, df_hist["eficacia"], 1)

                                    # Ajuste Esfuerzo
                                    if m_esf > 0.1:
                                        aesf = "+0.5"
                                    elif m_esf < -0.1:
                                        aesf = "-0.5"
                                    else:
                                        aesf = "0"

                                    # Ajuste Eficacia
                                    if m_efi > 0.1:
                                        aefi = "+0.5"
                                    elif m_efi < -0.1:
                                        aefi = "-0.5"
                                    else:
                                        aefi = "0"

                                    v_esf = 0.5 if aesf == "+0.5" else (-0.5 if aesf == "-0.5" else 0)
                                    v_efi = 0.5 if aefi == "+0.5" else (-0.5 if aefi == "-0.5" else 0)

                                    nota_final_calc = int(round(p + v_esf + v_efi))
                                else:
                                    aesf, aefi = "0", "0"
                                    nota_final_calc = int(round(p))

                                prom_base = f"{p:.2f}"
                                adj_esf = aesf
                                adj_efi = aefi
                                nota_f = max(1, min(10, nota_final_calc))

                            datos_reporte.append({
                                "Estudiante": nombre_al,
                                "Prom. Base": prom_base,
                                "Adj. Esf.": adj_esf,
                                "Adj. Efi.": adj_efi,
                                "Nota Final": nota_f
                            })

                        # 3️⃣ Mostrar Resultados
                        df_final = pd.DataFrame(datos_reporte)

                        st.write(f"### 📋 Acta de Calificaciones - {curso_seleccionado} (T{trimestre_n})")
                        st.dataframe(df_final, use_container_width=True, hide_index=True)

                        st.caption(
                            "📌 El ajuste de +/- 0.5 se aplica automáticamente por tendencia "
                            "(mejora o descenso) en el desempeño."
                        )

                except Exception as e:
                    st.error(f"Error al generar el reporte: {e}")
                    
        # --- 10. CREADOR DE EXÁMENES (Versión AUTOINCREMENT) ---
        st.divider()
        st.subheader("🍎 Creador de Exámenes")

        with st.expander("Configurar Nueva Clase/Examen", expanded=False):
            # 1. Datos Maestros (Sin pedir ID, SQLite lo hace solo)
            col_tri, col_preg = st.columns(2)
            trimestre_new = col_tri.selectbox("📅 Trimestre:", ["1", "2", "3"], key="tri_new_auto")
            cant_preguntas = col_preg.number_input("❓ Cantidad de preguntas:", min_value=1, max_value=50, value=5, step=1)
            
            tema_new = st.text_input("📚 Tema de la clase:", placeholder="Ej: Fracciones, Revolución de Mayo...")

            # 2. Formulario dinámico de preguntas
            # Nota: Aquí no guardamos el id_clase todavía porque no lo conocemos hasta insertar la clase
            preguntas_lista = []
            
            with st.form("form_preguntas_auto"):
                st.write("### 📝 Detalle de Preguntas")
                
                for i in range(1, cant_preguntas + 1):
                    st.markdown(f"**Pregunta {i}**")
                    enunciado = st.text_input(f"Enunciado {i}:", key=f"enun_auto_{i}")
                    
                    c1, c2 = st.columns(2)
                    op_a = c1.text_input(f"A:", key=f"a_auto_{i}")
                    op_b = c2.text_input(f"B:", key=f"b_auto_{i}")
                    op_c = c1.text_input(f"C:", key=f"c_auto_{i}")
                    op_d = c2.text_input(f"D (NDA):", value="Ninguna de las opciones de la presente lista", key=f"d_auto_{i}")
                    
                    correcta = st.selectbox(f"✅ Correcta {i}:", ["A", "B", "C", "D"], key=f"corr_auto_{i}")
                    st.divider()
                    
                    # Guardamos los datos de la pregunta (sin el id_clase por ahora)
                    preguntas_lista.append((enunciado, op_a, op_b, op_c, op_d, correcta))

                submit_examen = st.form_submit_button("✨ GUARDAR EXAMEN COMPLETO", use_container_width=True)

            if submit_examen:
                if not tema_new:
                    st.error("Por favor, ingresa un tema para la clase.")
                else:
                    try:
                        # PASO A: Insertar la clase
                        execute("""
                            INSERT INTO clases (fecha, tema, ejercicios_totales, trimestre) 
                            VALUES (?, ?, ?, ?)
                        """, ("", tema_new, cant_preguntas, int(trimestre_new)))

                        # PASO B: Obtener el ID recién generado
                        id_clase_generado = execute("""
                            INSERT INTO clases (fecha, tema, ejercicios_totales, trimestre) 
                            VALUES (?, ?, ?, ?)
                        """, ("", tema_new, cant_preguntas, int(trimestre_new)))

                        # PASO C: Preparar preguntas con el ID obtenido
                        preguntas_finales = []
                        for p in preguntas_lista:
                            preguntas_finales.append((id_clase_generado, *p))

                        # PASO D: Insertar preguntas vinculadas
                        for pregunta in preguntas_finales:
                            execute("""
                                INSERT INTO preguntas 
                                (id_clase, enunciado, opc_a, opc_b, opc_c, opc_d, correcta)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, pregunta)

                        st.balloons()
                        st.success(
                            f"✅ ¡Éxito! Se ha creado la Clase N° {id_clase_generado} sobre '{tema_new}'."
                        )
                    except Exception as e:
                        st.error(f"❌ ERROR: {e}")
                        
        # --- 11. VISUALIZADOR DE CLASES Y PREGUNTAS ---
        st.divider()
        st.subheader("📂 Explorador de Clases y Exámenes")

        try:
            # 1️⃣ Traer todas las clases registradas
            clases = query("SELECT * FROM clases ORDER BY id_clase DESC")

            if not clases:
                st.info("Aún no hay clases registradas en la base de datos.")
            else:
                df_clases = pd.DataFrame(
                    clases,
                    columns=["id_clase", "fecha", "tema", "ejercicios_totales", "trimestre"]
                )

                st.write("### 1. Seleccione una Clase")
                st.dataframe(df_clases, use_container_width=True, hide_index=True)

                # Crear diccionario para selectbox
                opciones_clases = {
                    f"ID: {row.id_clase} - {row.tema} ({row.fecha})": row.id_clase
                    for _, row in df_clases.iterrows()
                }

                clase_a_ver = st.selectbox(
                    "🔍 Seleccione una clase para ver sus preguntas:",
                    options=opciones_clases.keys(),
                    index=None,
                    placeholder="Elija una clase..."
                )

                if clase_a_ver:
                    id_seleccionado = opciones_clases[clase_a_ver]

                    # 2️⃣ Traer preguntas de la clase seleccionada
                    preguntas = query("""
                        SELECT enunciado, opc_a, opc_b, opc_c, opc_d, correcta
                        FROM preguntas
                        WHERE id_clase = ?
                    """, (id_seleccionado,))

                    if not preguntas:
                        st.warning("Esta clase no tiene preguntas vinculadas.")
                    else:
                        df_preguntas = pd.DataFrame(
                            preguntas,
                            columns=["enunciado", "opc_a", "opc_b", "opc_c", "opc_d", "correcta"]
                        )

                        st.write(f"### 📝 Preguntas de la Clase ID: {id_seleccionado}")

                        for i, row in df_preguntas.iterrows():
                            with st.container(border=True):
                                st.markdown(f"**Pregunta {i+1}: {row['enunciado']}**")

                                c1, c2 = st.columns(2)
                                c1.write(f"**A:** {row['opc_a']}")
                                c2.write(f"**B:** {row['opc_b']}")
                                c1.write(f"**C:** {row['opc_c']}")
                                c2.write(f"**D:** {row['opc_d']}")

                                st.success(f"✅ Respuesta Correcta: **{row['correcta']}**")
        except Exception as e:
            st.error(f"Error al leer la base de datos: {e}")
            
        # --- 12. CIERRE DE SESIÓN (UN SOLO BOTÓN) ---
        st.sidebar.divider()
        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.session_state["logout_confirmado"] = True
            st.rerun()








