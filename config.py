import streamlit as st
import re
import libsql_client
import os

# 1. Datos de Turso
TURSO_URL = "tu_url_de_turso"
TURSO_TOKEN = "tu-token-seguro"

# 2. VARIABLE RUTA (Mantenela para evitar el ImportError)
# Poné el nombre de tu archivo .db viejo. No se va a usar, pero evita que la app explote.
ruta = "ad_astra.db" 

def conectar():
    return libsql_client.create_client_sync(
        url="libsql://astradb-juanmanuelborrego.aws-us-east-1.turso.io" , 
        auth_token="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzI0NjA5MTUsImlkIjoiMDE5Y2FlZTItZDgwMS03ZTg0LWFhNzAtOGFmMGE4YTYwMzk3IiwicmlkIjoiMWQ2NmE1ZDYtZGE1Mi00Y2VjLWI0MGEtMjg0ZDk3YWQ3YjFlIn0.rrSrgrFcgfFI4gw2tCyWBxIU0wv-PQ9RA5DBxsQjs3HLHXyg-yztr3isa5-pXiRxr_cy-E6hdohFfzPlx7t9Cw"
    )
