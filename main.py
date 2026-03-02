# main.py
from db import query, execute
import pandas as pd

from clases import Alumno
from funciones import (
    login_alumno, 
    panel_profesor, 
    obtener_clase_activa, 
    mostrar_dashboard,
    ejecutar_examen,
)

def menu_principal():
    while True:
        print("\n" + "█" * 50)
        print("      SISTEMA EDUCATIVO INTEGRADO V.0.1")
        print("█" * 50)
        print("\n [1] SECCIÓN ESTUDIANTES 🎓")
        print(" [2] SECCIÓN PROFESOR DE MATEMÁTICA JUAN MANUEL BORREGO 🍎")
        print(" [S] SALIR DEL SISTEMA 🚪")
        
        opcion = input("\n Seleccioná una sección: ").upper()

        if opcion == "1":
            # 1. Identificación
            estudiante = login_alumno() 
            
            if estudiante:
                # 2. Sintonización (Ver si hay clase para su curso)
                id_clase_hoy = obtener_clase_activa(estudiante.curso)
                
                # --- NUEVO: Consultamos el estado del feedback en la DB ---
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("SELECT feedback_visible FROM configuracion_clase WHERE id = 1")
                    res = cursor.fetchone()
                    conn.close()
                    # Si no hay datos, por defecto es 0 (bloqueado)
                    estado_feedback = res[0] if res else 0
                except:
                    estado_feedback = 0
                
                # 3. Lanzar Panel del Alumno
                # El dashboard devuelve "EXAMEN" o "LOGOUT"
                resultado = mostrar_dashboard(estudiante, id_clase_hoy, estado_feedback)
                
                if resultado == "EXAMEN":
                    print(f"\n📝 Iniciando Examen de la Clase {id_clase_hoy}...")
                    if id_clase_hoy:
                    # Lanzamos la lógica de preguntas y respuestas
                        ejecutar_examen(estudiante, id_clase_hoy)
                    # Después del examen, refrescamos el historial del objeto
                    # para que el próximo dashboard muestre la nota nueva
                        estudiante.sincronizar_historial()
                    else:
                        print("\n⚠️ No hay una clase activa asignada para tu curso hoy.")
                    input("\nPresioná Enter para volver al menú...")

        elif opcion == "2":
            # Acceso al Panel de Control (Pide clave adentro)
            panel_profesor()

        elif opcion == "S":
            print("\n👋 Saliendo del sistema. ¡Que tengas un buen día!")
            break
        else:
            print("\n❌ Opción no válida. Intentá de nuevo.")

#--------------------------------------------------------------------------------------------------------------------------
#podría poner directamente (y andaría)
#menu_principal()
#pero no es una buena práctica por varias razones que se pueden googlear

if __name__ == "__main__":
    menu_principal()
