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

# Especificar el nombre de la nueva carpeta para los registros de Excel
nombre_carpeta_registros = 'registros_excel'

# Crear la carpeta si no existe
if not os.path.exists(nombre_carpeta_registros):
    os.makedirs(nombre_carpeta_registros)

def obtener_ruta_archivo_excel():
    hora, fecha_actual = infhora()
    ruta_archivo_excel = os.path.join(nombre_carpeta_registros, f"{fecha_actual}.xlsx")
    return ruta_archivo_excel

def obtener_o_crear_hoja_excel(ruta_archivo_excel):
    try:
        wb = xl.load_workbook(ruta_archivo_excel)
        hojam = wb["Actual"]
    except FileNotFoundError:
        wb = xl.Workbook()
        hojam = wb.create_sheet("Actual")
        hojam.append(["Documento", "Nombre", "Area", "Fecha", "Hora Escaneo", "Hora Entrada", "Hora Salida", "Rango"])  # Encabezados
        wb.save(ruta_archivo_excel)
    return wb, hojam

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

        ruta_archivo_excel = obtener_ruta_archivo_excel()
        wb, hojam = obtener_o_crear_hoja_excel(ruta_archivo_excel)

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

                    if codigo not in mañana or (codigo in mañana and time.time() - tiempo_ultima_registro.get(codigo, 0) > 60):
                        mañana.append(codigo)
                        tiempo_ultima_registro[codigo] = time.time()

                        # Obtener el área correspondiente al primer carácter del código
                        area = obtener_area(codigo)

                        codigo_despues_del_primer_digito = info.split('-')[0][2:].strip()

                        # Buscar la hora de entrada en el archivo de Excel
                        hora_entrada = None
                        for row in hojam.iter_rows(min_row=2, max_col=6, max_row=hojam.max_row):
                            if row[0].value == codigo_despues_del_primer_digito:
                                # Verificar que la tupla tenga suficientes elementos antes de intentar acceder al índice 5
                                if len(row) > 5:
                                    hora_entrada = row[5].value
                                break

                        if hora_entrada is None:
                            # Si no se encuentra la hora de entrada, usar la hora actual
                            hora_entrada = time.strftime("%H:%M:%S", time.localtime())

                        # Agregar la fila al archivo de Excel con código, nombre, área, fecha, hora de entrada y hora de salida
                        rango = obtener_rango(hora_actual.strftime('%H:%M:%S'))
                        hojam.append([codigo_despues_del_primer_digito, nombre, area, fecha, texth, hora_entrada, time.strftime("%H:%M:%S"), rango])

                        # Guardar los cambios en el archivo de Excel
                        wb.save(ruta_archivo_excel)

                        if area != 'Tercero':
                            # Guardar el registro en la base de datos MySQL
                            database.guardar_registro_en_mysql(codigo_despues_del_primer_digito, nombre, area, fecha, texth, hora_entrada, time.strftime("%H:%M:%S"), rango)
                        else:
                            # Guardar el registro en la tabla de terceros en la base de datos MySQL
                            database.guardar_registro_tercero_en_mysql(codigo_despues_del_primer_digito, nombre, area, fecha, texth, hora_entrada, time.strftime("%H:%M:%S"), rango)

                        cv2.putText(frame, f"{letr}0{num}", (xi - 15, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 55, 0), 2)
                        print("El usuario es accionista de la empresa \nNúmero de Identificación:", codigo, "Fecha de registro:", fecha, "Hora de registro:", texth)

                    elif codigo in mañana:
                        cv2.putText(frame, f"El ID {codigo}", (xi - 65, yi - 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        cv2.putText(frame, "Registro Exitoso", (xi - 65, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        print(mañana)

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')