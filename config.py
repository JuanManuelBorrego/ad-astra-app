import libsql_client
import os

def conectar():
    # USAR create_client_sync es la clave para que exista el método .cursor()
    client = libsql_client.create_client_sync(
        url="libsql://astradb-juanmanuelborrego.aws-us-east-1.turso.io", 
        auth_token="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzI0NjA5MTUsImlkIjoiMDE5Y2FlZTItZDgwMS03ZTg0LWFhNzAtOGFmMGE4YTYwMzk3IiwicmlkIjoiMWQ2NmE1ZDYtZGE1Mi00Y2VjLWI0MGEtMjg0ZDk3YWQ3YjFlIn0.rrSrgrFcgfFI4gw2tCyWBxIU0wv-PQ9RA5DBxsQjs3HLHXyg-yztr3isa5-pXiRxr_cy-E6hdohFfzPlx7t9Cw"
    )
    # --- TRUCO DE COMPATIBILIDAD ---
    # Como el cliente de Turso no tiene .cursor(), se lo inventamos 
    # para que devuelva al propio cliente (que sí tiene .execute() y .fetchone())
    if not hasattr(client, "cursor"):
        client.cursor = lambda: client
    return client

ruta = "ad_astra.db"
