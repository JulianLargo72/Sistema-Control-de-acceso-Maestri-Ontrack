import mysql.connector

# Configuración de la conexión a la base de datos MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="registros_qr"
)
