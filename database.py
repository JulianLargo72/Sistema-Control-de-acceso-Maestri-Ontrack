import mysql.connector
import os

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
    
def insertar_usuario(identificacion, nombre, area, correo, qr_path):
    cursor = mydb.cursor()
    sql = "INSERT INTO usuarios (identificacion, nombre, area, correo, qr_path) VALUES (%s, %s, %s, %s, %s)"
    val = (identificacion, nombre, area, correo, qr_path)
    cursor.execute(sql, val)
    mydb.commit()
    cursor.close()
    
def obtener_usuarios():
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        return usuarios
    except mysql.connector.Error as error:
        print("Error al obtener usuarios de la base de datos:", error)
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()

def obtener_usuario_por_id(id_usuario):
    try:
        cursor = mydb.cursor(dictionary=True)
        sql = "SELECT * FROM usuarios WHERE id = %s"
        cursor.execute(sql, (id_usuario,))
        usuario = cursor.fetchone()
        return usuario
    except mysql.connector.Error as error:
        print("Error al obtener usuario de la base de datos:", error)
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
            
def borrar_usuario(id_usuario, qr_path):
    try:
        # Eliminar usuario de la base de datos
        cursor = mydb.cursor()
        sql = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(sql, (id_usuario,))
        mydb.commit()
        
        # Eliminar imagen QR asociada
        if qr_path:
            # Construir la ruta completa del archivo QR
            ruta_qr = os.path.join(os.getcwd(), qr_path)
            # Verificar si el archivo existe y eliminarlo
            if os.path.exists(ruta_qr):
                os.remove(ruta_qr)
        
        print("Usuario y QR eliminados correctamente.")
    except mysql.connector.Error as error:
        print("Error al borrar usuario de la base de datos:", error)
    finally:
        if 'cursor' in locals():
            cursor.close()
    
def obtener_registros():
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM registros")
        registros = cursor.fetchall()
        return registros
    except mysql.connector.Error as error:
        print("Error al obtener usuarios de la base de datos:", error)
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
            
def obtener_registros_por_fecha(fecha):
    try:
        cursor = mydb.cursor(dictionary=True)
        sql = "SELECT * FROM registros WHERE fecha = %s"
        cursor.execute(sql, (fecha,))
        registros = cursor.fetchall()
        return registros
    except mysql.connector.Error as error:
        print("Error al obtener registros de la base de datos:", error)
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
            
def editar_registro(id_registro, identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango):
    try:
        cursor = mydb.cursor()
        sql = "UPDATE registros SET identificacion = %s, nombre = %s, area = %s, fecha = %s, hora_escaneo = %s, hora_entrada = %s, hora_salida = %s, rango = %s WHERE id = %s"
        val = (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango, id_registro)
        cursor.execute(sql, val)
        mydb.commit()
        print("Registro editado correctamente.")
    except mysql.connector.Error as error:
        print("Error al editar registro en la base de datos:", error)
    finally:
        if 'cursor' in locals():
            cursor.close()
            
def obtener_registro_por_id(id_registro):
    try:
        cursor = mydb.cursor(dictionary=True)
        sql = "SELECT * FROM registros WHERE id = %s"
        cursor.execute(sql, (id_registro,))
        registro = cursor.fetchone()
        return registro
    except mysql.connector.Error as error:
        print("Error al obtener registro de la base de datos:", error)
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()


def crear_registro(identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango):
    try:
        cursor = mydb.cursor()
        sql = "INSERT INTO registros (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango)
        cursor.execute(sql, val)
        mydb.commit()
        cursor.close()
        print("Registro creado exitosamente.")
        return True
    except mysql.connector.Error as error:
        print("Error al crear registro en la base de datos:", error)
        return False

