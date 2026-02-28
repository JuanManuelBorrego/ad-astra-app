import streamlit as st

# Mantenemos la variable ruta por compatibilidad, aunque sea un texto muerto
ruta = "App_V.0.1.db"

def get_connection():
    """
    Crea y devuelve la conexión a Supabase usando los Secrets de Streamlit.
    """
    # 'sql' es el motor de SQLAlchemy que entiende PostgreSQL
    return st.connection("postgresql", type="sql")
