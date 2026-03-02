import libsql_client
import os

TURSO_URL = "libsql://tu-base.turso.io"
TURSO_TOKEN = "tu-token"
ruta = "ad_astra.db" 

def conectar():
    # USAR create_client_sync es la clave para que exista el método .cursor()
    client = libsql_client.create_client_sync(
        url="libsql://astradb-juanmanuelborrego.aws-us-east-1.turso.io", 
        auth_token="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzI0NjA5MTUsImlkIjoiMDE5Y2FlZTItZDgwMS03ZTg0LWFhNzAtOGFmMGE4YTYwMzk3IiwicmlkIjoiMWQ2NmE1ZDYtZGE1Mi00Y2VjLWI0MGEtMjg0ZDk3YWQ3YjFlIn0.rrSrgrFcgfFI4gw2tCyWBxIU0wv-PQ9RA5DBxsQjs3HLHXyg-yztr3isa5-pXiRxr_cy-E6hdohFfzPlx7t9Cw"
    )
    return client
