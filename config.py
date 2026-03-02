import libsql
import os

def conectar():
    # Esta librería es la recomendada para evitar errores de OSError en Streamlit
    conn = libsql.connect(
        database="https://astradb-juanmanuelborrego.aws-us-east-1.turso.io",
        auth_token="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzI0NjA5MTUsImlkIjoiMDE5Y2FlZTItZDgwMS03ZTg0LWFhNzAtOGFmMGE4YTYwMzk3IiwicmlkIjoiMWQ2NmE1ZDYtZGE1Mi00Y2VjLWI0MGEtMjg0ZDk3YWQ3YjFlIn0.rrSrgrFcgfFI4gw2tCyWBxIU0wv-PQ9RA5DBxsQjs3HLHXyg-yztr3isa5-pXiRxr_cy-E6hdohFfzPlx7t9Cw"
    )
    

ruta = "ad_astra.db"
