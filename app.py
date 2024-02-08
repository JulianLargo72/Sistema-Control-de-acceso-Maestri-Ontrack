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
from camera import generate_frames
from qr import generar_qr, enviar_correo
from excel import enviar_correo_excel
import database

app = Flask(__name__)
app.secret_key = 'maestri'

@app.route('/leer')
def mostrar_leer():
    return render_template('leer.html')

@app.route('/')
def inicio():
    return render_template('index.html')

areas = {
    'A': 'Administrativa',
    'G': 'Gerencial',
    'C': 'Comercial',
    'O': 'Operaciones',
    'T': 'Tercero'
}

@app.route('/generar', methods=['GET', 'POST'])
def generar():
    if request.method == 'POST':
        try:
            prefijo = request.form['prefijo']
            if not prefijo.isalpha():
                raise ValueError("El prefijo debe contener solo letras.")
            
            identificacion = int(request.form['identificacion'])
            nombre = request.form['nombre']
            qr_path, info_completa = generar_qr(prefijo, identificacion, nombre)

            # Verificar si el campo de correo está presente en el formulario
            destinatario = request.form.get('correo', '')  # Si no se proporciona, el valor será una cadena vacía

            # Verificar si el prefijo está en el diccionario de áreas
            area = areas.get(prefijo)
            if area:
                mensaje = f"QR generado para la identificación: {identificacion}, nombre: {nombre} y con un vinculo con la empresa de: {area}."
            else:
                mensaje = f"QR generado para la identificación: {identificacion} y el nombre: {nombre}."
                
            # Insertar datos en la tabla usuarios
            database.insertar_usuario(identificacion, nombre, area, destinatario, qr_path)
            
            # Enviar el correo electrónico solo si se proporciona el correo
            if destinatario:
                enviar_correo(destinatario, "Codigo QR control de acceso Maestri Ontrack", f" Cordial saludo:\n\nTe informamos que el QR generado con la siguiente informacion ha sido registrado con exito!\n\nNombre: {nombre}\nVinculo: {area}\n Identificación: {identificacion}\n\nA continuacion adjuntamos el codigo", qr_path)

            if destinatario:
                mensaje += f" Se ha enviado al correo: {destinatario}."
            return render_template('generar.html', mensaje=mensaje, qr_path=qr_path)
        except ValueError as e:
            mensaje = str(e)
            return render_template('generar.html', mensaje=mensaje)
    return render_template('generar.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/registros', methods=['GET'])
def mostrar_registros():
    fecha_filtro = request.args.get('fecha', datetime.today().strftime('%Y-%m-%d'))
    carpeta_registros = 'registros_excel'
    
    registros = []

    for archivo_excel in os.listdir(carpeta_registros):
        ruta_archivo_excel = os.path.join(carpeta_registros, archivo_excel)

        try:
            wb = xl.load_workbook(ruta_archivo_excel)
            hoja_actual = wb['Actual']

            for row in hoja_actual.iter_rows(min_row=2, values_only=True):
                registro = {
                    'Id': row[0],
                    'Identificacion': row[1],
                    'Nombre': row[2],
                    'Area': row[3],
                    'Fecha': row[4],
                    'Hora': row[5],
                    'Entrada': row[6],
                    'Salida': row[7],
                    'Rango': row[8]
                }

                # Filtra los registros por fecha si se proporciona una fecha de filtro
                if fecha_filtro:
                    if registro['Fecha'] == fecha_filtro:
                        registros.append(registro)
                else:
                    registros.append(registro)

        except Exception as e:
            print(f"Error al procesar el archivo {archivo_excel}: {e}")

    return render_template('registros.html', registros=registros, fecha_actual=datetime.today().strftime('%Y-%m-%d'))

@app.route('/enviar_excel', methods=['GET', 'POST'])
def enviar_excel():
    carpeta_registros = 'registros_excel'
    fecha_filtro = datetime.today().strftime('%Y-%m-%d')
    registros = []  # Inicializa la variable registros aquí

    if request.method == 'GET':
        fecha_filtro = request.args.get('fecha', fecha_filtro)

        try:
            archivos_excel = [archivo for archivo in os.listdir(carpeta_registros) if archivo.endswith('.xlsx')]
        except FileNotFoundError:
            flash('No se encontraron archivos de registro.')
            return render_template('enviar_correo.html', registros=registros, fecha_actual=datetime.today().strftime('%Y-%m-%d'))

        for archivo_excel in archivos_excel:
            ruta_archivo_excel = os.path.join(carpeta_registros, archivo_excel)

            try:
                wb = xl.load_workbook(ruta_archivo_excel)
                hoja_actual = wb['Actual']

                for row in hoja_actual.iter_rows(min_row=2, values_only=True):
                    registro = {
                        'Identificacion': row[0],
                        'Nombre': row[1],
                        'Area': row[2],
                        'Fecha': row[3],
                        'Hora': row[4],
                        'Entrada': row[5],
                        'Salida': row[6],
                        'Rango': row[7]
                    }

                    if fecha_filtro:
                        if registro['Fecha'] == fecha_filtro:
                            registros.append(registro)
                    else:
                        registros.append(registro)

            except Exception as e:
                print(f"Error al procesar el archivo {archivo_excel}: {e}")

        return render_template('enviar_correo.html', registros=registros, fecha_actual=datetime.today().strftime('%Y-%m-%d'))

    elif request.method == 'POST':
        correo_destinatario = request.form.get('correo_destinatario')
        fecha_filtro = request.form.get('fecha', fecha_filtro)

        archivo_a_enviar = os.path.join(carpeta_registros, f'{fecha_filtro}.xlsx')

        try:
            enviar_correo_excel(correo_destinatario, 'Archivo Control de Acceso', f"Cordial saludo,\n\nA continuacion adjuntamos el archivo de control de acceso correspondiente al registro de la fecha {fecha_filtro}", archivo_a_enviar)
            flash('Correo enviado exitosamente.', 'success')  # Agrega la alerta de éxito
        except FileNotFoundError:
            flash('El archivo de registro no se encontró.')
            return redirect(url_for('enviar_excel'))

        # Devuelve la plantilla con la fecha actual y la alerta de éxito
        return render_template('enviar_correo.html', registros=[], fecha_actual=datetime.today().strftime('%Y-%m-%d'))
    
@app.route('/usuarios')
def mostrar_usuarios():
    usuarios = database.obtener_usuarios()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/ver_usuario/<int:id_usuario>')
def ver_usuario(id_usuario):
    usuario = database.obtener_usuario_por_id(id_usuario)
    if usuario:
        return render_template('detalles_usuario.html', usuario=usuario)
    else:
        return "Usuario no encontrado"
    
@app.route('/eliminar_usuario/<int:id_usuario>')
def eliminar_usuario(id_usuario):
    # Obtener el usuario por su ID
    usuario = database.obtener_usuario_por_id(id_usuario)

    if usuario:
        # Llamar a la función para borrar el usuario y la imagen QR
        database.borrar_usuario(id_usuario, usuario['qr_path'])
        # Redirigir a la página de lista de usuarios
        return redirect(url_for('mostrar_usuarios'))
    else:
        return "Usuario no encontrado"

if __name__ == '__main__':
    app.run(host='192.168.0.44', port=5000, debug=True)
