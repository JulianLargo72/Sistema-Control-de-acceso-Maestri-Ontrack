import mysql.connector
import os

# Configuración de la conexión a la base de datos MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="registros_qr"
)

def ejecutar_consulta_sql(query):
    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="registros_qr"
        )
        
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor()

        # Ejecutar la consulta
        cursor.execute(query)

        # Obtener los resultados de la consulta
        resultados = cursor.fetchall()

        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

        return resultados

    except mysql.connector.Error as error:
        print("Error al ejecutar la consulta SQL:", error)
        return None
    
def guardar_registro_en_mysql(identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango):
    cursor = mydb.cursor()
    sql = "INSERT INTO registros (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango)
    cursor.execute(sql, val)
    mydb.commit()
    cursor.close()
    
def guardar_registro_tercero_en_mysql(identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango):
    cursor = mydb.cursor()

    # Consultar los datos del externo basados en la identificación
    sql_externo_info = "SELECT compañia, motivo, dependencia, recibe, arl, equipo FROM externos WHERE identificacion = %s"
    cursor.execute(sql_externo_info, (identificacion,))
    externo_info = cursor.fetchone()

    # Si se encuentra información del externo, la guardamos en variables correspondientes
    if externo_info:
        compañia, motivo, dependencia, recibe, arl, equipo = externo_info
    else:
        # Si no se encuentra información del externo, establecemos valores predeterminados
        compañia, motivo, dependencia, recibe, arl, equipo = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

    # Insertar el registro en la tabla de tercero con los campos obtenidos y los datos recibidos como parámetros
    sql = "INSERT INTO tercero (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango, compañia, motivo, dependencia, recibe, arl, equipo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango, compañia, motivo, dependencia, recibe, arl, equipo)
    cursor.execute(sql, val)
    
    mydb.commit()
    cursor.close()

    
def insertar_externo(identificacion, nombre, area, correo, compañia, motivo, dependencia, recibe, arl, equipo, qr_path):
    cursor = mydb.cursor()
    sql = "INSERT INTO externos (identificacion, nombre, area, correo, compañia, motivo, dependencia, recibe, arl, equipo, qr_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (identificacion, nombre, area, correo, compañia, motivo, dependencia, recibe, arl, equipo, qr_path)
    cursor.execute(sql, val)
    mydb.commit()
    cursor.close()
    
def obtener_externos():
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM externos")
        id_externo = cursor.fetchall()
        return id_externo
    except mysql.connector.Error as error:
        print("Error al obtener usuarios de la base de datos:", error)
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
            
def obtener_externo_por_id(id_externo):
    try:
        cursor = mydb.cursor(dictionary=True)
        sql = "SELECT * FROM externos WHERE id = %s"
        cursor.execute(sql, (id_externo,))
        tercero_u = cursor.fetchone()
        return tercero_u
    except mysql.connector.Error as error:
        print("Error al obtener usuario de la base de datos:", error)
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
            
def borrar_externo(id_externo, qr_path):
    try:
        # Eliminar usuario de la base de datos
        cursor = mydb.cursor()
        sql = "DELETE FROM externos WHERE id = %s"
        cursor.execute(sql, (id_externo,))
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
    
def editar_externo(id_externo, identificacion, nombre, area, correo, compañia, motivo, dependencia, recibe, arl, equipo):
    try:
        cursor = mydb.cursor()
        sql = "UPDATE externos SET identificacion = %s, nombre = %s, area = %s, correo = %s, compañia = %s, motivo = %s, dependencia = %s, recibe = %s, arl = %s, equipo = %s WHERE id = %s"
        val = (identificacion, nombre, area, correo, compañia, motivo, dependencia, recibe, arl, equipo, id_externo)
        cursor.execute(sql, val)
        mydb.commit()
        print("Registro editado correctamente.")
    except mysql.connector.Error as error:
        print("Error al editar registro en la base de datos:", error)
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
            
def obtener_registros_entre_fechas(fecha_inicio, fecha_fin):
    try:
        cursor = mydb.cursor(dictionary=True)
        sql = "SELECT * FROM registros WHERE fecha BETWEEN %s AND %s"
        cursor.execute(sql, (fecha_inicio, fecha_fin))
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


def borrar_registro(id_registro):
    cursor = mydb.cursor()
    sql = "DELETE FROM registros WHERE id = %s"
    cursor.execute(sql, (id_registro,))
    mydb.commit()






def obtener_tercero():
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tercero")
        tercero = cursor.fetchall()
        return tercero
    except mysql.connector.Error as error:
        print("Error al obtener usuarios de la base de datos:", error)
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
            
def obtener_tercero_entre_fechas(fecha_inicio, fecha_fin):
    try:
        cursor = mydb.cursor(dictionary=True)
        sql = "SELECT * FROM tercero WHERE fecha BETWEEN %s AND %s"
        cursor.execute(sql, (fecha_inicio, fecha_fin))
        tercero = cursor.fetchall()
        return tercero
    except mysql.connector.Error as error:
        print("Error al obtener tercero de la base de datos:", error)
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
            
def editar_tercero(id_tercero, identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango):
    try:
        cursor = mydb.cursor()
        sql = "UPDATE tercero SET identificacion = %s, nombre = %s, area = %s, fecha = %s, hora_escaneo = %s, hora_entrada = %s, hora_salida = %s, rango = %s WHERE id = %s"
        val = (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango, id_tercero)
        cursor.execute(sql, val)
        mydb.commit()
        print("Tercero editado correctamente.")
    except mysql.connector.Error as error:
        print("Error al editar tercero en la base de datos:", error)
    finally:
        if 'cursor' in locals():
            cursor.close()
            
def obtener_tercero_por_id(id_tercero):
    try:
        cursor = mydb.cursor(dictionary=True)
        sql = "SELECT * FROM tercero WHERE id = %s"
        cursor.execute(sql, (id_tercero,))
        tercero = cursor.fetchone()
        return tercero
    except mysql.connector.Error as error:
        print("Error al obtener tercero de la base de datos:", error)
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()


def crear_tercero(identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango):
    try:
        cursor = mydb.cursor()
        sql = "INSERT INTO tercero (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango)
        cursor.execute(sql, val)
        mydb.commit()
        cursor.close()
        print("tercero creado exitosamente.")
        return True
    except mysql.connector.Error as error:
        print("Error al crear tercero en la base de datos:", error)
        return False


def borrar_tercero(id_tercero):
    cursor = mydb.cursor()
    sql = "DELETE FROM tercero WHERE id = %s"
    cursor.execute(sql, (id_tercero,))
    mydb.commit()