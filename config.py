import streamlit as st

# En la nube no usamos rutas de archivos, usamos la conexión de Secrets
def get_db_connection():
    try:
        # Esto busca automáticamente la URL que pegaste en los Secrets de Streamlit
        conn = st.connection("database", type="sql")
        return conn
    except Exception as e:
        st.error(f"Error de conexión a la base de datos: {e}")
        return None

# Mantenemos esta variable por compatibilidad con tus archivos viejos
# pero ahora la apuntamos a la conexión de Streamlit
ruta = "database"
