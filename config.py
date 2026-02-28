import streamlit as st
import re

# Mantenemos esto para que tus otros archivos no den error al importar
ruta = "App_V.0.1.db"

def get_connection():
    """Conexión base a Supabase"""
    return st.connection("postgresql", type="sql")

def ejecutar_sql(query, params=None):
    """
    TRADUCTOR AUTOMÁTICO: 
    Recibe queries con '?' (estilo SQLite) y las convierte 
    al formato ':p1' (estilo PostgreSQL/Supabase).
    """
    conn = get_connection()
    
    if params:
        # 1. Convertimos los '?' en ':p1', ':p2', etc.
        count = 1
        new_query = query
        while '?' in new_query:
            new_query = new_query.replace('?', f':p{count}', 1)
            count += 1
        
        # 2. Convertimos la tupla de parámetros en un diccionario
        # Ejemplo: (1, 'Juan') -> {'p1': 1, 'p2': 'Juan'}
        if isinstance(params, (list, tuple)):
            new_params = {f'p{i+1}': v for i, v in enumerate(params)}
        else:
            # Por si viene un solo valor suelto
            new_params = {'p1': params}
            
        # 3. Ejecutamos en Supabase
        return conn.query(new_query, params=new_params, ttl="0")
    else:
        return conn.query(query, ttl="0")
