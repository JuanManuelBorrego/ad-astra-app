import streamlit as st
import re
import libsql_client
import os

# Estos datos los sacás de la web de Turso (panel de control)
TURSO_URL = "libsql://tu-base-de-datos.turso.io"
TURSO_TOKEN = "tu-token-seguro"

def conectar():
    # Esta función reemplaza a sqlite3.connect(ruta)
    # Devuelve un objeto compatible con todos tus .execute(), .commit() y .close()
    return libsql_client.create_client_sync(
        url=TURSO_URL, 
        auth_token=TURSO_TOKEN
    )

