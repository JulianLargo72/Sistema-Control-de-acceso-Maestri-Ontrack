import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import os
from flask import Flask, render_template, url_for, flash, request, redirect, Response, send_file
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from datetime import datetime, timedelta
import openpyxl as xl
import time
import pyqrcode
from camera import generate_frames
from qr import generar_qr, enviar_correo
import database
import pandas as pd
from io import BytesIO


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
    
@app.route('/registros_bd')
def mostrar_registros_bd():
    registros = database.obtener_registros()
    return render_template('registros_bd.html', registros=registros)

@app.route('/filtrar_registros', methods=['GET'])
def filtrar_registros():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio:
        fecha_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')

    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')

    registros_filtrados = database.obtener_registros_entre_fechas(fecha_inicio, fecha_fin)
    
    if request.args.get('exportar') == 'True':
        df = pd.DataFrame(registros_filtrados)

        # Crear el nombre del archivo con el formato deseado
        nombre_archivo = f"{fecha_inicio.strftime('%Y-%m-%d')} - {fecha_fin.strftime('%Y-%m-%d')}.xlsx"

        # Forzar la descarga del archivo de Excel desde memoria
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return send_file(excel_buffer, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name=nombre_archivo)


    return render_template('registros_bd.html', registros=registros_filtrados, fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'), fecha_fin=fecha_fin.strftime('%Y-%m-%d'))

@app.route('/crear_registro', methods=['GET', 'POST'])
def crear_registro():
    if request.method == 'POST':
        identificacion = request.form['identificacion']
        nombre = request.form['nombre']
        area = request.form['area']
        fecha = request.form['fecha']
        hora_escaneo = request.form['hora_escaneo']
        hora_entrada = request.form['hora_entrada']
        hora_salida = request.form['hora_salida']
        rango = request.form['rango']
        if database.crear_registro(identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango):
            # Redirige a una página exitosa si la creación del registro fue exitosa
            return redirect(url_for('mostrar_registros_bd'))
        else:
            # Redirige a una página de error si la creación del registro falló
            return redirect(url_for('crear_registro'))
    else:
        # Obtener la lista de usuarios desde la base de datos
        usuarios = database.obtener_usuarios()
        # Renderizar la vista HTML para crear un nuevo registro, pasando la lista de usuarios al template
        return render_template('crear_registro.html', usuarios=usuarios)


@app.route('/editar_registro/<int:id_registro>', methods=['GET', 'POST'])
def editar_registro(id_registro):
    if request.method == 'POST':
        # Obtener los datos del formulario de edición
        identificacion = request.form['identificacion']
        nombre = request.form['nombre']
        area = request.form['area']
        fecha = request.form['fecha']
        hora_escaneo = request.form['hora_escaneo']
        hora_entrada = request.form['hora_entrada']
        hora_salida = request.form['hora_salida']
        rango = request.form['rango']

        # Llamar a la función para editar el registro en la base de datos
        database.editar_registro(id_registro, identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, rango)

        # Redireccionar a la página de lista de registros después de la edición
        return redirect(url_for('mostrar_registros_bd'))
    else:
        # Obtener el registro a editar de la base de datos
        registro = database.obtener_registro_por_id(id_registro)
        usuarios = database.obtener_usuarios()
        return render_template('editar_registro.html', registro=registro, usuarios=usuarios)

@app.route('/borrar_registro/<int:id_registro>', methods=['GET', 'POST'])
def borrar_registro_route(id_registro):
    if request.method == 'POST':
        database.borrar_registro(id_registro)
        return redirect(url_for('mostrar_registros_bd'))
    else:
        return "Método no permitido", 405


if __name__ == '__main__':
    app.run(host='192.168.0.44', port=5000, debug=True)
