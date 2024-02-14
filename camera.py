import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import os
from flask import Flask, render_template, url_for, flash, request, redirect, Response
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from datetime import datetime
import openpyxl as xl
import time
import pyqrcode
import database 

mañana = []
tiempo_ultima_registro = {}

# Diccionario para mapear el primer carácter al área correspondiente
areas = {
    'A': 'Administrativa',
    'G': 'Gerencial',
    'C': 'Comercial',
    'O': 'Operaciones',
    'T': 'Tercero'
}


def obtener_area(codigo):
    primer_caracter = codigo[0]
    return areas.get(primer_caracter, 'Desconocida')

def infhora():
    inf = datetime.now()
    fecha = inf.strftime('%Y-%m-%d')
    hora = inf.strftime('%H:%M:%S')
    return hora, fecha

def obtener_rango(hora_actual):
    hora_entrada = datetime.strptime(hora_actual, '%H:%M:%S')
    if datetime.strptime('07:00:00', '%H:%M:%S') <= hora_entrada <= datetime.strptime('09:00:00', '%H:%M:%S'):
        return 'Entrada AM'
    elif datetime.strptime('11:30:00', '%H:%M:%S') <= hora_entrada <= datetime.strptime('12:30:00', '%H:%M:%S'):
        return 'Salida AM'
    elif datetime.strptime('12:30:00', '%H:%M:%S') <= hora_entrada <= datetime.strptime('14:30:00', '%H:%M:%S'):
        return 'Entrada PM'
    elif datetime.strptime('16:30:00', '%H:%M:%S') <= hora_entrada <= datetime.strptime('19:00:00', '%H:%M:%S'):
        return 'Salida PM'
    else:
        return 'Revisar'

def obtener_hora_entrada_desde_db(identificacion):
    # Obtener la fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d')

    # Consulta SQL para obtener la hora de entrada desde la tabla registros
    query_registros = f"SELECT hora_entrada FROM registros WHERE identificacion = '{identificacion}' AND fecha = '{fecha_actual}' ORDER BY id ASC LIMIT 1"

    # Ejecutar la consulta y obtener los resultados de registros
    resultados_registros = database.ejecutar_consulta_sql(query_registros)

    # Si hay resultados en la tabla registros, retornar la hora de entrada encontrada
    if resultados_registros:
        hora_entrada = resultados_registros[0][0]
        return hora_entrada

    # Si no hay resultados en la tabla registros, consultar la tabla tercero para obtener la hora de entrada
    else:
        # Consulta SQL para obtener la hora de entrada desde la tabla tercero
        query_externo = f"SELECT hora_entrada FROM tercero WHERE identificacion = '{identificacion}'"

        # Ejecutar la consulta y obtener los resultados de tercero
        resultados_externo = database.ejecutar_consulta_sql(query_externo)

        # Si hay resultados en la tabla tercero, retornar la hora de entrada encontrada
        if resultados_externo:
            hora_entrada = resultados_externo[0][0]
            return hora_entrada

        # Si no hay resultados en la tabla externo, retornar la hora actual
        else:
            return datetime.now().strftime('%H:%M:%S')

    
def codigo_existe_en_tercero_o_usuario(codigo):
    query_usuarios = f"SELECT COUNT(*) FROM usuarios WHERE identificacion = '{codigo}'"
    query_externos = f"SELECT COUNT(*) FROM externos WHERE identificacion = '{codigo}'"

    resultado_usuarios = database.ejecutar_consulta_sql(query_usuarios)
    resultado_terceros = database.ejecutar_consulta_sql(query_externos)

    return (resultado_usuarios[0][0] > 0) or (resultado_terceros[0][0] > 0)




def generate_frames():
    cap = cv2.VideoCapture(1)
    while True:
        ret, frame = cap.read()
        
        # INTERFAZ
        # Texto
        cv2.putText(frame, 'Ubica el QR code', (160, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Ubicanos el rectangulo en las zonas
        cv2.rectangle(frame, (170, 100), (470, 400), (0, 255, 0), 2)

        hora, fecha = infhora()
        diasem = datetime.today().weekday()

        a, me, d = fecha[0:4], fecha[5:7], fecha[8:10]
        h, m, s = int(hora[0:2]), int(hora[3:5]), int(hora[6:8])

        # Obtener la hora actual
        hora_actual = datetime.now().time()

        # Formatear la hora, minutos y segundos con dos dígitos
        texth = hora_actual.strftime('%H:%M:%S')
        print(texth)

        for codes in decode(frame):
                info = codes.data.decode('utf-8')
                tipo = int(info[0:2])
                letr = chr(tipo)
                num = info[2:]
                nombre = info.split('-')[1].strip()
                pts = np.array([codes.polygon], np.int32)
                xi, yi = codes.rect.left, codes.rect.top
                pts = pts.reshape((-1, 1, 2))
                codigo = letr + num
                
                # Imprimir el valor del código QR en la consola
                print("Valor del código QR:", codigo)

                if 6 >= diasem >= 0:
                    cv2.polylines(frame, [pts], True, (255, 255, 0), 5)

                    # Obtener el área correspondiente al primer carácter del código
                    area = obtener_area(codigo)

                    codigo_despues_del_primer_digito = info.split('-')[0][2:].strip()

                    # Verificar si el código existe en la base de datos de usuarios
                    if not codigo_existe_en_tercero_o_usuario(codigo_despues_del_primer_digito):
                        # Si no existe, mostrar mensaje de error y continuar con el siguiente código
                        cv2.putText(frame, f"Usuario no registrado", (xi - 65, yi - 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.putText(frame, "Registro Fallido", (xi - 65, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        continue

                    # Si el código está en la lista "mañana" y el tiempo desde el último registro es menor o igual a 60 segundos,
                    # muestra un mensaje de éxito y continúa con el siguiente código.
                    if codigo in mañana and time.time() - tiempo_ultima_registro.get(codigo, 0) <= 60:
                        cv2.putText(frame, f"El ID {codigo}", (xi - 65, yi - 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        cv2.putText(frame, "Registro Exitoso", (xi - 65, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        print(mañana)
                        continue

                    # Si llega a este punto, es un nuevo registro válido, entonces lo agregamos a "mañana" y actualizamos el tiempo del último registro.
                    mañana.append(codigo)
                    tiempo_ultima_registro[codigo] = time.time()

                    # Buscar la hora de entrada en la base de datos
                    hora_entrada = obtener_hora_entrada_desde_db(codigo_despues_del_primer_digito)

                    if area != 'Tercero':
                        # Guardar el registro en la base de datos MySQL
                        database.guardar_registro_en_mysql(codigo_despues_del_primer_digito, nombre, area, fecha, texth, hora_entrada, time.strftime("%H:%M:%S"), obtener_rango(hora_actual.strftime('%H:%M:%S')))
                    else:
                        # Guardar el registro en la tabla de terceros en la base de datos MySQL
                        database.guardar_registro_tercero_en_mysql(codigo_despues_del_primer_digito, nombre, area, fecha, texth, hora_entrada, time.strftime("%H:%M:%S"))

                    cv2.putText(frame, f"{letr}0{num}", (xi - 15, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 55, 0), 2)
                    print("El usuario pertenece a la empresa \nNúmero de Identificación:", codigo, "Fecha de registro:", fecha, "Hora de registro:", texth)

                elif codigo in mañana:
                    cv2.putText(frame, f"El ID {codigo}", (xi - 65, yi - 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    cv2.putText(frame, "Registro Exitoso", (xi - 65, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    print(mañana)

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
