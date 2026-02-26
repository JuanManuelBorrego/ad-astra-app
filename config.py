import os

# Buscamos la carpeta donde vive este archivo y le sumamos el nombre de la DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(BASE_DIR, 'App_V.0.1.db')
