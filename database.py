import mysql.connector

# Configuración de la conexión a la base de datos MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="registros_qr"
)

def guardar_registro_en_mysql(identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango):
    cursor = mydb.cursor()
    sql = "INSERT INTO registros (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango)
    cursor.execute(sql, val)
    mydb.commit()
    cursor.close()
    
def guardar_registro_tercero_en_mysql(identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango):
    cursor = mydb.cursor()
    sql = "INSERT INTO tercero (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango)
    cursor.execute(sql, val)
    mydb.commit()
    cursor.close()
    
    
