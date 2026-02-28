from config import ejecutar_sql
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class Alumno:
    def __init__(self, id_alumno, nombre, curso):
        self.id = id_alumno
        self.nombre = nombre
        self.curso = curso
        self.historial = {} 

    # 1. MÉTODO: ESTADO DEL EXAMEN (Saneado)
    def clase_esta_activa(self):
        """Consulta si el profesor mantiene el examen habilitado."""
        try:
            # Usamos ejecutar_sql en lugar de sqlite3
            resultado = ejecutar_sql("SELECT examen_activo FROM configuracion_clase WHERE id = 1")
            if not resultado.empty:
                return resultado.iloc[0]['examen_activo'] == 1
            return False
        except:
            return False

    # 2. MÉTODO: REGISTRAR CLASE (Saneado y con la regla del 1.0)
    def registrar_clase(self, id_clase, completados, correctos, nota_oral=None):
        # A. Buscamos el total de preguntas real
        res_preguntas = ejecutar_sql("SELECT COUNT(*) as total FROM preguntas WHERE id_clase = %s", (id_clase,))
        totales_reales = int(res_preguntas.iloc[0]['total']) if not res_preguntas.empty else 0
        
        if totales_reales == 0:
            return None
        
        # B. Sincronizamos la tabla clases
        ejecutar_sql("UPDATE clases SET ejercicios_totales = %s WHERE id_clase = %s", (totales_reales, id_clase))
        
        # C. Lógica de Esfuerzo y Eficacia
        esfuerzo = completados / totales_reales
        
        if completados > 0:
            eficacia = correctos / completados
        else:
            eficacia = 0
            # REGLA 21/02: Si no hizo nada, forzamos nota 1.0
            if nota_oral is None:
                self.historial[id_clase] = {"esfuerzo": 0, "eficacia": 0, "nota_oral": None, "nota_final": 1.0}
                ejecutar_sql("""
                    INSERT INTO reportes_diarios (id_alumno, id_clase, ejercicios_completados, ejercicios_correctos, nota_final)
                    VALUES (%s, %s, 0, 0, 1.0)
                """, (self.id, id_clase))
                return 1.0

        # D. Cálculo de nota final
        nota_final = float(nota_oral) if nota_oral is not None else round(((esfuerzo + eficacia) / 2) * 10, 2)
        
        # E. Guardar en memoria y en Supabase
        self.historial[id_clase] = {
            "esfuerzo": esfuerzo, "eficacia": eficacia, "nota_oral": nota_oral, "nota_final": nota_final
        }
        
        ejecutar_sql("""
            INSERT INTO reportes_diarios (id_alumno, id_clase, ejercicios_completados, ejercicios_correctos, nota_oral, nota_final)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (self.id, id_clase, completados, correctos, nota_oral, nota_final))
        
        return nota_final

    # 3. MÉTODO: SINCRONIZAR HISTORIAL (Ya lo tenías bien, lo mantengo)
    def sincronizar_historial(self):
        query = """
            SELECT r.id_clase, r.ejercicios_completados, r.ejercicios_correctos, 
                   r.nota_final, r.nota_oral, c.ejercicios_totales
            FROM reportes_diarios r
            JOIN clases c ON r.id_clase = c.id_clase
            WHERE r.id_alumno = %s
        """
        df_historial = ejecutar_sql(query, (self.id,))

        if not df_historial.empty:
            for _, f in df_historial.iterrows():
                id_clase_f = int(f['id_clase'])
                comp = f['ejercicios_completados'] if pd.notnull(f['ejercicios_completados']) else 0
                corr = f['ejercicios_correctos'] if pd.notnull(f['ejercicios_correctos']) else 0
                tot = f['ejercicios_totales']
            
                val_esf = (comp / tot * 100) if tot > 0 else 0
                val_efi = (corr / comp * 100) if comp > 0 else 0
                    
                self.historial[id_clase_f] = {
                    "esfuerzo": val_esf, "eficacia": val_efi,
                    "nota_final": f['nota_final'], "nota_oral": f['nota_oral']
                }

    # 4. MÉTODOS DE CÁLCULO (Promedio y Tendencia - Sin cambios necesarios)
    def promedio(self):    
        notas = [n["nota_final"] for n in self.historial.values() if n["nota_final"] is not None]
        return round(sum(notas) / len(notas), 2) if notas else 'no hay cargas todavía'

    def interpretar_tendencia(self, m_eficacia, m_esfuerzo):
        data = self.calcular_nota_trimestral(m_esfuerzo, m_eficacia)
        if isinstance(data, str): return "⚪ Sin notas suficientes."
        
        nota_proy = data['total_entero']
        # (Aquí va tu lógica de semáforos que ya tenías)
        return f"Nota Proyectada: {nota_proy}. (Análisis de tendencia activo)"

    def calcular_nota_trimestral(self, m1_esfuerzo, m2_eficacia):
        p = self.promedio()
        if isinstance(p, str): return p
        adj_esf = 0.5 if m1_esfuerzo > 0.3 else (-0.5 if m1_esfuerzo < -0.3 else 0)
        adj_efi = 0.5 if m2_eficacia > 0.3 else (-0.5 if m2_eficacia < -0.3 else 0)
        nota_dec = max(1.0, min(10.0, p + adj_esf + adj_efi))
        return {"total_decimal": round(nota_dec, 2), "total_entero": int(round(nota_dec))}

    # 5. MÉTODO: GRÁFICOS (Sin cambios, usa los datos de la memoria)
    def graficar_tendencia(self):
        if len(self.historial) < 2: return "Faltan datos."
        ids = sorted(self.historial.keys())
        x = np.arange(len(ids))
        y_esf = np.array([self.historial[i]['esfuerzo'] for i in ids])
        y_efi = np.array([self.historial[i]['eficacia'] for i in ids])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        # ... (Tu lógica de Matplotlib se mantiene igual)
        m1, b1 = np.polyfit(x, y_esf, 1)
        m2, b2 = np.polyfit(x, y_efi, 1)
        return m1, m2


