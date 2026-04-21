import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import random
from config import conectar
from clases import Alumno
from funciones import login_alumno, obtener_clase_activa
import os
import json



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#CON ESTA FUNCIÓN MIGRÉ LOS DATOS DEL ARCHIVO "TRANSITORIO" QUE LO VOY A DEJAR SOLAMENTE PARA QUE SEPA CÓMO LO HICE, LO MISMO QUE ESTA FUNCIÓN (tanto el archivo como esta función en realidad deberían ser borrados después de que se cumplió ese traspaso a Turso)
#from migrar_a_turso import migrar
#if st.button("🚀 INICIAR MIGRACIÓN A TURSO AHORA"):
#    migrar()
#    st.success("¡Datos migrados!")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
        
       /* --- FIX PARA EL ANCHO TOTAL EN COMPUTADORA --- */
        .main .block-container {
            padding-top: 1rem !important;
            max-width: 95% !important; /* <--- ESTO ELIMINA LO ANGOSTO */
            margin-left: auto;
            margin-right: auto;
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

        /* --- TARJETAS GLASSMORPHISM REFORZADAS --- */
        div[data-testid="stForm"], div.stCard, .stExpander {
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(12px);
            
            /* Ajustamos el padding: 1.5rem arriba/abajo y 2rem a los costados */
            padding: 1.5rem 2rem !important; 
            
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            
            /* FORZAMOS EL ANCHO INTERNO */
            width: 100% !important; 
            min-width: 100% !important;
            box-sizing: border-box !important;
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
            font-size: 11px;
            border-top: 1px solid #1B263B;
            z-index: 999;
        }
        </style>
    """, unsafe_allow_html=True)

    # LEYENDAS
    st.markdown('<p style="color: #00E5FF; font-size: 13px; text-align: right; font-style: italic; font-weight: bold;">ASTRA: Misión Educativa v1.0</p>', unsafe_allow_html=True)
    st.markdown("""<div class="footer">© 2026 -<b>Astra</b> | Prof. Juan Manuel Borrego<br><b>Ciencia de Datos & Matemática</b></div>""", unsafe_allow_html=True)

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
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("SELECT id_alumno, nombre, curso FROM alumnos WHERE nombre = ?", (nombre_ingresado,))
                res = cursor.fetchone()
                conn.close()
                
                if res:
                    # res[0]=id, res[1]=nombre, res[2]=curso
                    st.session_state.estudiante = Alumno(res[0], res[1], res[2])
                    
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

        # --- RANKING DINÁMICO (VERSIÓN FINAL SIN ERRORES DE COLUMNA) ---
        try:
            with conectar() as conn:
                # 1. Identificamos las últimas 3 clases donde alumnos DE ESTE CURSO tuvieron actividad
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT r.id_clase 
                    FROM reportes_diarios r
                    JOIN alumnos a ON r.id_alumno = a.id_alumno
                    WHERE a.curso = ?
                    ORDER BY r.id_clase DESC LIMIT 3
                """, (st.session_state.estudiante.curso,))
                
                filas = cursor.fetchall()
                ids_activas = [f[0] for f in filas]

                if ids_activas:
                    placeholders = ', '.join(['?'] * len(ids_activas))
                    
                    # 2. Query de Ranking Blindada: Fuerza el 1.0 si no hay reporte
                    query_ranking = f"""
                        SELECT a.nombre, 
                        AVG(
                            COALESCE(
                                CASE 
                                    WHEN r.ejercicios_completados = 0 THEN 1.0 
                                    ELSE ((CAST(r.ejercicios_completados AS REAL) / NULLIF(c.ejercicios_totales, 0)) + 
                                         (CAST(r.ejercicios_correctos AS REAL) / NULLIF(r.ejercicios_completados, 0))) / 2 * 10 
                                END, 
                                1.0 -- Si el reporte no existe (NULL), promedia un 1.0
                            )
                        ) as promedio
                        FROM alumnos a
                        CROSS JOIN (SELECT id_clase, ejercicios_totales FROM clases WHERE id_clase IN ({placeholders})) c
                        LEFT JOIN reportes_diarios r ON a.id_alumno = r.id_alumno AND c.id_clase = r.id_clase
                        WHERE a.curso = ?
                        GROUP BY a.id_alumno
                        ORDER BY promedio DESC
                    """
                    
                    # Los parámetros: primero los IDs de las clases, luego el curso para el WHERE final
                    params = ids_activas + [st.session_state.estudiante.curso]
                    df_ranking = pd.read_sql_query(query_ranking, conn, params=params)
                    
                    if not df_ranking.empty:
                        # --- MÉTODO OLÍMPICO (Salta puestos si hay empate) ---
                        df_ranking['puesto'] = df_ranking['promedio'].rank(method='min', ascending=False).astype(int)
                        
                        st.subheader("🏆 Cuadro de Honor")
                        st.caption(f"📊 Promedio de los últimos {len(ids_activas)} exámenes (Inasistencia = 1.0).")

                        with st.container(border=True):
                            c_lista, c_yo = st.columns([1.5, 1])
                            
                            with c_lista:
                                medallas = {1: "🥇", 2: "🥈", 3: "🥉", 4: "🏅", 5: "🏅"}
                                
                                # Mostramos a todos los que estén dentro del "Top 5" de posiciones
                                # Si hay 6 personas en el puesto 1, se verán las 6.
                                df_top = df_ranking[df_ranking['puesto'] <= 5]
                                
                                for _, row in df_top.iterrows():
                                    p = row['puesto']
                                    emoji = medallas.get(p, "👤")
                                    es_usuario = " (Vos)" if row['nombre'] == st.session_state.estudiante.nombre else ""
                                    
                                    # Formateamos el promedio a un solo decimal (ej: 9.5)
                                    promedio_formateado = f"{row['promedio']:.2f}"
                                    
                                    # Formato: Negrita para el podio 1, 2 y 3
                                    nombre_fmt = f"**{row['nombre']}**" if p <= 3 else row['nombre']
                                    
                                    # Imprimimos: Emoji Puesto Nombre (Vos) `Promedio`
                                    st.markdown(f"{emoji} {p}° {nombre_fmt}{es_usuario} ` {promedio_formateado} `")
                                    
                            with c_yo:
                                # --- POSICIÓN PERSONAL ---
                                yo = df_ranking[df_ranking['nombre'] == st.session_state.estudiante.nombre]
                                if not yo.empty:
                                    p_actual = int(yo.iloc[0]['puesto'])
                                    prom_actual = float(yo.iloc[0]['promedio']) # Obtenemos el promedio personal
                                    
                                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                                    st.write("🎯 **Tu Posición**")
                                    
                                    if p_actual == 1:
                                        st.subheader(f"👑 #{p_actual}")
                                        st.success("Orgullo: ¡sos el líder del curso!")
                                    elif p_actual <= 5:
                                        st.subheader(f"✨ #{p_actual}")
                                        st.success("Orgullo: ¡estás en el Cuadro de Honor del Curso!")
                                    elif p_actual <= 10:
                                        st.subheader(f"⚡ #{p_actual}")
                                        st.info("Estás en el TOP 10: ¡a un paso de integrar el Cuadro de Honor!")
                                    else:
                                        st.subheader(f"🚀 #{p_actual}")
                                        st.warning("¡A seguir sumando para entrar al TOP 10!")

                                    # Agregamos el promedio personal bien visible debajo del estado
                                    st.write(f"Tu promedio: **{prom_actual:.2f}**")
                                    
                                    st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("📉 No hay datos suficientes para el ranking.")
                else:
                    st.info("📉 El ranking aparecerá cuando se registren las primeras notas.")
                    
        except Exception as e:
            st.error(f"Error técnico en el ranking: {e}")

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
                st.success("✨ ¡Estado: APROBANDO EL AÑO! ¡A SEGUIR ASÍ ESTE TRAMO FINAL!")
            else:
                faltan = 18 - puntos_totales
                if faltan > 0:
                    st.warning(f"Necesitás {faltan} puntos más para aprobar el año.")
                else:
                    st.info("Promedio alcanzado, pero recordá que para aprobar el año el 3er trimestre debe ser mayor o igual a 6.")

        st.divider()
        # --- BOTONES DE ACCIÓN ---
        st.subheader("🎮 Acciones Disponibles")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            # --- 1. VALIDACIÓN: ¿YA EXISTE NOTA EN DB? ---
            ya_rindio = False
            if st.session_state.id_clase_hoy:
                try:
                    with conectar() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT COUNT(*) FROM reportes_diarios 
                            WHERE id_alumno = ? AND id_clase = ?
                        """, (st.session_state.estudiante.id, st.session_state.id_clase_hoy))
                        if cursor.fetchone()[0] > 0:
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
                        conn = conectar()
                        df_preguntas = pd.read_sql_query(
                            "SELECT id_pregunta, enunciado, opc_a, opc_b, opc_c, opc_d, correcta FROM preguntas WHERE id_clase = ?", 
                            conn, params=(st.session_state.id_clase_hoy,)
                        )
                        conn.close()
                    
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

                                # --- NUEVO: GUARDAR ÚLTIMO EXAMEN EN JSON ---
                                try:
                                    # Convertimos el diccionario a una cadena de texto (JSON)
                                    respuestas_json = json.dumps(st.session_state.respuestas_temporales)
                                    
                                    with conectar() as conn:
                                        cursor = conn.cursor()
                                        # INSERT OR REPLACE asegura que solo haya UNA fila por alumno
                                        cursor.execute("""
                                            INSERT OR REPLACE INTO ultimo_examen_alumno (id_alumno, id_clase, respuestas_json)
                                            VALUES (?, ?, ?)
                                        """, (st.session_state.estudiante.id, st.session_state.id_clase_hoy, respuestas_json))
                                        conn.commit()
                                except Exception as e:
                                    # Lo ponemos en un log o warning por si falla, pero que no trabe la entrega
                                    print(f"Error guardando JSON: {e}")
                    
                                # --- EFECTOS NATIVOS ---
                                st.balloons() 
                                st.success(f'✅ ¡Entregado! Vas a poder ver tu nota seleccionando "📚 REPASAR CLASES" apenas el profesor lo habilite')
                                
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
                
                # --- 1. LÓGICA DE REVISIÓN DETALLADA (MODO LISTA CON BOTÓN) ---
                try:
                    with conectar() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT feedback_visible FROM configuracion_clase WHERE id = 1")
                        res_f = cursor.fetchone()
                        feedback_ok = res_f[0] == 1 if res_f else False
                        
                        cursor.execute("SELECT id_clase, respuestas_json FROM ultimo_examen_alumno WHERE id_alumno = ?", 
                                       (st.session_state.estudiante.id,))
                        datos_memoria = cursor.fetchone()
                
                    if datos_memoria and feedback_ok:
                        id_clase_guardada, json_respuestas = datos_memoria
                        st.info(f"💡 Revisión detallada disponible (Clase ID: {id_clase_guardada})")
                        
                        # Inicializamos la variable de estado si no existe
                        if 'ver_revision' not in st.session_state:
                            st.session_state.ver_revision = False
                
                        # Botón para activar la vista
                        if st.button("🔎 MIRÁ TU ÚLTIMO EXAMEN CORREGIDO", use_container_width=True):
                            st.session_state.ver_revision = True
                
                        # Si el estado es True, mostramos la lista completa
                        if st.session_state.ver_revision:
                            with conectar() as conn:
                                df_p = pd.read_sql_query(
                                    "SELECT id_pregunta, enunciado, correcta, opc_a, opc_b, opc_c, opc_d FROM preguntas WHERE id_clase = ?", 
                                    conn, params=(id_clase_guardada,)
                                )
                            
                            respuestas_alumno = json.loads(json_respuestas)
                            
                            with st.expander("📝 Detalle de tu examen", expanded=True):
                                for i, (_, p) in enumerate(df_p.iterrows(), 1):
                                    st.markdown(f"#### 🚩 PREGUNTA {i}")
                                    st.info(f"**{p['enunciado']}**")
                                    
                                    id_preg = str(p['id_pregunta'])
                                    rta_alumno = respuestas_alumno.get(id_preg, 'N')
                                    rta_correcta = str(p['correcta']).strip().upper()
                                    
                                    opciones_db = {'A': p['opc_a'], 'B': p['opc_b'], 'C': p['opc_c'], 'D': p['opc_d']}
                                    
                                    for letra, texto_opcion in opciones_db.items():
                                        if texto_opcion:
                                            if letra == rta_alumno and letra == rta_correcta:
                                                st.success(f"🟢 **{letra}) {texto_opcion}** (Tu respuesta)")
                                            elif letra == rta_alumno and letra != rta_correcta:
                                                st.error(f"🔴 **{letra}) {texto_opcion}** (Tu respuesta)")
                                            elif letra == rta_correcta:
                                                st.warning(f"✅ **{letra}) {texto_opcion}** (Correcta)")
                                            else:
                                                st.write(f"⚪ {letra}) {texto_opcion}")
                                    
                                    if rta_alumno == 'N':
                                        st.caption("⚠️ *No seleccionaste ninguna respuesta.*")
                                    
                                    st.divider()
                                
                                # Botón opcional para volver a ocultar la lista
                                if st.button("Ocultar revisión"):
                                    st.session_state.ver_revision = False
                                    st.rerun()
                
                    elif not feedback_ok and datos_memoria:
                        st.caption("🔒 La revisión detallada no está habilitada por el profesor.")
                    else:
                        st.caption("ℹ️ No hay un examen reciente para revisar.")
                
                except Exception as e:
                    st.error(f"Error al cargar revisión: {e}")                
                           
                # --- 2. TU HISTORIAL GENERAL (TABLA REPORTES_DIARIOS) ---
                st.markdown("---")
                st.subheader("📖 Tu Historial de Aprendizaje")
                
                try:
                    # --- VALIDACIÓN REAL CONTRA LA CONFIGURACIÓN DEL PROFESOR ---
                    with conectar() as conn_check:
                        cursor_check = conn_check.cursor()
                        # Consultamos la tabla de configuración que usa el profesor
                        cursor_check.execute("SELECT feedback_visible FROM configuracion_clase WHERE id = 1")
                        res_check = cursor_check.fetchone()
                        # Si es 1 está habilitado, si es 0 (o no existe) está bloqueado
                        feedback_habilitado = (res_check[0] == 1) if res_check else False        
                    if not feedback_habilitado:
                        st.warning("🔒 El profesor ha desactivado la visualización de resultados momentáneamente.")
                    else:
                        # Si está habilitado (o no hay clase hoy bloqueando), mostramos todo el código que ya tenías
                        conn = conectar()
                        id_actual = st.session_state.estudiante.id                    
                        # 1. Definimos la Query con la Opción B y el redondeo
                        query = """
                            SELECT
                                c.id_clase as 'ID Clase',
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
                            ORDER BY c.id_clase DESC
                        """
                        df_repaso = pd.read_sql_query(query, conn, params=(id_actual,))
                        conn.close()
    
                        # 2. Procesamos y mostramos la tabla
                        if not df_repaso.empty:
                            # Forzamos los enteros para que no aparezca el .0
                            cols_int = ['Ejercicios del día', 'Total resueltos', 'Total correctos']
                            for col in cols_int:
                                df_repaso[col] = pd.to_numeric(df_repaso[col], errors='coerce').fillna(0).astype(int)
    
                            st.dataframe(
                                df_repaso.style.map(
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
                if clave == st.secrets["PASSWORD_DOCENTE"]: # Tu clave actual
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
            with conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_clase_actual, curso, feedback_visible, examen_activo FROM configuracion_clase WHERE id = 1")
                res = cursor.fetchone()
                
                if res:
                    id_c, cur_c, feed_c, act_c = res
                    
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
        
        # --- REFRESCO DE DATOS DESDE TURSO ---
        try:
            conn = conectar() 
            # Con libsql.connect, ejecutamos directamente
            res_query = conn.execute("SELECT id_clase_actual, curso, feedback_visible, examen_activo FROM configuracion_clase WHERE id = 1")
            fila = res_query.fetchone()
            
            if fila:
                res = fila
            else:
                # Si la tabla está vacía, creamos la configuración inicial
                conn.execute("INSERT INTO configuracion_clase (id, id_clase_actual, curso, feedback_visible, examen_activo) VALUES (1, 1, '5TO A', 0, 0)")
                res = [1, "5TO A", 0, 0]
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            res = [1, "5TO A", 0, 0] # Valores de respaldo para evitar el AttributeError
            
        # --- CUERPO DEL EXPANDER ---
        with st.expander("⚙️ Configurar Clase y Curso Actual", expanded=True):
            # Usamos los valores obtenidos de la consulta de arriba
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
        
            # Actualizado use_container_width por width='stretch' según sugerencia de Streamlit
            if st.button("💾 GUARDAR Y APLICAR CAMBIOS", width='stretch'):
                with conectar() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO configuracion_clase (id, id_clase_actual, curso, feedback_visible, examen_activo) 
                        VALUES (1, ?, ?, ?, ?)
                    """, (id_clase_input, curso_seleccionado, 1 if nuevo_feed else 0, 1 if nuevo_activo else 0))
                    conn.commit() # Aseguramos el guardado en la nube
                st.success("✅ ¡Configuración actualizada en todo el sistema!")
                st.rerun()
        
        # --- 3. CIERRE DE JORNADA (REEMPLAZO TOTAL) ---
        st.divider()
        st.subheader("🔒 Finalización de Clase")
        
        try:
            with conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_clase_actual, curso FROM configuracion_clase WHERE id = 1")
                config = cursor.fetchone()
        
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
                        with conectar() as conn:
                            cursor = conn.cursor()
                            
                            # 1. Registrar la fecha real de hoy en la tabla clases
                            fecha_actual = datetime.date.today().strftime("%d/%m/%Y")
                            cursor.execute("""
                                UPDATE clases SET fecha = ? WHERE id_clase = ?
                            """, (fecha_actual, clase_id_activa))
                            
                            # 2. Buscamos alumnos del curso
                            cursor.execute("SELECT id_alumno, nombre FROM alumnos WHERE UPPER(curso) = UPPER(?)", (curso_activo,))
                            alumnos_del_curso = cursor.fetchall()
                            
                            contador_ausentes = 0
                            nombres_ausentes = []
        
                            for id_al, nombre_al in alumnos_del_curso:
                                # Verificamos si ya tiene nota registrada (ya sea por examen o nota oral)
                                cursor.execute("SELECT COUNT(*) FROM reportes_diarios WHERE id_alumno = ? AND id_clase = ?", 
                                               (id_al, clase_id_activa))
                                
                                if cursor.fetchone()[0] == 0:
                                    # REGLA 21/02: Grabamos el AUSENTE y el 1.0 reglamentario
                                    cursor.execute("""
                                        INSERT INTO reportes_diarios 
                                        (id_alumno, id_clase, ejercicios_completados, ejercicios_correctos, nota_final, asistencia)
                                        VALUES (?, ?, 0, 0, 1.0, 'AUSENTE')
                                    """, (id_al, clase_id_activa))
                                    contador_ausentes += 1
                                    nombres_ausentes.append(nombre_al)
                            
                            # 3. Cerramos el acceso al examen
                            cursor.execute("UPDATE configuracion_clase SET examen_activo = 0 WHERE id = 1")
                            
                            conn.commit()
                        
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
                    with conectar() as conn:
                        cursor = conn.cursor()
                        # Buscamos a los alumnos del curso configurado actualmente
                        cursor.execute("SELECT nombre FROM alumnos WHERE UPPER(curso) = UPPER(?)", (curso_seleccionado,))
                        lista_alumnos = [fila[0] for fila in cursor.fetchall()]
                        
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
                with conectar() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT nombre FROM alumnos WHERE UPPER(TRIM(curso)) = UPPER(TRIM(?)) ORDER BY nombre ASC", (curso_seleccionado,))
                    lista_nombres = [f[0] for f in cursor.fetchall()]
                
                alumno_a_calificar = st.selectbox("Seleccionar Alumno", lista_nombres, 
                    index=lista_nombres.index(nombre_por_defecto) if nombre_por_defecto in lista_nombres else 0)
            
            with col_nota:
                nota_input = st.number_input("Nota Final", min_value=1.0, max_value=10.0, value=7.0, step=0.5)

            if st.button("💾 GUARDAR NOTA ORAL", use_container_width=True):
                try:
                    with conectar() as conn:
                        cursor = conn.cursor()
                        
                        # 1. Obtenemos el ID del alumno
                        cursor.execute("SELECT id_alumno FROM alumnos WHERE nombre = ?", (alumno_a_calificar,))
                        res_id = cursor.fetchone()
                        
                        if res_id:
                            id_al = res_id[0]
                            # 2. Verificamos si ya existe el registro para esa clase
                            cursor.execute("SELECT COUNT(*) FROM reportes_diarios WHERE id_alumno = ? AND id_clase = ?", (id_al, id_clase_input))
                            existe = cursor.fetchone()[0]
                            
                            if existe > 0:
                                cursor.execute("""
                                    UPDATE reportes_diarios 
                                    SET nota_oral = ?, nota_final = ? 
                                    WHERE id_alumno = ? AND id_clase = ?
                                """, (nota_input, nota_input, id_al, id_clase_input))
                            else:
                                cursor.execute("""
                                    INSERT INTO reportes_diarios 
                                    (id_alumno, id_clase, ejercicios_completados, ejercicios_correctos, nota_oral, nota_final)
                                    VALUES (?, ?, 0, 0, ?, ?)
                                """, (id_al, id_clase_input, nota_input, nota_input))
                            
                            conn.commit()
                            
                            # --- MEJORA: Mensaje que sí se ve ---
                            st.toast(f"✅ Nota {nota_input} guardada para {alumno_a_calificar}", icon="🔥")
                            st.success(f"Cambios registrados para {alumno_a_calificar}.")
                            
                            # Usamos un pequeño delay o simplemente no refrescamos para ver el success
                            # st.rerun() # Si lo quitas, el cartel de success se queda fijo.
                        else:
                            st.error("No se pudo encontrar el ID del alumno.")
                except Exception as e:
                    st.error(f"Error al guardar nota: {e}")
                    
        # --- 6. JUSTIFICAR INASISTENCIA (Versión con Registro de Ausencia Permanente) ---
        st.divider()
        st.subheader("🏥 Justificar Inasistencia")
        
        with st.expander("Abrir panel de justificación"):
            st.info("Esta acción mantendrá el registro de 'AUSENTE' pero eliminará la nota 1.0 para que el alumno pueda rendir.")
            
            busqueda = st.text_input("Buscar alumno por nombre o apellido:", key="input_justificar")
            resultados = []
            
            if busqueda:
                try:
                    with conectar() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT id_alumno, nombre, curso FROM alumnos WHERE nombre LIKE ?", (f"%{busqueda}%",))
                        resultados = cursor.fetchall()
                except Exception as e:
                    st.error(f"Error de búsqueda: {e}")

            if resultados:
                opciones_alumnos = {f"{r[1]} ({r[2]})": r[0] for r in resultados}
                seleccion = st.selectbox("Seleccioná el alumno correcto:", opciones_alumnos.keys())
                id_al_elegido = opciones_alumnos[seleccion]
                
                # Asumimos que id_clase_input viene de la configuración de arriba
                id_clase_justificar = st.number_input("ID de Clase a justificar:", value=id_clase_input, key="nro_clase_just")
                
                if st.button("⚠️ JUSTIFICAR Y LIMPIAR NOTAS", use_container_width=True):
                    try:
                        with conectar() as conn:
                            cursor = conn.cursor()
                            # CAMBIO CLAVE: UPDATE en lugar de DELETE
                            # Seteamos notas y ejercicios en NULL para que el sistema lo vea como "no rendido"
                            # pero NO tocamos la columna 'asistencia' (que seguirá siendo 'AUSENTE')
                            cursor.execute("""
                                UPDATE reportes_diarios 
                                SET ejercicios_completados = NULL, 
                                    ejercicios_correctos = NULL, 
                                    nota_final = NULL 
                                WHERE id_alumno = ? AND id_clase = ?
                            """, (id_al_elegido, id_clase_justificar))
                            conn.commit()
                        
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
        
        try:
            with conectar() as conn:
                query_monitor = """
                    SELECT 
                        alumnos.nombre AS Alumno, 
                        reportes_diarios.asistencia AS Asistencia,
                        reportes_diarios.ejercicios_completados AS Hechos, 
                        reportes_diarios.ejercicios_correctos AS Correctos, 
                        reportes_diarios.nota_oral AS "Nota Oral",
                        reportes_diarios.nota_final AS "Nota Final",
                        clases.fecha AS Fecha
                    FROM reportes_diarios
                    INNER JOIN alumnos ON reportes_diarios.id_alumno = alumnos.id_alumno
                    INNER JOIN clases ON reportes_diarios.id_clase = clases.id_clase
                    WHERE reportes_diarios.id_clase = ? 
                    AND UPPER(TRIM(alumnos.curso)) = UPPER(TRIM(?))
                    ORDER BY alumnos.nombre ASC
                """
                
                df_mon = pd.read_sql_query(query_monitor, conn, params=(id_clase_input, curso_seleccionado))
                
                if not df_mon.empty:
                    # LLAMAMOS A LA COLUMNA FECHA DIRECTO (del primer renglón)
                    fecha_clase = df_mon['Fecha'].iloc[0]
                    
                    # SUBHEADER CORTO:
                    st.subheader(f"📈 {curso_seleccionado} - Clase № {id_clase_input} - {fecha_clase}")
                    
                    # --- HISTOGRAMA ---
                    # Filtramos solo a los presentes para el histograma de notas reales
                    df_presentes = df_mon[df_mon['Asistencia'] == 'PRESENTE'].copy()
                    
                    if not df_presentes.empty:
                        import plotly.express as px
                        
                        # Crear el histograma
                        fig = px.histogram(
                            df_presentes, 
                            x="Nota Final", 
                            nbins=10, 
                            range_x=[0, 11],
                            title="Distribución de Calificaciones (Presentes)",
                            labels={'Nota Final': 'Calificación', 'count': 'Cantidad de Alumnos'},
                            color_discrete_sequence=['#28a745'] # Verde como tus notas
                        )
                        
                        # Ajustes visuales para que se vea limpio
                        fig.update_layout(
                            xaxis=dict(tickmode='linear', tick0=1, dtick=1),
                            yaxis_title="Cantidad de Alumnos", # Reforzamos el nombre del eje Y
                            bargap=0.1, 
                            height=350,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )

                        # ESTO ES LO QUE CENTRA LA BARRA SOBRE EL NÚMERO
                        fig.update_traces(xbins=dict(
                            start=0.5,   # Empezamos en 0.5 para que el '1' sea el centro
                            end=10.5,    # Terminamos en 10.5 para que el '10' sea el centro
                            size=1       # Cada barra ocupa exactamente 1 unidad de nota
                        ))
                        
                        # Mostramos el gráfico
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Métricas rápidas arriba de la tabla
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Promedio Clase", f"{df_presentes['Nota Final'].mean():.2f}")
                        col2.metric("Aprobados", len(df_presentes[df_presentes['Nota Final'] >= 6]))
                        col3.metric("Ausentes", len(df_mon[df_mon['Asistencia'] == 'AUSENTE']))
                    
                    # --- LA TABLA DE SIEMPRE (DEBAJO DEL GRÁFICO) ---
                    st.write("### Detalle por Alumno")
                    def resaltar_ausencia(val):
                        color = '#FF4B4B' if val == 'AUSENTE' else '#28a745'
                        return f'color: {color}; font-weight: bold'
        
                    df_estilado = df_mon.style.map(resaltar_ausencia, subset=['Asistencia'])
                    st.dataframe(df_estilado, use_container_width=True, hide_index=True)
                    
                    st.caption(f"✅ Mostrando {len(df_mon)} registros encontrados.")
                    
                else:
                    st.subheader(f"📈 {curso_seleccionado} - Clase № {id_clase_input}")
                    st.info("No hay registros para esta clase.")
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
        
        # --- 8. REPORTE TRIMESTRAL (Cálculo de Tendencias y Notas) ---
        st.divider()
        st.subheader("📊 Generador de Notas Trimestrales")

        with st.expander("Calcular Acta del Trimestre", expanded=False):
            trimestre_n = st.selectbox("Seleccione el Trimestre:", ["1", "2", "3"], key="trim_sel")
            
            # --- DENTRO DEL EXPANDER DEL PROFESOR ---
            if st.button("🚀 GENERAR REPORTE", key="btn_generar_acta", use_container_width=True):
                try:
                    import numpy as np # Aseguramos que estén disponibles para los métodos de la clase
                    import pandas as pd
            
                    with conectar() as conn:
                        cursor = conn.cursor()
                        # 1. Traer alumnos del curso activo
                        cursor.execute("SELECT id_alumno, nombre, curso FROM alumnos WHERE UPPER(curso) = UPPER(?)", (curso_seleccionado,))
                        
                        # DEFINIMOS LA VARIABLE AQUÍ MISMO
                        alumnos_lista = cursor.fetchall() 
            
                        if not alumnos_lista:
                            st.warning(f"No se encontraron alumnos registrados en el curso: {curso_seleccionado}")
                        else:
                            datos_reporte = []
                            
                            with st.spinner("Sincronizando promedios y tendencias de cada alumno..."):
                                for id_al, nombre_al, curso_al in alumnos_lista:
                                    # 2. INSTANCIAMOS LA CLASE (Usando 'Alumno' como definiste arriba)
                                    obj_al = Alumno(id_al, nombre_al, curso_al)
                                    
                                    # 3. SINCRONIZAMOS TRIMESTRE (Limpia Nones y aplica nota > 0)
                                    obj_al.sincronizar_historial_por_trimestre(str(trimestre_n))
                                    
                                    # 4. PROCESAMOS SEGÚN CANTIDAD DE NOTAS
                                    if not obj_al.historial:
                                        # Caso sin notas (Inasistencia total o sin carga)
                                        p_base, a_esf, a_efi, n_final = "---", "0", "0", "---"
                                    else:
                                        # Intentamos calcular tendencia (m1, m2)
                                        res_t = obj_al.graficar_tendencia()
                                        
                                        if isinstance(res_t, tuple):
                                            # Caso: 2 o más notas (Usa tus ajustes de 0.3)
                                            m_esf, m_efi = res_t
                                            dt = obj_al.calcular_nota_trimestral(m_esf, m_efi)
                                            
                                            p_base = f"{dt['promedio']:.2f}"
                                            a_esf = dt['ajuste_esfuerzo']
                                            a_efi = dt['ajuste_eficacia']
                                            n_final = dt['total_entero']
                                        else:
                                            # Caso: 1 sola nota (Promedio simple, sin ajustes)
                                            prom_val = obj_al.promedio()
                                            p_base = f"{prom_val:.2f}" if isinstance(prom_val, (int, float)) else "---"
                                            a_esf, a_efi = "0", "0"
                                            n_final = int(round(float(prom_val))) if isinstance(prom_val, (int, float)) else "---"
            
                                    datos_reporte.append({
                                        "Estudiante": nombre_al,
                                        "Nota Final": n_final,
                                        "Prom. Base": p_base,
                                        "Ajuste Esfuerzo.": a_esf,
                                        "Ajuste Concentración.": a_efi,
                                    })
            
                            # 5. MOSTRAR RESULTADOS
                            df_final = pd.DataFrame(datos_reporte)
                            st.write(f"### 📋 Acta de Calificaciones - {curso_seleccionado} (T{trimestre_n})")
                            # --- NUEVO: SECCIÓN DE ANÁLISIS VISUAL ---
                            df_grafico = df_final[df_final["Nota Final"] != "---"].copy()
                            
                            if not df_grafico.empty:
                                df_grafico["Nota Final"] = pd.to_numeric(df_grafico["Nota Final"])
                                
                                # Histogramas del Trimestre (En color Azul para diferenciar del diario)
                                fig_trim = px.histogram(
                                    df_grafico, 
                                    x="Nota Final", 
                                    nbins=11, 
                                    range_x=[0, 11],
                                    labels={'Nota Final': 'Calificación Final', 'count': 'Alumnos'},
                                    color_discrete_sequence=['#007BFF'],
                                    text_auto=True
                                )
        
                                fig_trim.update_layout(
                                    xaxis=dict(tickmode='linear', tick0=1, dtick=1),
                                    yaxis_title="Cantidad de Alumnos",
                                    bargap=0.1, height=350,
                                    margin=dict(l=20, r=20, t=20, b=20)
                                )
                                fig_trim.update_traces(xbins=dict(start=0.5, end=10.5, size=1))
                                
                                # Mostrar métricas destacadas
                                c1, c2, c3 = st.columns(3)
                                c1.metric("Promedio General", f"{df_grafico['Nota Final'].mean():.2f}")
                                aprobados = len(df_grafico[df_grafico["Nota Final"] >= 6])
                                c2.metric("Aprobados", f"{aprobados} ({int(aprobados/len(df_grafico)*100)}%)")
                                c3.metric("Evaluados", len(df_grafico))
        
                                st.plotly_chart(fig_trim, use_container_width=True)
                                
                            # Tabla de detalles
                            st.dataframe(df_final, use_container_width=True, hide_index=True)
                            st.caption("📌 Nota: Los ajustes de +/- 0.5 se aplican automáticamente según la tendencia de mejora en el desempeño.")
            
                except Exception as e:
                    st.error(f"Error técnico al generar el acta: {e}")
                
                    
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
                        with conectar() as conn:
                            cursor = conn.cursor()

                            # PASO A: Insertar la clase (SQLite genera el ID solo)
                            # No incluimos 'id_clase' en la lista de columnas
                            cursor.execute("""
                                INSERT INTO clases (fecha, tema, ejercicios_totales, trimestre) 
                                VALUES (?, ?, ?, ?)
                            """, ("", tema_new, cant_preguntas, int(trimestre_new)))

                            # PASO B: Obtener el ID que SQLite acaba de generar
                            id_clase_generado = cursor.lastrowid

                            # PASO C: Preparar preguntas con el ID recién obtenido
                            preguntas_finales = []
                            for p in preguntas_lista:
                                # Agregamos el id_clase_generado al principio de cada tupla
                                preguntas_finales.append((id_clase_generado, *p))

                            # PASO D: Insertar las preguntas vinculadas a ese ID
                            cursor.executemany("""
                                INSERT INTO preguntas (id_clase, enunciado, opc_a, opc_b, opc_c, opc_d, correcta)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, preguntas_finales)
                            
                            conn.commit()
                        
                        st.balloons()
                        st.success(f"✅ ¡Éxito! Se ha creado la Clase N° {id_clase_generado} sobre '{tema_new}'.")
                        # No hacemos rerun automático aquí para que el profe pueda ver el ID generado
                        
                    except Exception as e:
                        st.error(f"❌ ERROR: {e}")
                        
        # --- 11. VISUALIZADOR DE CLASES Y PREGUNTAS ---
        st.divider()
        st.subheader("📂 Explorador de Clases y Exámenes")

        try:
            with conectar() as conn:
                # 1. Traer todas las clases registradas
                query_clases = "SELECT * FROM clases ORDER BY id_clase DESC"
                df_clases = pd.read_sql_query(query_clases, conn)

            if df_clases.empty:
                st.info("Aún no hay clases registradas en la base de datos.")
            else:
                st.write("### 1. Seleccione una Clase")
                # Mostramos la tabla de clases para referencia rápida
                st.dataframe(df_clases, use_container_width=True, hide_index=True)

                # Creamos un buscador para elegir la clase y ver sus preguntas
                opciones_clases = {f"ID: {r.id_clase} - {r.tema} ({r.fecha})": r.id_clase for _, r in df_clases.iterrows()}
                clase_a_ver = st.selectbox("🔍 Seleccione una clase para ver sus preguntas:", 
                                        options=opciones_clases.keys(),
                                        index=None,
                                        placeholder="Elija una clase...")

                if clase_a_ver:
                    id_seleccionado = opciones_clases[clase_a_ver]
                    
                    with conectar() as conn:
                        # 2. Traer las preguntas de la clase seleccionada
                        query_preg = """
                            SELECT enunciado, opc_a, opc_b, opc_c, opc_d, correcta 
                            FROM preguntas 
                            WHERE id_clase = ?
                        """
                        df_preguntas = pd.read_sql_query(query_preg, conn, params=(id_seleccionado,))

                    if df_preguntas.empty:
                        st.warning("Esta clase no tiene preguntas vinculadas.")
                    else:
                        st.write(f"### 📝 Preguntas de la Clase ID: {id_seleccionado}")
                        
                        # Mostramos las preguntas de forma estética
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

        # --- 12. GESTIÓN DE ALUMNOS (NUEVO) ---
        st.sidebar.divider()
        with st.expander("👤 Gestión de Alumnos", expanded=False):
            st.subheader("Registrar Nuevo Alumno")
            with st.form("form_nuevo_alumno", clear_on_submit=True):
                nuevo_nombre = st.text_input("Nombre Completo del Alumno:")
                nuevo_curso = st.selectbox("Asignar a Curso:", ["4TO A", "4TO C", "5TO A", "5TO C", "5TO A NATURALES"]) # Ajustá tus cursos aquí
                btn_crear = st.form_submit_button("Registrar Alumno")

                if btn_crear:
                    if nuevo_nombre:
                        try:
                            conn = conectar()
                            cursor = conn.cursor()
                            # Insertamos en la tabla alumnos
                            cursor.execute("INSERT INTO alumnos (nombre, curso) VALUES (?, ?)", 
                                         (nuevo_nombre.strip().upper(), nuevo_curso))
                            conn.commit()
                            conn.close()
                            st.success(f"✅ {nuevo_nombre.upper()} ha sido registrado en {nuevo_curso}")
                        except Exception as e:
                            st.error(f"Error al registrar: {e}")
                    else:
                        st.warning("Por favor, ingresa un nombre.")
            
        # --- 13. CIERRE DE SESIÓN (UN SOLO BOTÓN) ---
        st.sidebar.divider()
        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.session_state["logout_confirmado"] = True
            st.rerun()

















































































