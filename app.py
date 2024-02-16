import functools
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import os
from flask import Flask, render_template, url_for, flash, request, redirect, Response, send_file, session, Blueprint
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
login_blueprint = Blueprint('login', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'logueado' not in session or not session['logueado']:
            return redirect(url_for('login_route'))
        return view(**kwargs)
    return wrapped_view

@app.route('/leer')
@login_required
def mostrar_leer():
    return render_template('leer.html')

@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

areas = {
    'A': 'Administrativa',
    'G': 'Gerencial',
    'C': 'Comercial',
    'O': 'Operaciones',
    'T': 'Tercero'
}

@app.route('/acceso-login', methods=["GET", "POST"])
def login_route():
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        # Consulta SQL parametrizada
        query = 'SELECT * FROM login WHERE correo = %s AND password = %s'
        params = (_correo, _password)

        # Llama a la función login para ejecutar la consulta
        accounts = database.login(query, params)

        if accounts:
            session['logueado'] = True
            session['id'] = accounts[0]['id']
            return render_template("index.html")
        else:
            flash('Usuario o contraseña incorrectas', 'error')  # Mensaje de error usando flash
            return render_template('login.html')
            
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar():
    if request.method == 'POST':
        correo = request.form['txtcorreo']
        contraseña = request.form['password']
        
        # Insertar en la base de datos
        database.insertar_en_base_de_datos(correo, contraseña)
        
        # Mensaje de éxito
        flash('¡Registro exitoso!', 'success')
        
        # Redireccionar a la página de inicio
        return redirect(url_for('index'))
    
    return render_template('registro.html')


@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()  # Elimina todas las variables de sesión
    return redirect(url_for('login_route'))  # Redirige al usuario a la página de inicio de sesión o a la página principal

@app.route('/generar', methods=['GET', 'POST'])
@login_required
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
                mensaje = f"QR generado para la identificación: {identificacion}, nombre: {nombre} y pertenece al area de: {area}."
            else:
                mensaje = f"QR generado para la identificación: {identificacion} y el nombre: {nombre}."
                
            # Insertar datos en la tabla usuarios
            database.insertar_usuario(identificacion, nombre, area, destinatario, qr_path)
            
            # Enviar el correo electrónico solo si se proporciona el correo
            if destinatario:
                enviar_correo(destinatario, "Codigo QR control de acceso Maestri Ontrack", f" Cordial saludo:\n\nTe informamos que el QR generado con la siguiente informacion ha sido registrado con exito!\n\nNombre: {nombre}\nArea: {area}\nIdentificación: {identificacion}\n\nA continuacion adjuntamos el codigo", qr_path)

            if destinatario:
                mensaje += f" Se ha enviado al correo: {destinatario}."
                flash('QR generado correctamente', 'success')
            return render_template('generar.html', mensaje=mensaje, qr_path=qr_path)
        except ValueError as e:
            mensaje = str(e)
            return render_template('generar.html', mensaje=mensaje)
    return render_template('generar.html')

@app.route('/generar_externo', methods=['GET', 'POST'])
@login_required
def generar_externo():
    if request.method == 'POST':
        try:
            prefijo = request.form['prefijo']
            if not prefijo.isalpha():
                raise ValueError("El prefijo debe contener solo letras.")
            
            identificacion = int(request.form['identificacion'])
            nombre = request.form['nombre']
            
            destinatario = request.form.get('correo', '')
            compañia = request.form['compañia']
            motivo = request.form['motivo']
            dependencia = request.form['dependencia']
            recibe = request.form['recibe']
            arl = request.form['arl']
            equipo = request.form['equipo']
            qr_path, info_completa = generar_qr(prefijo, identificacion, nombre)
            
            # Verificar si el prefijo está en el diccionario de áreas
            area = areas.get(prefijo)
            
            mensaje = f"QR generado para la identificación: {identificacion}, nombre: {nombre}, con un vinculo de: {area}."
                
            # Insertar datos en la tabla usuarios
            database.insertar_externo(identificacion, nombre, area, destinatario, compañia, motivo, dependencia, recibe, arl, equipo, qr_path)
            
            # Enviar el correo electrónico solo si se proporciona el correo
            if destinatario:
                enviar_correo(destinatario, "Codigo QR control de acceso Maestri Ontrack", f" Cordial saludo:\n\nTe informamos que el QR generado con la siguiente informacion ha sido registrado con exito!\n\nNombre: {nombre}\nVinculo: {area}\nIdentificación: {identificacion}\nCompañia que representa: {compañia}\nMotivo de la visita: {motivo}\nDependencia visitada:{dependencia}\nPersona que lo recibe: {recibe}\nArl: {arl}\nEquipo: {equipo}\n\nA continuacion adjuntamos el codigo", qr_path)

            if destinatario:
                flash('QR generado correctamente', 'success')
            return render_template('generar_externo.html', mensaje= mensaje, qr_path=qr_path)
        except ValueError as e:
            return render_template('generar_externo.html')
    usuarios = database.obtener_usuarios()
    return render_template('generar_externo.html', usuarios=usuarios)

@app.route('/externos')
@login_required
def mostrar_externos():
    # Obtener los datos de la tabla de externos
    externos = database.obtener_externos()

    # Obtener los datos de la tabla de usuarios
    usuarios = database.obtener_usuarios()

    return render_template('externos.html', externos=externos, usuarios=usuarios)



@app.route('/editar_externo/<int:id_externo>', methods=['GET', 'POST'])
@login_required
def editar_externo(id_externo):
    if request.method == 'POST':
        try:
            identificacion = int(request.form['identificacion'])
            nombre = request.form['nombre']
            correo = request.form['correo']
            compañia = request.form['compañia']
            motivo = request.form['motivo']
            dependencia = request.form['dependencia']
            recibe = request.form['recibe']
            arl = request.form['arl']
            equipo = request.form['equipo']
            
            # Verificar si el prefijo está en el diccionario de áreas
            prefijo = request.form['prefijo']
            area = areas.get(prefijo)

            # Llamar a la función para editar el registro en la base de datos
            database.editar_externo(id_externo, identificacion, nombre, area, correo, compañia, motivo, dependencia, recibe, arl, equipo)
            flash('Registro editado correctamente', 'success')  # Mensaje de éxito

            # Redireccionar a la página de lista de registros después de la edición
            return redirect(url_for('mostrar_externos'))
        except ValueError:
            flash('Error al editar el registro. Asegúrate de que los datos sean válidos.', 'error')
            return redirect(url_for('mostrar_externos'))
    else:
        # Obtener el registro a editar de la base de datos
        externo = database.obtener_externo_por_id(id_externo)
        usuarios = database.obtener_usuarios()
        return render_template('editar_externo.html', usuarios=usuarios, externo=externo)


@app.route('/ver_externo/<int:id_externo>')
@login_required
def ver_externo(id_externo):
    externo = database.obtener_externo_por_id(id_externo)
    if externo:
        return render_template('detalles_externo.html', externo=externo)
    else:
        return "Usuario no encontrado"
    
@app.route('/eliminar_externo/<int:id_externo>')
def eliminar_externo(id_externo):
    # Obtener el usuario por su ID
    externo = database.obtener_externo_por_id(id_externo)

    if externo:
        # Llamar a la función para borrar el usuario y la imagen QR
        database.borrar_externo(id_externo, externo['qr_path'])
        # Redirigir a la página de lista de usuarios
        return redirect(url_for('mostrar_externos'))
    else:
        return "Usuario no encontrado"
    
    
    
    
    
    

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/usuarios')
@login_required
def mostrar_usuarios():
    usuarios = database.obtener_usuarios()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/ver_usuario/<int:id_usuario>')
@login_required
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
@login_required
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

    # Verificar qué botón se ha presionado
    if request.args.get('exportar') == 'True':
        registros_filtrados = database.obtener_registros_entre_fechas(fecha_inicio, fecha_fin)
        
        df = pd.DataFrame(registros_filtrados)

        # Crear el nombre del archivo con el formato deseado
        nombre_archivo = f"{fecha_inicio.strftime('%Y-%m-%d')} - {fecha_fin.strftime('%Y-%m-%d')}_internos.xlsx"

        # Forzar la descarga del archivo de Excel desde memoria
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return send_file(excel_buffer, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name=nombre_archivo)
    elif request.args.get('filtrar_general') == 'True':
        registros = database.obtener_registros_entre_fechas(fecha_inicio, fecha_fin)
        tercero = database.obtener_tercero_entre_fechas(fecha_inicio, fecha_fin)
        
        # Crear DataFrames para registros y tercero
        df_registros = pd.DataFrame(registros)
        df_tercero = pd.DataFrame(tercero)

        # Fusionar DataFrames manteniendo las mismas columnas
        df_merged = pd.concat([df_registros, df_tercero], axis=0, ignore_index=True)

        # Ordenar por 'fecha' y 'hora_escaneo'
        df_merged.sort_values(by=['fecha', 'hora_escaneo'], inplace=True)

        # Llenar los valores NaN con 'N/A'
        df_merged.fillna('N/A', inplace=True)

        # Crear el nombre del archivo con el formato deseado
        nombre_archivo = f"{fecha_inicio.strftime('%Y-%m-%d')} - {fecha_fin.strftime('%Y-%m-%d')}_terceros.xlsx"

        # Forzar la descarga del archivo de Excel desde la memoria
        excel_buffer = BytesIO()
        df_merged.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        # Enviar el archivo Excel como respuesta
        return send_file(excel_buffer, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name=nombre_archivo)

    registros_filtrados = database.obtener_registros_entre_fechas(fecha_inicio, fecha_fin)
    
    return render_template('registros_bd.html', registros=registros_filtrados, fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'), fecha_fin=fecha_fin.strftime('%Y-%m-%d'))


@app.route('/crear_registro', methods=['GET', 'POST'])
@login_required
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
            flash('Registro creado correctamente', 'success')  # Mensaje de éxito
            return redirect(url_for('mostrar_registros_bd'))
        else:
            flash('Error al crear el registro', 'error')  # Mensaje de error
            return redirect(url_for('crear_registro'))
    else:
        usuarios = database.obtener_usuarios()
        return render_template('crear_registro.html', usuarios=usuarios)       

@app.route('/editar_registro/<int:id_registro>', methods=['GET', 'POST'])
@login_required
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
        flash('Registro editado correctamente', 'success')  # Mensaje de éxito

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
        flash('Registro eliminado correctamente', 'success')
        return redirect(url_for('mostrar_registros_bd'))
    else:
        return "Método no permitido", 405
    
    
    
    
    
@app.route('/terceros')
def mostrar_terceros():
    terceros = database.obtener_tercero()
    return render_template('terceros.html', terceros=terceros)

@app.route('/ver_tercero/<int:id_tercero>')
def ver_tercero(id_tercero):
    tercero = database.obtener_tercero_por_id(id_tercero)
    if tercero:
        return render_template('detalles_tercero.html', tercero=tercero)
    else:
        return "Usuario no encontrado"

@app.route('/filtrar_terceros', methods=['GET'])
def filtrar_terceros():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio:
        fecha_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')

    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')

    terceros_filtrados = database.obtener_tercero_entre_fechas(fecha_inicio, fecha_fin)
    
    if request.args.get('exportar') == 'True':
        df = pd.DataFrame(terceros_filtrados)

        # Crear el nombre del archivo con el formato deseado
        nombre_archivo = f"{fecha_inicio.strftime('%Y-%m-%d')} - {fecha_fin.strftime('%Y-%m-%d')}.xlsx"

        # Forzar la descarga del archivo de Excel desde memoria
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return send_file(excel_buffer, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name=nombre_archivo)


    return render_template('terceros.html', terceros=terceros_filtrados, fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'), fecha_fin=fecha_fin.strftime('%Y-%m-%d'))

@app.route('/crear_tercero', methods=['GET', 'POST'])
def crear_tercero():
    if request.method == 'POST':
        identificacion = request.form['identificacion']
        nombre = request.form['nombre']
        area = request.form['area']
        fecha = request.form['fecha']
        hora_escaneo = request.form['hora_escaneo']
        hora_entrada = request.form['hora_entrada']
        hora_salida = request.form['hora_salida']
        compañia = request.form['compañia']
        motivo = request.form['motivo']
        dependencia = request.form['dependencia']
        recibe = request.form['recibe']
        arl = request.form['arl']
        equipo = request.form['equipo']
        if database.crear_tercero(identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, compañia, motivo, dependencia, recibe, arl, equipo):
            flash('Registro eliminado correctamente', 'success')
            return redirect(url_for('mostrar_terceros'))
        else:
            flash('Error al crear el registro', 'error')
            return redirect(url_for('crear_tercero'))
    else:
        # Obtener la lista de usuarios desde la base de datos
        tercero = database.obtener_tercero()
        usuarios = database.obtener_usuarios()
        externos = database.obtener_externos()

        return render_template('crear_tercero.html', tercero= tercero, externos = externos, usuarios=usuarios)


@app.route('/editar_tercero/<int:id_tercero>', methods=['GET', 'POST'])
def editar_tercero(id_tercero):
    if request.method == 'POST':
        # Obtener los datos del formulario de edición
        identificacion = request.form['identificacion']
        nombre = request.form['nombre']
        area = request.form['area']
        fecha = request.form['fecha']
        hora_escaneo = request.form['hora_escaneo']
        hora_entrada = request.form['hora_entrada']
        hora_salida = request.form['hora_salida']
        compañia = request.form['compañia']
        motivo = request.form['motivo']
        dependencia = request.form['dependencia']
        recibe = request.form['recibe']
        arl = request.form['arl']
        equipo = request.form['equipo']

        # Llamar a la función para editar el tercero en la base de datos
        database.editar_tercero(id_tercero, identificacion, nombre, area, fecha, hora_escaneo, hora_entrada, hora_salida, compañia, motivo, dependencia, recibe, arl, equipo)
        flash('Registro editado correctamente', 'success')
        return redirect(url_for('mostrar_terceros'))
    else:
        # Obtener el tercero a editar de la base de datos
        tercero = database.obtener_tercero_por_id(id_tercero)
        usuarios = database.obtener_usuarios()
        externos = database.obtener_externos()
        return render_template('editar_tercero.html', externos = externos, tercero=tercero, usuarios=usuarios)

@app.route('/borrar_tercero/<int:id_tercero>', methods=['GET', 'POST'])
def borrar_tercero_route(id_tercero):
    if request.method == 'POST':
        database.borrar_tercero(id_tercero)
        flash('Registro eliminado correctamente', 'success')
        return redirect(url_for('mostrar_terceros'))
    else:
        return "Método no permitido", 405
    
app.register_blueprint(login_blueprint)

if __name__ == '__main__':
    app.run(host='192.168.0.45', port=5000, debug=True)
