import sqlite3
from config import conectar, ruta # Usamos la ruta vieja y la conexión nueva

def migrar():
    print("Iniciando migración...")
    # 1. Conectamos a la base local (el archivo .db del repo)
    local_conn = sqlite3.connect(ruta)
    
    # 2. Conectamos a Turso
    try:
        remote_conn = conectar()
        
        # 3. Leemos todo el contenido de tu base local
        for linea in local_conn.iterdump():
            # Ejecutamos cada línea (tablas, datos, índices) en Turso
            remote_conn.execute(linea)
            
        print("✅ ¡Éxito! Tu base de datos ahora está en la nube de Turso.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        local_conn.close()

if __name__ == "__main__":
    migrar()
