#FASE 0: El "Control Remoto" (Administrador)

#🛠️ 1. La Función Principal: DASHBOARD PANEL PROFESOR
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt # Ya que lo usás en la clase Alumno
import sqlite3
import random
import getpass # Para ocultar la clave al escribir
import datetime # Asegurate de tener este import arriba
from clases import Alumno # <-- IMPORTANTE: Trae la clase para poder instanciar
from config import conectar # <-- IMPORTANTE: Trae la ruta única

#DEFINO PRIMERO DOS FUNCIONES QUE LUEGO VAN A ESTAR DENTRO DE panel_profesor() Y LAS DEBO COLOCAR ANTES YA QUE SE INCLUYEN LUEGO

#---------------------------------------------------------------------------------------------------------------------------------------------------

# 🎲 1 Sorteador por Curso (Rápido y Preciso)

def sorteador_orales():
    print("\n🎯 SORTEO DE EXAMEN ORAL")
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # 1. Leemos el curso que está configurado como activo ahora
        cursor.execute("SELECT curso FROM configuracion_clase WHERE id = 1")
        config = cursor.fetchone()
        
        if not config:
            print("⚠️ No hay un curso configurado en la tabla de registro único.")
            conn.close()
            return
            
        curso_activo = config[0]
        print(f"🎲 Sorteando alumno de: {curso_activo}...")

        # 2. Buscamos a los alumnos de ese curso
        cursor.execute("SELECT nombre FROM alumnos WHERE UPPER(curso) = UPPER(?)", (curso_activo,))
        estudiantes = cursor.fetchall()
        conn.close()

        if not estudiantes:
            print(f"⚠️ No se encontraron alumnos para el curso {curso_activo}.")
            return

        # 3. Sorteo
        lista_nombres = [e[0] for e in estudiantes]
        elegido = random.choice(lista_nombres)
        
        print("-" * 30)
        print(f"🔥 ELEGIDO: {elegido.upper()}")
        print("-" * 30)
        
    except Exception as e:
        print(f"❌ Error en el sorteador: {e}")

#---------------------------------------------------------------------------------------------------------------------------------

#🎤 2 Carga Manual de Notas Orales (Paso Crítico)

def cargar_nota_oral_manual():
    print("\n" + "🎤" * 3 + " CARGA NOTA ORAL (Búsqueda Flexible) " + "🎤" * 3)
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # 1. Detectar automáticamente la clase y el curso activos
        cursor.execute("SELECT id_clase_actual, curso FROM configuracion_clase WHERE id = 1")
        config = cursor.fetchone()
        
        if not config:
            print("❌ Error: No hay una clase configurada actualmente.")
            conn.close()
            return
            
        id_clase_activa, curso_activo = config

        # 2. Búsqueda flexible del alumno
        nombre_buscado = input("👤 Nombre o Apellido del alumno: ").strip()
        if not nombre_buscado: return

        # Filtramos por nombre similar Y que pertenezca al curso activo
        cursor.execute("""
            SELECT id_alumno, nombre 
            FROM alumnos 
            WHERE nombre LIKE ? AND UPPER(curso) = UPPER(?)
        """, (f"%{nombre_buscado}%", curso_activo))
        
        resultados = cursor.fetchall()

        if not resultados:
            print(f"❌ No se encontró a '{nombre_buscado}' en el curso {curso_activo}.")
            conn.close()
            return

        # 3. Selección en caso de homónimos
        if len(resultados) > 1:
            print(f"\nSe encontraron {len(resultados)} alumnos. Seleccioná el correcto:")
            for i, r in enumerate(resultados):
                print(f"{i+1}. {r[1]}")
            
            try:
                opcion = int(input("🔢 Número de opción: ")) - 1
                alumno_elegido = resultados[opcion]
            except (ValueError, IndexError):
                print("❌ Selección inválida.")
                conn.close()
                return
        else:
            alumno_elegido = resultados[0]

        id_al, nombre_completo = alumno_elegido

        # 4. Carga de la nota
        try:
            nota = float(input(f"📝 Nota oral para {nombre_completo}: "))
        except ValueError:
            print("❌ Error: La nota debe ser un número (ej: 8 o 7.5).")
            conn.close()
            return

        # 5. Verificamos si ya existe el registro en reportes_diarios
        cursor.execute("""
            SELECT id_reporte FROM reportes_diarios 
            WHERE id_alumno = ? AND id_clase = ?
        """, (id_al, id_clase_activa))
        registro_previo = cursor.fetchone()

        if registro_previo:
            # Si ya existe (quizás ya tiene nota del examen), actualizamos oral y final
            cursor.execute("""
                UPDATE reportes_diarios 
                SET nota_oral = ?, nota_final = ? 
                WHERE id_alumno = ? AND id_clase = ?
            """, (nota, nota, id_al, id_clase_activa))
            print(f"🔄 Registro actualizado: {nombre_completo} ahora tiene un {nota}.")
        else:
            # Si no existe (faltó o todavía no abrió el examen), creamos la fila
            cursor.execute("""
                INSERT INTO reportes_diarios (id_alumno, id_clase, nota_oral, nota_final, ejercicios_completados, ejercicios_correctos)
                VALUES (?, ?, ?, ?, 0, 0)
            """, (id_al, id_clase_activa, nota, nota))
            print(f"✅ Nuevo registro creado para {nombre_completo} con nota {nota}.")

        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error técnico: {e}")
        

#-----------------------------------------------------------------------------------------------------------------------------
#3 (valor 5 del menu profesor) CREAMOS EXAMENES NUEVOS DESDE EL MENU PROFESOR

def menu_profesor_cargar_examen():
    print("\n" + "🍎" * 5 + " CREADOR DE EXÁMENES Y CLASES " + "🍎" * 5)
    
    # 1. Datos Maestros de la Clase
    id_clase = input("🔢 ID de la Clase (ej: 10): ")
    tema = input("📚 Tema de la clase (ej: Fracciones, Revolución de Mayo): ")
    
    # --- NUEVO: Captura de Trimestre ---
    trimestre = ""
    while trimestre not in ['1', '2', '3']:
        trimestre = input("📅 Trimestre al que pertenece (1, 2 o 3): ").strip() 

    try:
        cant = int(input("❓ ¿Cuántas preguntas vas a cargar hoy?: "))
    except:
        cant = 5

    preguntas_para_db = []
    
    # 2. Recolección de Preguntas
    for i in range(1, cant + 1):
        print(f"\n--- PREGUNTA {i} de {cant} ---")
        enunciado = input("📝 Enunciado: ")
        a = input("   A: ")
        b = input("   B: ")
        c = input("   C: ")
        d = input("   D (NDA): ") or "Ninguna de las opciones de la presente lista"
        
        correcta = ""
        while correcta not in ['A', 'B', 'C', 'D']:
            correcta = input("✅ Correcta (A/B/C/D): ").upper()
            
        preguntas_para_db.append((id_clase, enunciado, a, b, c, d, correcta))

    # 3. GUARDADO EN BASE DE DATOS
    try:
        conn = conectar()
        cursor = conn.cursor()

        # PASO A: Crear o Actualizar la clase maestra (INCLUYENDO TRIMESTRE)
        # Agregamos 'trimestre' a la lista de columnas y al VALUES
        cursor.execute("""
            INSERT OR REPLACE INTO clases (id_clase, fecha, tema, ejercicios_totales, trimestre) 
            VALUES (?, ?, ?, ?, ?)
        """, (id_clase, None, tema, cant, int(trimestre)))

        # PASO B: LIMPIEZA DE PREGUNTAS PREVIAS
        cursor.execute("DELETE FROM preguntas WHERE id_clase = ?", (id_clase,))

        # PASO C: Insertar las preguntas nuevas
        cursor.executemany("""
            INSERT INTO preguntas (id_clase, enunciado, opc_a, opc_b, opc_c, opc_d, correcta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, preguntas_para_db)
        
        conn.commit()
        conn.close()
        
        print(f"\n" + "✨" * 10)
        print(f"✅ ¡ÉXITO TOTAL!")
        print(f"📍 Clase {id_clase} ('{tema}') registrada.")
        print(f"📅 Asignada al {trimestre}° Trimestre.")
        print(f"📝 {cant} preguntas vinculadas correctamente.")
        print("✨" * 10)

    except Exception as e:
        print(f"\n❌ ERROR EN BASE DE DATOS: {e}")

    input("\nPresioná Enter para volver...")
        
#-----------------------------------------------------------------------------------------------------------------------------


#FASE 1: EL LOGIN DEL ALUMNO!!! UEUEUEUEUEUEUEUE ===DDD

def login_alumno():
    #Fase 1: Identificación, Validación e Instanciación.
    print("\n" + "="*30)
    print("   ACCESO DE ESTUDIANTES")
    print("="*30)
    
    intentos = 0
    while intentos < 3:
        id_ingresado = input("\nPor favor, ingresá tu ID de Alumno: ")
        
        # 1. Validación de tipo (que no rompa el script si ponen letras)
        if not id_ingresado.isdigit():
            print("❌ Error: El ID debe ser un número.")
            intentos += 1
            continue

        # 2. Consulta a la Base de Datos
        try:
            conn = conectar()
            cursor = conn.cursor()
            
            # Buscamos los datos básicos para crear al alumno
            query = "SELECT id_alumno, nombre, curso FROM alumnos WHERE id_alumno = ?"
            cursor.execute(query, (int(id_ingresado),))
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                # 3. INSTANCIACIÓN: Creamos el objeto Alumno
                id_db, nombre_db, curso_db = resultado
                nuevo_alumno = Alumno(id_db, nombre_db, curso_db)
                
                # 4. SINCRONIZACIÓN: Cargamos su pasado
                nuevo_alumno.sincronizar_historial()
                
                print(f"\n✅ ¡Bienvenido/a, {nuevo_alumno.nombre}!",nuevo_alumno.curso)
                return nuevo_alumno # Devolvemos el objeto "vivo" al main
            else:
                print("❌ ID no encontrado en la base de datos.")
                intentos += 1

        except sqlite3.Error as e:
            print(f"⚠️ Error de conexión a la base de datos: {e}")
            return None

    print("\n⚠️ Demasiados intentos fallidos. Volviendo al menú inicial.")
    return None

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# FASE 2: Dashboard Permanente (Modo Consulta)
#FASE 2_FUNCIÓN mostrar_dashboard()

import matplotlib.pyplot as plt

def mostrar_dashboard(alumno, id_clase_hoy, visible):
    # Esta variable permite que la primera vez sea automático, pero luego respete al usuario
    trimestre_seleccionado = None 

    while True:
        # --- PREPARACIÓN DE DATOS ANUALES (Puntos 1 y 2) ---
        notas_anuales = []
        labels_anuales = ['1° Trim', '2° Trim', '3° Trim']
        ultimo_trimestre_con_datos = "1"
        
        # Escaneamos los 3 trimestres para el panorama general
        for t in ['1', '2', '3']:
            alumno.sincronizar_historial_por_trimestre(t)
            res = alumno.calcular_nota_trimestral(0, 0)
            if isinstance(res, dict):
                notas_anuales.append(res['total_entero'])
                ultimo_trimestre_con_datos = t 
            else:
                notas_anuales.append(0)

        # Si el alumno no eligió manualmente, mostramos el trimestre más alto con notas
        if trimestre_seleccionado is None:
            trimestre_seleccionado = ultimo_trimestre_con_datos

        # 1. CABECERA
        print("\n" + "═"*75)
        print(f" 🎓 PANEL CENTRAL - ESTUDIANTE: {alumno.nombre.upper()}")
        print("═"*75)

        # --- PUNTO 1: GRÁFICO DE BARRAS CON NOTAS TRIMESTRALES ---
        print(" 📊 Generando gráfico de rendimiento anual... (Cerrá la ventana para continuar)")
        plt.figure(figsize=(7, 4))
        colores = ['#3498db', '#9b59b6', '#2ecc71']
        barras = plt.bar(labels_anuales, notas_anuales, color=colores, edgecolor='black')
        plt.axhline(y=6, color='red', linestyle='--', label='Aprobación (6)')
        plt.ylim(0, 11)
        plt.title(f"NOTAS POR TRIMESTRE - {alumno.nombre}")
        plt.ylabel("Nota Final")
        for bar in barras:
            yval = bar.get_height()
            if yval > 0:
                plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, int(yval), ha='center', fontweight='bold')
        plt.legend()
        plt.tight_layout()
        plt.show()

        # --- PUNTO 2: BREVE EXPLICACIÓN DEL GRÁFICO (PANORAMA) ---
        t1, t2, t3 = notas_anuales
        txt_t1 = f"{t1}" if t1 > 0 else "sin notas"
        txt_t2 = f"{t2}" if t2 > 0 else "sin notas"
        txt_t3 = f"{t3}" if t3 > 0 else "sin notas"

        print(f"\n 📝 Panorama si hoy fuera la última clase:")
        print(f"    1er Trimestre {txt_t1}; 2do Trimestre {txt_t2}; 3er Trimestre {txt_t3}")

        # Lógica de aprobación anual (18 pts + T3 >= 6)
        puntos_actuales = sum(notas_anuales)
        if t1 > 0 and t2 > 0 and t3 > 0:
            if (puntos_actuales / 3) >= 6 and t3 >= 6:
                print("    ✨ ¡Estado: APROBADO EL AÑO!")
            elif t3 < 6:
                print("    ⚠️ Ojo: para aprobar el año vas a necesitar un 6 o más en el 3er Trimestre.")
            else:
                print(f"    ❌ Ojo: El promedio no alcanza para aprobar ({puntos_actuales/3:.2f}).")
        else:
            necesarios = 18 - puntos_actuales
            if t3 == 0:
                if necesarios <= 10:
                    print(f"    💡 (Ojo: para aprobar el año vas a necesitar sumar {necesarios} puntos más).")
                else:
                    print(f"    ⚠️ (Necesitás {necesarios} puntos y el máximo es de 10 por trimestre).")

        # --- PUNTO 3: EL TRIMESTRE EN DESARROLLO / SELECCIONADO ---
        print(f"\n" + "─"*75)
        # Identificamos si es vista automática o consulta manual
        estado_txt = "EN DESARROLLO" if trimestre_seleccionado == ultimo_trimestre_con_datos else "CONSULTA"
        print(f" 📍 {estado_txt}: {trimestre_seleccionado}° TRIMESTRE")
        
        # Sincronizamos los datos del trimestre específico para los gráficos de tendencia
        alumno.sincronizar_historial_por_trimestre(trimestre_seleccionado)
        
        if len(alumno.historial) == 0:
            print(f"\n ℹ️  No hay notas todavía de este trimestre ({trimestre_seleccionado}°).")
        else:
            # Mostramos gráficos de regresión y obtenemos pendientes
            res_graf = alumno.graficar_tendencia()
            
            if isinstance(res_graf, tuple):
                m_esf, m_efi = res_graf
                msg_ia = alumno.interpretar_tendencia(m_efi, m_esf)
                dt = alumno.calcular_nota_trimestral(m_esf, m_efi)
                
                # Desglose de la nota final (Punto 3 solicitado)
                print(f"\n 🎯 NOTA PROYECTADA AL CIERRE:")
                print(f"    1) Promedio base de clases:    {dt['promedio']:.2f}")
                print(f"    2) Ajuste por Esfuerzo:        {dt['ajuste_esfuerzo']}") 
                print(f"    3) Ajuste por Concentración:   {dt['ajuste_eficacia']}")
                print(f"    -------------------------------------------")
                print(f"    🚩 NOTA FINAL TRIMESTRAL:      {dt['total_decimal']}")
                print(f"    👉 NOTA EN SAGE (Boletín):     {dt['total_entero']}")
                print(f"    -------------------------------------------")
                print(f"\n 🤖 TUTOR VIRTUAL: {msg_ia}")
            else:
                print(f"\n ℹ️ {res_graf}")

        # --- PUNTO 4: PANEL DE CONTROL DEL ALUMNO ---
        print("\n" + " 🎮 PANEL DE CONTROL:")
        print(" [1, 2, 3] Cambiar trimestre | [E] Rendir | [R] Repasar | [S] Salir")
        
        # Validamos si ya rindió sincronizando el historial completo
        ya_rindio = False
        if id_clase_hoy:
            alumno.sincronizar_historial() # Recuperamos visión total
            if id_clase_hoy in alumno.historial:
                print(" ✅ CLASE DEL DÍA: Ya has completado esta evaluación.")
                ya_rindio = True
            else:
                print(" 🚀 [E] EMPEZAR EXAMEN DEL DÍA")
        
        if visible == 1: 
            print(" 📚 [R] REPASAR MIS EXÁMENES ANTERIORES")
            
        print(" 🚪 [S] CERRAR SESIÓN")
        print("-" * 75)

        opcion = input(" Seleccioná una opción: ").upper()

        # Lógica de navegación del Panel
        if opcion in ['1', '2', '3']:
            trimestre_seleccionado = opcion 
        
        elif opcion == 'E' and id_clase_hoy:
            if not ya_rindio:
                return "EXAMEN"
            else:
                print("\n[!] Ya rendiste esta clase. Mirá tus gráficos actualizados.")
                input("Presioná Enter para continuar...")
        
        elif opcion == 'R' and visible == 1:
            alumno.sincronizar_historial() # Aseguramos historial completo para el repaso
            ver_repaso_examen(alumno)
            
        elif opcion == 'S':
            print(f"\nSaliendo del perfil de {alumno.nombre}...")
            return "LOGOUT"
        
        else:
            print("\n[!] Opción no válida o acción no permitida.")
    
                    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#1. La función "Sintonizadora"
#Esta función es la que hace el trabajo sucio: mira la fila 1 y la compara con el curso del alumno que acaba de entrar.

def obtener_clase_activa(curso_alumno):
    try:
        conn = conectar()
        cursor = conn.cursor()
        # Leemos el "semáforo" del profesor
        cursor.execute("SELECT id_clase_actual, curso FROM configuracion_clase WHERE id = 1")
        config = cursor.fetchone()
        conn.close()
        
        if config:
            id_clase_db, curso_db = config
            # 💡 AQUÍ ESTÁ EL MATCH:
            # 💡 NORMALIZAMOS: Pasamos ambos a mayúsculas y quitamos espacios extra
            if str(curso_db).strip().upper() == str(curso_alumno).strip().upper():
                return id_clase_db
        
        return None # Si no hay match o no hay nada configurado
    except:
        return None

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def ejecutar_examen(estudiante, id_clase_objetivo):
    # 1. Doble Check e Inicio
    print("\n" + "⚠️ " * 10)
    print(f"  ZONA DE EXAMEN - CLASE {id_clase_objetivo}")
    confirmar = input("  ¿Confirmás que querés empezar? (S/N): ").strip().upper()
    
    if confirmar != 'S': return

    # 2. Traer preguntas
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT enunciado, opc_a, opc_b, opc_c, opc_d, correcta FROM preguntas WHERE id_clase = ?", (id_clase_objetivo,))
    preguntas = cursor.fetchall()
    conn.close()

    if not preguntas:
        print("\n⚠️ No hay preguntas para esta clase.")
        return

    # VARIABLES DE SEGUIMIENTO
    aciertos = 0
    intentados = 0  # <--- Esto es lo que vos querés contar
    total_examen = len(preguntas)
    finalizado_prematuro = False
    bloqueado_por_profesor = False # Nueva bandera de control

    # 3. Bucle del Examen
    for i, p in enumerate(preguntas, 1):
        if finalizado_prematuro or bloqueado_por_profesor: break
        
        # --- 🛡️ EL CANDADO: Chequeo de seguridad antes de cada pregunta ---
        if not estudiante.clase_esta_activa():
            bloqueado_por_profesor = True
            continue # Salta al final del bucle

        enunciado, a, b, c, d, correcta_letra = p
        mapeo_db = {'A': str(a), 'B': str(b), 'C': str(c), 'D': str(d)}
        texto_correcto = mapeo_db[correcta_letra]

        opciones_mezcladas = [str(a), str(b), str(c), str(d)]
        random.shuffle(opciones_mezcladas)

        print(f"\n--- PREGUNTA {i}/{total_examen} ---")
        print(f"❓ {enunciado}")
        
        letras_visuales = ['A', 'B', 'C', 'D']
        for letra, texto in zip(letras_visuales, opciones_mezcladas):
            print(f"   {letra}) {texto}")
        print("   F) [FINALIZAR Y ENTREGAR]")

        rta_alumno = ""
        while rta_alumno not in ['A', 'B', 'C', 'D', 'F']:
            rta_alumno = input("\n> Tu respuesta: ").strip().upper()

        if rta_alumno == 'F':
            finalizado_prematuro = True
            continue 

        # --- LÓGICA DE CONTEO ---
        intentados += 1 # El alumno respondió algo (A, B, C o D)
        
        indice_elegido = letras_visuales.index(rta_alumno)
        if opciones_mezcladas[indice_elegido] == texto_correcto:
            aciertos += 1
        
        # MODO SILENCIOSO: No imprimimos si está bien o mal aquí
        print("✔️ Registrado. Pasando a la siguiente...")

    # 4. Registro y Feedback Final
    # Enviamos 'intentados' en lugar del total de la tabla si preferís medir esfuerzo real
    # Pero ojo: la nota suele calcularse sobre el total del examen para ser justa
    if bloqueado_por_profesor:
        print("\n" + "🛑" * 15)
        print(" ¡TIEMPO AGOTADO! El profesor ha cerrado el acceso.")
        print(" Se enviarán tus respuestas registradas hasta este momento.")
        print("🛑" * 15)
        
    nota_final = estudiante.registrar_clase(id_clase_objetivo, intentados, aciertos)
    
    print("\n" + "🏁" * 15)
    print("  EXAMEN ENTREGADO")
    print(f"  Preguntas intentadas: {intentados} de {total_examen}")
    print(f"  Aciertos logrados: {aciertos}")
    print(f"  Tu nota final: {nota_final}")
    print("🏁" * 15)
    
#----------------------------------------------------------------------------------------------------------------------
# OPCIÓN PARA AGREGAR ALUMNOS NUEVOS DENTRO DEL COMANDO DEL USUARIO PROFESOR

def registrar_nuevo_alumno():
    print("\n" + "👤" * 5 + " REGISTRO DE NUEVO ESTUDIANTE " + "👤" * 5)
    
    nombre = input("📝 Nombre completo: ").strip().upper()
    curso = input("🎓 Curso (Ej: 5TO A): ").strip().upper()

    if not nombre or not curso:
        print("❌ Error: El nombre y el curso son obligatorios.")
        return

    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Al pasar NULL en id_alumno, SQLite activa el AUTOINCREMENT
        cursor.execute("""
            INSERT INTO alumnos (id_alumno, nombre, curso) 
            VALUES (NULL, ?, ?)
        """, (nombre, curso))
        
        # Recuperamos el ID que la base de datos asignó automáticamente
        nuevo_id = cursor.lastrowid
        
        conn.commit()
        conn.close()

        print(f"\n" + "✅" * 10)
        print(f" ¡ESTUDIANTE REGISTRADO!")
        print(f" 👤 Nombre: {nombre}")
        print(f" 🆔 ID ASIGNADO: {nuevo_id}")
        print(f" 🎓 Curso: {curso}")
        print("✅" * 10)
        print(f"👉 Importante: El alumno debe usar el ID {nuevo_id} para ingresar.")
        
    except Exception as e:
        print(f"❌ Error al guardar en la base de datos: {e}")

    input("\nPresioná Enter para volver al panel...")

#---------------------------------------------------------------------------------------------------------------------------------
#FUNCIÓN PARA VER LA TABLA DE NOTAS POR CURSOS

import pandas as pd
import sqlite3

def ver_reporte_curso():
    # Eliminamos el input. Ahora el sistema es proactivo.
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # 1. Leemos la configuración de la fila única
        cursor.execute("SELECT id_clase_actual, curso FROM configuracion_clase WHERE id = 1")
        config = cursor.fetchone()
        
        if not config:
            print("⚠️ No hay ninguna clase activa configurada actualmente.")
            conn.close()
            return
            
        id_clase_activa, curso_activo = config

        # 2. Traemos los datos directamente usando la configuración detectada
        query = """
            SELECT 
                a.nombre AS "Estudiante", 
                r.ejercicios_completados AS "Intentados", 
                r.ejercicios_correctos AS "Correctos", 
                r.nota_final AS "Nota"
            FROM alumnos a
            LEFT JOIN reportes_diarios r ON a.id_alumno = r.id_alumno AND r.id_clase = ?
            WHERE UPPER(a.curso) = UPPER(?)
        """
        
        df = pd.read_sql_query(query, conn, params=(id_clase_activa, curso_activo))
        conn.close()

        # 3. Visualización prolija
        print(f"\n" + "📈" * 5 + f" MONITOR ACTIVO: {curso_activo} " + "📈" * 5)
        print(f"📍 Clase ID: {id_clase_activa}")
        print("=" * 65)
        
        if df.empty:
            print(f"⚠️ No hay alumnos registrados para el curso {curso_activo}.")
        else:
            # Rellenamos con "---" para que las inasistencias no queden como NaN
            print(df.fillna("---").to_string(index=False))
            
        print("=" * 65)
        
    except Exception as e:
        print(f"❌ Error técnico: {e}")
    
    input("\nPresioná Enter para volver al panel...")
        
#----------------------------------------------------------------------------------------------------------------------------------------------------
#GENERAMOS LAS NOTAS POR TRIMESTRES

def ver_reporte_trimestral():
    print("\n" + "📊" * 5 + " GENERADOR DE NOTAS TRIMESTRALES " + "📊" * 5)
    
    # 1. Obtenemos curso de la configuración y preguntamos el trimestre
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT curso FROM configuracion_clase WHERE id = 1")
        config = cursor.fetchone()
        
        if not config:
            print("❌ Error: Configure primero un curso en el panel.")
            conn.close()
            return
            
        curso_ver = config[0]
        trimestre_n = input(f"📅 Ingrese el Trimestre a procesar para {curso_ver} (1, 2 o 3): ").strip()
        
        if trimestre_n not in ['1', '2', '3']:
            print("❌ Trimestre inválido.")
            conn.close()
            return

        # 2. Traemos la lista de alumnos de ese curso
        cursor.execute("SELECT id_alumno, nombre, curso FROM alumnos WHERE UPPER(curso) = UPPER(?)", (curso_ver,))
        lista_alumnos = cursor.fetchall()
        conn.close()

        if not lista_alumnos:
            print(f"❌ No se encontraron alumnos para {curso_ver}.")
            return

        print(f"\n🚀 Procesando Trimestre {trimestre_n} para {curso_ver}...")
        datos_reporte = []

        # 3. Iteración sobre alumnos con filtro de trimestre
        for id_al, nom, cur in lista_alumnos:
            estudiante = Alumno(id_al, nom, cur)
            
            # ¡IMPORTANTE! Modificamos la sincronización para que solo traiga este trimestre
            estudiante.sincronizar_historial_por_trimestre(trimestre_n)
            
            p = estudiante.promedio()

            if isinstance(p, str) or p is None:
                prom_base, adj_esf, adj_efi, nota_f = "---", "---", "---", "---"
            else:
                ids_ordenados = sorted(estudiante.historial.keys())
                if len(ids_ordenados) >= 2:
                    x = np.arange(len(ids_ordenados))
                    y_esf = [estudiante.historial[i]['esfuerzo'] for i in ids_ordenados]
                    y_efi = [estudiante.historial[i]['eficacia'] for i in ids_ordenados]
                    
                    # Cálculo de tendencias (pendientes)
                    m1, _ = np.polyfit(x, y_esf, 1)
                    m2, _ = np.polyfit(x, y_efi, 1)
                    
                    data = estudiante.calcular_nota_trimestral(m1, m2)
                else:
                    # Si solo tiene 1 nota, el ajuste es 0
                    data = {
                        "promedio": p,
                        "ajuste_esfuerzo": "0",
                        "ajuste_eficacia": "0",
                        "total_entero": int(round(p))
                    }
                
                prom_base = f"{data['promedio']:.2f}"
                adj_esf = data["ajuste_esfuerzo"]
                adj_efi = data["ajuste_eficacia"]
                nota_f = data["total_entero"]

            datos_reporte.append({
                "Estudiante": nom,
                "Prom. Base": prom_base,
                "Adj. Esf.": adj_esf,
                "Adj. Efi.": adj_efi,
                "Nota Final": nota_f
            })
            
        # 4. Mostrar Resultados
        df_final = pd.DataFrame(datos_reporte)
        print("\n" + "=" * 80)
        print(f"📋 ACTA DE CALIFICACIONES - TRIMESTRE {trimestre_n}")
        print("=" * 80)
        print(df_final.to_string(index=False))
        print("=" * 80)
        print("📌 El ajuste de +/- 0.5 se aplica por tendencia de mejora/descenso.")
        
    except Exception as e:
        print(f"❌ Error al generar el reporte: {e}")
    
    input("\nPresioná Enter para volver...")

#--------------------------------------------------------------------------------------------------------------------------------------------------
#CIERRE DE PLANILLAS CON 1 A LOS AUSENTES

def completar_inasistencias_con_uno():
    print("\n--- 🔐 CIERRE DE PLANILLA DIARIA ---")
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # 1. Obtenemos la configuración actual
        cursor.execute("SELECT id_clase_actual, curso FROM configuracion_clase WHERE id = 1")
        config = cursor.fetchone()
        
        if not config:
            print("❌ Error: No se encontró una clase activa en la configuración.")
            conn.close()
            return
            
        id_clase_activa, curso_activo = config
        
        # 2. Paso Intermedio: Confirmación explícita
        print(f"\n⚠️  ATENCIÓN: Vas a cerrar la planilla de:")
        print(f"   📅 Clase ID: {id_clase_activa}")
        print(f"   👥 Curso: {curso_activo}")
        print("-" * 40)
        
        confirmar = input("¿Confirmamos el cierre de la planilla del día completando con 1 a aquellos alumnos que faltaron? (S/N): ").strip().upper()
        
        if confirmar == 'S':
            # 1. Obtenemos la fecha de hoy para el cierre
            fecha_cierre = datetime.date.today().strftime("%d/%m/%Y")
            
            # 2. ACTUALIZAMOS LA FECHA EN LA TABLA CLASES
            cursor.execute("""
                UPDATE clases 
                SET fecha = ? 
                WHERE id_clase = ?
            """, (fecha_cierre, id_clase_activa))
                
            # 3. Ejecución de la carga masiva
            query = """
                INSERT INTO reportes_diarios (id_alumno, id_clase, ejercicios_completados, ejercicios_correctos, nota_final)
                SELECT id_alumno, ?, 0, 0, 1.0
                FROM alumnos
                WHERE UPPER(curso) = UPPER(?) 
                AND id_alumno NOT IN (
                    SELECT id_alumno FROM reportes_diarios WHERE id_clase = ?
                )
            """
            cursor.execute(query, (id_clase_activa, curso_activo, id_clase_activa))
            filas_afectadas = cursor.rowcount
            conn.commit()
            
            print(f"\n✅ Planilla cerrada con fecha {fecha_cierre}. Se registraron {filas_afectadas} ausentes.")
        
        else:
            print("\n🛑 Operación cancelada. No se modificó ninguna nota.")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error en la base de datos: {e}")

#----------------------------------------------------------------------------------------------------------------------------------------
#JUSTIFICACIÓN DE INASISTENCIAS (ELIMINACIÓN DEL REGISTRO PARA ESA CLASE)
def justificar_inasistencia_manual():
    print("\n--- 🏥 JUSTIFICAR INASISTENCIA (Borrar nota 1.0) ---")
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # 1. Detectamos la clase activa para facilitar el trámite
        cursor.execute("SELECT id_clase_actual, curso FROM configuracion_clase WHERE id = 1")
        config = cursor.fetchone()
        id_sugerido = config[0] if config else None
        
        # 2. Pedimos los datos
        nombre_buscado = input("Nombre o Apellido del alumno: ").strip()
        
        # 3. Buscamos coincidencias
        cursor.execute("SELECT id_alumno, nombre, curso FROM alumnos WHERE nombre LIKE ?", (f"%{nombre_buscado}%",))
        resultados = cursor.fetchall()

        if not resultados:
            print("❌ No se encontró ningún alumno.")
            return

        # 4. Selección del alumno (por si hay nombres similares)
        if len(resultados) > 1:
            print("\nSe encontraron varios alumnos. Seleccioná el número correcto:")
            for i, al in enumerate(resultados):
                print(f"{i+1}. {al[1]} ({al[2]})")
            
            opcion = int(input("Número de opción: ")) - 1
            alumno_elegido = resultados[opcion]
        else:
            alumno_elegido = resultados[0]

        id_al, nombre_al, curso_al = alumno_elegido

        # 5. Confirmar clase y borrar
        id_clase = input(f"ID de clase para {nombre_al} [Default {id_sugerido}]: ").strip()
        if not id_clase: id_clase = id_sugerido

        confirmar = input(f"⚠️ ¿Confirmás borrar la nota de {nombre_al} en la clase {id_clase}? (S/N): ").upper()
        
        if confirmar == 'S':
            cursor.execute("DELETE FROM reportes_diarios WHERE id_alumno = ? AND id_clase = ?", (id_al, id_clase))
            conn.commit()
            print(f"✅ ¡Listo! Registro borrado para {nombre_al}.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        
#----------------------------------------------------------------------------------------------------------------------------------------------
#VER TABLA POR ALUMNO Y TRIMESTRE

def ver_progreso_individual_trimestral():
    print("\n" + "👤" * 3 + " REPORTE INDIVIDUAL POR TRIMESTRE " + "👤" * 3)
    
    nombre_buscado = input("🔍 Nombre o Apellido del alumno: ").strip()
    if not nombre_buscado:
        return
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Búsqueda flexible
        cursor.execute("SELECT id_alumno, nombre, curso FROM alumnos WHERE nombre LIKE ?", (f"%{nombre_buscado}%",))
        resultados = cursor.fetchall()
        
        if not resultados:
            print(f"❌ No se encontró a '{nombre_buscado}'.")
            conn.close()
            return
            
        # Selección de alumno
        if len(resultados) > 1:
            print(f"\nCoincidencias encontradas:")
            for i, r in enumerate(resultados):
                print(f"{i+1}. {r[1]} ({r[2]})")
            opcion = int(input("\n🔢 Número de opción: ")) - 1
            alumno = resultados[opcion]
        else:
            alumno = resultados[0]
            
        id_al, nombre_al, curso_al = alumno
        trimestre_n = input(f"📅 Trimestre para {nombre_al} (1, 2 o 3): ").strip()

        # CONSULTA CORREGIDA: Usamos 'tema' en lugar de 'nombre_clase'
        query = """
            SELECT 
                c.id_clase AS "ID",
                c.fecha AS "Fecha",
                c.tema AS "Tema",
                r.nota_final AS "Nota"
            FROM reportes_diarios r
            JOIN clases c ON r.id_clase = c.id_clase
            WHERE r.id_alumno = ? AND c.trimestre = ?
            ORDER BY c.id_clase ASC
        """
        
        df = pd.read_sql_query(query, conn, params=(id_al, trimestre_n))
        conn.close()

        print(f"\n" + "=" * 50)
        print(f"📄 INFORME: {nombre_al} | {curso_al}")
        print(f"📅 TRIMESTRE: {trimestre_n}")
        print("=" * 50)
        
        if df.empty:
            print(f"\nℹ️ Sin notas en el {trimestre_n}° Trimestre.")
        else:
            print(df.to_string(index=False))
            print("-" * 50)
            promedio = df["Nota"].mean()
            print(f"⭐ PROMEDIO TRIMESTRAL: {promedio:.2f}")
        print("=" * 50)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPresioná Enter para volver...")
        
#-----------------------------------------------------------------------------------------------------------------------------------------
def panel_profesor():
    # 1. ACCESO DE SEGURIDAD
    print("\n" + "🔐" * 20)
    clave = getpass.getpass(" INGRESE CLAVE DE ADMINISTRADOR: ")
    if clave != "35445771":
        print("❌ Acceso denegado.")
        return None

    # Variables de estado locales (se sincronizan con la DB al entrar)
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id_clase_actual, curso, feedback_visible, examen_activo FROM configuracion_clase WHERE id = 1")
    config = cursor.fetchone()
    conn.close()

    id_clase = config[0] if config else "---"
    curso_objetivo = config[1] if config else "---"

    while True:
        # Consulta de refresco para estados dinámicos
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT feedback_visible, examen_activo FROM configuracion_clase WHERE id = 1")
        res = cursor.fetchone()
        conn.close()
        
        visible = res[0] if res else 0
        estado_actual = res[1] if res else 0

        # Interfaz visual
        candado_txt = "🔓 ABIERTO" if estado_actual == 1 else "🔒 CERRADO"
        feedback_txt = "👁️ VISIBLE" if visible == 1 else "🚫 BLOQUEADO"

        print("\n" + "═" * 65)
        print(" 🍎 PANEL DE CONTROL DOCENTE")
        print("═" * 65)
        print(f" 📍 CLASE ACTIVA: {id_clase}  |  🎓 CURSO: {curso_objetivo}")
        print(f" ⚙️  EXAMEN: {candado_txt}   |  ⚙️  FEEDBACK: {feedback_txt}")
        print("═" * 65)

        # OPCIÓN 1: Configuración
        print(" [1] SELECCIONAR CLASE Y CURSO (Sincronizar Aula) 📡")

        # OPCIÓN 2: Alternar Feedback (Texto dinámico solicitado)
        if visible == 0:
            print(" [2] Habilitar que los alumnos vean sus respuestas hoy 👁️")
        else:
            print(" [2] Deshabilitar la visualización de respuestas a los alumnos 🚫")

        # OPCIÓN 3: Alternar Examen (Texto dinámico solicitado)
        if estado_actual == 0:
            print(" [3] ABRIR EXAMEN (Permitir ingreso de alumnos) 🟢")
        else:
            print(" [3] CERRAR EXAMEN (Bloquear/Finalizar exámenes) ⛔")

        # RESTO DE OPCIONES
        print(" [4] LANZAR SORTEADOR DE ORALES 🎲")
        print(" [5] CARGAR NOTA ORAL MANUAL 🎤")
        print(" [6] REGISTRAR/EDITAR EXAMEN EN DB 📝")
        print(" [7] REGISTRAR NUEVO ALUMNO 👤") 
        print(" [8] VER TABLA DE NOTAS DEL CURSO DEL DÍA 📊")
        print(" [9] REPORTE TRIMESTRAL 📅")
        print("[10] CIERRE DE LA PLANILLA DE NOTAS DEL DÍA")
        print("[11] JUSTIFICAR INASISTENCIA")
        print("[12] VER PLANILLA DE NOTAS POR ALUMNO")
        print(" [0] SALIR AL MENÚ PRINCIPAL 🚪")
        
        opcion = input("\n Seleccioná una acción: ")

        if opcion == "1":
            nueva_clase = input("📌 Ingrese el ID de la clase: ")
            nuevo_curso = input("🎓 Curso (Ej: 5TO A): ").strip().upper()
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clases WHERE id_clase = ?", (nueva_clase,))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE configuracion_clase 
                    SET id_clase_actual = ?, curso = ?, examen_activo = 1
                    WHERE id = 1
                """, (nueva_clase, nuevo_curso))
                conn.commit()
                id_clase, curso_objetivo = nueva_clase, nuevo_curso
                print(f"\n✅ Aula sincronizada: {nuevo_curso} ahora rinde Clase {nueva_clase}.")
            else:
                print(f"❌ Error: La clase {nueva_clase} no existe. Cargala primero en la opción [6].")
            conn.close()

        elif opcion == "2":
            nuevo_fb = 0 if visible == 1 else 1
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("UPDATE configuracion_clase SET feedback_visible = ? WHERE id = 1", (nuevo_fb,))
            conn.commit()
            conn.close()
            print(f"\n📢 FEEDBACK: {'HABILITADO' if nuevo_fb == 1 else 'DESHABILITADO'}")

        elif opcion == "3":
            nuevo_estado = 0 if estado_actual == 1 else 1
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("UPDATE configuracion_clase SET examen_activo = ? WHERE id = 1", (nuevo_estado,))
            conn.commit()
            conn.close()
            print(f"\n📢 ACCESO EXAMEN: {'CERRADO' if nuevo_estado == 0 else 'ABIERTO'}")

        elif opcion == "4":
            sorteador_orales()

        elif opcion == "5":
            cargar_nota_oral_manual()

        elif opcion == "6":
            menu_profesor_cargar_examen()
            
        elif opcion == "7":
            registrar_nuevo_alumno() 
            
        elif opcion == "8":
            ver_reporte_curso()
        
        elif opcion == "9":
            ver_reporte_trimestral()
        
        elif opcion=="10":
            completar_inasistencias_con_uno()
        
        elif opcion=="11":
            justificar_inasistencia_manual()
            
        elif opcion=="12":
            ver_progreso_individual_trimestral()

        elif opcion == "0":
            return id_clase, visible


#-----------------------------------------------------------------------------------------------------------------------------
#FUNCIÓN PARA EL USUARIO ALUMNO: PUEDE CONSULTAR POR CADA CLASE CUÁNTOS EJERCICIOS HIZO, CUÁLES RESPONDIÓ CORRECTAMENTE Y CUÁLES NO.

def ver_repaso_examen(alumno):
    # 1. Listar qué clases rindió
    clases_rendidas = list(alumno.historial.keys())
    
    if not clases_rendidas:
        print("\n ℹ️  Aún no has rendido ningún examen para repasar.")
        return

    print("\n" + "📚" * 5 + " HISTORIAL DE EXÁMENES " + "📚" * 5)
    for c in clases_rendidas:
        print(f" 📝 Clase {c}")
    
    entrada = input("\n🔎 ¿Qué clase deseás repasar? (ID): ").strip()
    if not entrada.isdigit():
        print("❌ Debes ingresar un número de clase válido.")
        return
    clase_elegida = int(entrada)
    if clase_elegida not in clases_rendidas:
        print("❌ No tienes registros de esa clase o no existe.")
        return

    # 2. Consultar la DB para ver el detalle
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Unimos las preguntas con la respuesta que dio el alumno (si la guardaste)
        # NOTA: Para esto necesitamos que tu tabla 'respuestas_detalladas' exista.
        # Si no la tenés, te muestro cómo traer las preguntas de esa clase:
        cursor.execute("""
            SELECT enunciado, opc_a, opc_b, opc_c, opc_d, correcta 
            FROM preguntas 
            WHERE id_clase = ?
        """, (clase_elegida,))
        
        preguntas = cursor.fetchall()
        conn.close()

        print(f"\n--- REPASO CLASE {clase_elegida} ---")
        for i, p in enumerate(preguntas, 1):
            enun, a, b, c, d, correcta_letra = p
            mapeo = {'A': a, 'B': b, 'C': c, 'D': d}
            
            print(f"\n{i}. {enun}")
            print(f" ✅ Respuesta correcta: {mapeo[correcta_letra]}")
        
        input("\nPresioná Enter para volver...")
        
    except Exception as e:

        print(f"❌ Error al cargar el repaso: {e}")



