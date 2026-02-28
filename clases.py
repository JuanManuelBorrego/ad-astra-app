# FASE 1: Puerta de Enlace (Login)

#SCRIPT PARA DARLE VIDA NUEVAMENTE A LOS OBJETOS CADA VEZ QUE SE TERMINÓ LA SESIÓN Y DEJARON DE EXISTIR, PORQUE LOS OBJETOS SÓLO VIVEN EN LA RAM
#CON ESTO, SE BUSCA EN LA BASE DE DATOS PARA REVIVIR Y RECARGAR LA CLASE ALUMNO EN TODAS SUS INSTANCIAS, ES DECIR, NACEN NUEVAMENTE TODOS LOS OBJETOS DE ESA CLASE 
#LO PRIMERO, PONGO LA FUNCIÓN db_cargar_rendimiento PORQUE LUEGO LA VOY A LLAMAR EN LA CLASE Alumno (EN EL PUNTO 5 DEL MÉTODO registrar_clase)

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from config import ruta # <-- IMPORTANTE: Trae la ruta única

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CLASE ALUMNO
class Alumno:
    def __init__(self, id_alumno, nombre, curso):
        self.id = id_alumno
        self.nombre = nombre
        self.curso = curso

        # El historial ahora usa id_clase como clave en lugar de fecha
        self.historial = {} 
        
    #------------------------------------------------------------------------------------------------------------------------
    #MÉTODO PARA VER SI EL EXAMEN ESTÁ ABIERTO O NO (ESTE MÉTODO CONSULTA SI EN EL PANEL DEL PROFESOR CAMBIÉ EL ESTADO DEL EXAMEN DE ACTIVO A BLOQUEADO PARA QUE SE LES CIERREN LAS NUEVAS PREGUNTAS A AQUELLOS ALUMNOS QUE CONTINÚEN RESPONDIENDO A PESAR DE QUE SE LES DIJO QUE SE TERMINÓ EL TIEMPO DE EXAMEN)
    def clase_esta_activa(self):
        """Consulta si el profesor mantiene el examen habilitado."""
        try:
            with sqlite3.connect(ruta) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT examen_activo FROM configuracion_clase WHERE id = 1")
                resultado = cursor.fetchone()
                return resultado[0] == 1 if resultado else False
        except:
            return False # Por seguridad, si falla la DB, no dejamos seguir
   #--------------------------------------------------------------------------------------------------------
    # MÉTODO REGISTRAR CLASE: ES LARGO, POR ESO LO DIVIDÍ EN 6 PARTES
    def registrar_clase(self, id_clase, completados, correctos, nota_oral=None):
        
        # 1. CONTAR REALIDAD Y ACTUALIZAR MAESTRO
        with sqlite3.connect(ruta) as conn:
            cursor = conn.cursor()
            
            # Contamos cuántas preguntas existen realmente para esta clase
            cursor.execute("SELECT COUNT(*) FROM preguntas WHERE id_clase = %s", (id_clase,))
            totales_reales = cursor.fetchone()[0]
            
            if totales_reales == 0:
                print(f"❌ Error: No se encontraron preguntas para la clase {id_clase}.")
                return None
            
            # Sincronizamos la tabla 'clases' para que el número manual no estorbe
            cursor.execute("UPDATE clases SET ejercicios_totales = %s WHERE id_clase = %s", 
                           (totales_reales, id_clase))
            conn.commit()
            
        totales = totales_reales # Usamos la verdad absoluta de la tabla preguntas
    
        #2 CALCULAMOS LOS DOS PILARES
        #A) ESFUERZO
        esfuerzo = completados / totales

        # B) EFICACIA Y REGLA DEL 1 POR INASISTENCIA/FALTA DE TRABAJO
        if completados > 0:
            eficacia = correctos / completados
        else:
            eficacia = 0
            # Si no hizo nada (completados == 0), forzamos la nota final a 1.0
            if nota_oral is None: 
                self.historial[id_clase] = {
                    "esfuerzo": 0, "eficacia": 0, "nota_oral": None, "nota_final": 1.0
                }
                # Guardamos directamente y salimos del método
                with sqlite3.connect(ruta) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO reportes_diarios (id_alumno, id_clase, ejercicios_completados, ejercicios_correctos, nota_oral, nota_final)
                        VALUES (%s, %s, 0, 0, NULL, 1.0)
                    """, (self.id, id_clase))
                return 1.0
        
        #3. LÓGICA DE NOTA FINAL (PRIORIDAD ORAL)
        if nota_oral is not None:
            nota_final = float(nota_oral)
        else:
            nota_final = round(((esfuerzo + eficacia) / 2) * 10, 2)
        
        #4. GUARDAR EN EL OBJETO (MEMORIA)
        self.historial[id_clase] = {
            "esfuerzo": esfuerzo,
            "eficacia": eficacia,
            "nota_oral": nota_oral,
            "nota_final": nota_final
        }
        

        # 5. ENVIAR A LA BASE DE DATOS (Código integrado, ya no llama a la de afuera)
        conn = sqlite3.connect(ruta)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reportes_diarios (id_alumno, id_clase, ejercicios_completados, ejercicios_correctos, nota_oral, nota_final)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (self.id, id_clase, completados, correctos, nota_oral, nota_final))
        conn.commit()
        conn.close()

        # 6. RECIÉN ACÁ DEVOLVEMOS EL VALOR PORQUE SI PONÍAMOS EL RETURN ANTES, EL SCRIPT FINALIZA EN ESE MOMENTO Y SE SALTABA TODOS LOS OTROS PASOS DEL MÉTODO registrar_clase
        return nota_final

   #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------     
    # MÉTODO SINCRONIZAR HISTORIAL: COMO LOS OBJETOS SE GUARDAN SÓLO EN LA RAM, CON ESTE MÉTODO APUNTAMOS SIEMPRE A LA BASE DE DATOS PARA RECONSTRUIR EL OBJETO
 
    def sincronizar_historial(self):
        #Busca en la DB los registros previos y los carga en el objeto
        conn = sqlite3.connect(ruta)
        cursor = conn.cursor()
        # Usamos JOIN para traer el total de la clase y calcular el relativo
        query = """
            SELECT r.id_clase, r.ejercicios_completados, r.ejercicios_correctos, 
                   r.nota_final, r.nota_oral, c.ejercicios_totales
            FROM reportes_diarios r
            JOIN clases c ON r.id_clase = c.id_clase
            WHERE r.id_alumno = %s
        """
        cursor.execute(query, (self.id,))
        filas = cursor.fetchall()

        for f in filas:
            id_clase_f = f[0]
            # Usamos un "if" corto para que si es None, lo convierta en 0 (si hay registros cargados solamente con nota oral, estos dejan la celda de "completados" y los "correctos" de la base de datos vacía y esto da error cuando se carga este valor en el script)
            completados_f = f[1] if f[1] is not None else 0
            correctos_f = f[2] if f[2] is not None else 0
            totales_f = f[5]
        
            # Cálculo de Esfuerzo (Cantidad) en porcentaje
            val_esfuerzo = (completados_f / totales_f)*100
            
            # Cálculo de Eficacia (Calidad sobre lo hecho) en porcentaje
            if completados_f > 0:
                val_eficacia = (correctos_f / completados_f)*100
            else:
                val_eficacia = 0
                
            # Llenamos el diccionario del objeto con lo que había en el disco
            self.historial[id_clase_f] = {
                "esfuerzo": val_esfuerzo, 
                "eficacia": val_eficacia,
                "nota_final": f[3],
                "nota_oral": f[4]
            }
        
        # ESPERAMOS QUE EL BUCLE TERMINE Y LUEGO EL CIERRE DE LO QUE SE ABRIÓ EN ESTE MÉTODO VA ACÁ:
        conn.close()
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #MÉTODO OBTENER EL PROMEDIO DE TODAS LAS NOTAS FINALES DE TODAS LAS CLASES AL MOMENTO (SI EL TRIMESTRE CERRASE EN ESE MOMENTO, ESA SERÍA LA NOTA)
    def promedio(self):    
        # Filtramos para que no haya errores si hay datos vacíos (None)
        notas = [n["nota_final"] for n in self.historial.values() if n["nota_final"] is not None]  #Si una clase existe en el historial pero por algún motivo la nota está vacía (None), esa clase no entra en la lista "notas"
        # Si la lista está vacía, devolvemos tu mensaje amigable (ya que no entró después de hacer el bucle ni siquiera una sola nota)
        if not notas:  #esto significa que notas está vacía, es decir que no es True la existencia de notas (una lista vacía es Falsa)
            return 'no hay cargas todavía'
        # Si llegamos acá, el cálculo es 100% seguro
        return round(sum(notas) / len(notas), 2)

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def interpretar_tendencia(self, m_eficacia, m_esfuerzo):
        
        # A. EL SEMÁFORO DEL PROMEDIO (Tu texto personalizado)

        # 1. Calculamos la nota proyectada real (con los +/- 0.5)
        data = self.calcular_nota_trimestral(m_esfuerzo, m_eficacia)
        f_promedio = "" # Inicializamos el mensaje vacío
        
        # 2. Si no hay notas, manejamos el caso inicial
        if isinstance(data, str):
            return "⚪ Todavía no tenés notas registradas para calcular un promedio. ¡A darlo todo!"
        
        # 3. Usamos la nota proyectada (la ya redondeada que va al boletin del SAGE) para el semáforo
        nota_proy = data['total_entero']
        f_promedio = ""
        #El semáforo del promedio en sí.
        if nota_proy < 6:
            f_promedio = "🔴 Si el trimestre terminase hoy, estarías desaprobándolo. ¡Pilas que vos podés subir esa nota!"
        elif 6 <= nota_proy < 7:
            f_promedio = "🟡 Si el trimestre terminase hoy, estarías aprobando por poco. ¡No te arriesgues a estar en el límite y tratá de levantar un poquito más la nota para que tengás mayor tranquilidad!"
        elif 7 <= nota_proy < 9:
            f_promedio = "🟢 Si el trimestre terminase hoy, estarías aprobando. ¡A seguir con actitud!"
        else: # 9 a 10
            f_promedio = "🌟 Venís espectacular en el trimestre. Tremendo orgullo y tranquilidad saber que si seguís así tu trimestre será aprobado. ¡No aflojemos en lo que falta y felicitaciones por lo que hiciste hasta acá!"
        
        
        # B. INTERPRETACIÓN DE EFICACIA (Calidad de las respuestas)
        if m_eficacia > 0.3:
            f_eficacia = "📈 CALIDAD DE LAS RESPUESTAS: Tu concentración al resolver cada actividad está mejorando; cada vez hacés mejor las actividades."
        elif m_eficacia < -0.3:
            f_eficacia = "📉 CALIDAD DE LAS RESPUESTAS: Cuidado, tu concentración en las actividades ha bajado últimamente. Hay que mejorar la concentración."
        else:
            f_eficacia = "📊 CALIDAD DE LAS RESPUESTAS: Tu nivel de concentración se mantiene constante."
        # C. INTERPRETACIÓN DE ESFUERZO (Cantidad de ejercicios terminados)
        if m_esfuerzo > 0.3:
            f_esfuerzo = "💪 CANTIDAD DE TRABAJO DIARIO: ¡Excelente! Estás terminando más ejercicios que antes, eso es compromiso."
        elif m_esfuerzo < -0.3:
            f_esfuerzo = "⚠️ CANTIDAD DE TRABAJO DIARIO: Ojo, estás dejando más ejercicios sin terminar que en las primeras clases."
        else:
            f_esfuerzo = "⚙️ CANTIDAD DE TRABAJO DIARIO: Tu ritmo de trabajo (ejercicios completados en cada clase) es estable."
        # Unimos todo para el Dashboard
        reporte = (
            f"{f_promedio}\n"
            f"🤖 ANÁLISIS DE TENDENCIA:\n"
            f"   - {f_eficacia}\n"
            f"   - {f_esfuerzo}"
        )
        return reporte


    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #MÉTODO PARA CALCULAR LA NOTA DEL TRIMESTRE
    
    def calcular_nota_trimestral(self, m1_esfuerzo, m2_eficacia):
        p = self.promedio()
        if isinstance(p, str): return p # Si no hay notas, devolvemos el texto
        
        # Inicializamos variables de ajuste
        ajuste_esfuerzo = 0
        ajuste_eficacia = 0
        txt_esfuerzo = "0"
        txt_eficacia = "0"

        # Lógica de ajuste por tendencia (0.5 puntos)
        # Esfuerzo (m1)
        if m1_esfuerzo > 0.3:
            ajuste_esfuerzo = 0.5
            txt_esfuerzo = "+0,5 (Mejora en CANTIDAD)"
        elif m1_esfuerzo < -0.3:
            ajuste_esfuerzo = -0.5
            txt_esfuerzo = "-0,5 (Caída en CANTIDAD)"

        # Eficacia/Concentración (m2)
        if m2_eficacia > 0.3:
            ajuste_eficacia = 0.5
            txt_eficacia = "+0,5 (Mejora en CALIDAD)"
        elif m2_eficacia < -0.3:
            ajuste_eficacia = -0.5
            txt_eficacia = "-0,5 (Caída en CALIDAD)"

        # Cálculo final decimal
        nota_decimal = p + ajuste_esfuerzo + ajuste_eficacia
        
        # Límites (mínimo 1, máximo 10)
        if nota_decimal < 1: nota_decimal = 1.0
        if nota_decimal > 10: nota_decimal = 10.0
        
        # Redondeo al entero más cercano
        nota_final_entero = int(round(nota_decimal))

        return {
            "promedio": p,
            "ajuste_esfuerzo": txt_esfuerzo,
            "ajuste_eficacia": txt_eficacia,
            "total_decimal": round(nota_decimal, 2),
            "total_entero": nota_final_entero
        }
        
    #------------------------------------------------------------------------------------------------------------------------------------------
    # CÁRGA DE NOTAS POR TRIMESTRES
    def sincronizar_historial_por_trimestre(self, trimestre):
        self.historial = {}
        try:
            conn = sqlite3.connect(ruta)
            cursor = conn.cursor()
            
            # 🔄 Agregamos c.ejercicios_totales a la consulta
            query = """
                SELECT r.id_clase, r.ejercicios_completados, r.ejercicios_correctos, 
                       r.nota_final, c.ejercicios_totales
                FROM reportes_diarios r
                JOIN clases c ON r.id_clase = c.id_clase
                WHERE r.id_alumno = %s AND c.trimestre = %s
            """
            cursor.execute(query, (self.id, trimestre))
            filas = cursor.fetchall()
            
            for f in filas:
                id_clase, comp, corr, nota, totales = f
                
                # 🛡️ Escudos anti-None
                comp = comp if comp is not None else 0
                corr = corr if corr is not None else 0
                totales = totales if (totales is not None and totales > 0) else 1 
                
                # 📈 CALCULAMOS PORCENTAJES (Para que el gráfico de 0-100 tenga sentido)
                val_esfuerzo = (comp / totales) * 100
                val_eficacia = (corr / comp) * 100 if comp > 0 else 0
                
                self.historial[id_clase] = {
                    'esfuerzo': val_esfuerzo, 
                    'eficacia': val_eficacia,
                    'nota_final': float(nota) if nota is not None else 0.0
                }
            conn.close()
        except Exception as e:
            print(f"❌ Error al sincronizar historial trimestral: {e}")
            
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # USO DE PANDAS Y NUMPY PARA LOS GRÁFICOS DE REGRESIÓN LINEAL Agregamos esto a la clase Alumno

    def graficar_tendencia(self):
        if len(self.historial) < 2:
            return "Se necesitan al menos 2 clases para calcular una tendencia."

        # 1. Ordenamos por ID de clase para que la línea de tiempo tenga sentido
        # Extraemos los datos: Eje X (ID clase), Eje Y (Valores)
        ids_ordenados = sorted(self.historial.keys())

        y_esfuerzo = [self.historial[i]['esfuerzo'] for i in ids_ordenados]
        y_eficacia = [self.historial[i]['eficacia'] for i in ids_ordenados]

        # Convertimos a formato numérico para la regresión
        # Convertimos a formato numérico relativo (1, 2, 3...) para que la pendiente sea real, porque si no el eje x se completará con el id de cada clase de la base de datos, siendo que varios id´s no corresponden a clases de ese curso
        # En lugar de usar [1, 5, 20], usamos [0, 1, 2]
        # Eje X: 0, 1, 2... (índice de clase asistida)
        x = np.arange(len(ids_ordenados))
        y_comp = np.array(y_esfuerzo)
        y_corr = np.array(y_eficacia)

        # 2. Creamos la figura con dos sub-gráficos
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # --- Gráfico 1: esfuerzo ---
        ax1.scatter(x, y_comp, color='blue', label='Datos reales')
        m1, b1 = np.polyfit(x, y_comp, 1)
        ax1.plot(x, m1*x + b1, color='red', linestyle='--', label='Tendencia')
        ax1.set_title(f'CANTIDAD: Nivel de Esfuerzo (%) - {self.nombre}')
        
        # FUERZA EL EJE Y: De 0 a 100 (o un poquito más para que no toque el borde)
        ax1.set_ylim(0, 110) 
        ax1.set_ylabel('Porcentaje (%)')
        # Esto agrega el símbolo % a los números del eje Y
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}%'))
        ax1.set_xticks(x) # Muestra 0, 1, 2 en el eje X
        ax1.legend()

        # --- Gráfico 2: eficacia/concentración ---
        ax2.scatter(x, y_corr, color='green', label='Datos reales')
        m2, b2 = np.polyfit(x, y_corr, 1)
        ax2.plot(x, m2*x + b2, color='orange', linestyle='--', label='Tendencia')
        ax2.set_title(f'CALIDAD: Nivel de Concentración (%) - {self.nombre}')
        
        # FUERZA EL EJE Y
        ax2.set_ylim(0, 110)
        ax2.set_ylabel('Porcentaje (%)')
        # Esto agrega el símbolo % a los números del eje Y
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}%'))
        ax2.set_xticks(x)
        ax2.legend()

        plt.tight_layout()
        # Quitamos plt.show() porque en Streamlit usamos st.pyplot(plt.gcf()) en el app.py
        return m1, m2
#FIN DE LA CLASE ALUMNO
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
