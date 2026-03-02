import libsql_client
import os

TURSO_URL = "libsql://tu-base.turso.io"
TURSO_TOKEN = "tu-token"
ruta = "ad_astra.db" 

def conectar():
    # USAR create_client_sync es la clave para que exista el método .cursor()
    client = libsql_client.create_client_sync(
        url=TURSO_URL, 
        auth_token=TURSO_TOKEN
    )
    return client
