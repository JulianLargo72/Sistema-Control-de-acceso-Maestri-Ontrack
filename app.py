from flask import Flask, render_template, request
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from datetime import datetime
import openpyxl as xl
import time
import pyqrcode
import os

app = Flask(__name__)

def generar_qr(prefijo, identificacion, nombre):
    if not prefijo.isalpha():
        raise ValueError("El prefijo debe contener solo letras.")
    
    ascii_prefijo = str(ord(prefijo))  # Convertir letra a código ASCII
    id_completo = ascii_prefijo + str(identificacion)
    info_completa = f"{id_completo} - {nombre}"
    qr = pyqrcode.create(info_completa, error='L')
    qr_path = f'static/qr_images/{prefijo}{identificacion}.png'
    qr.png(qr_path, scale=6)
    return qr_path

@app.route('/generar', methods=['GET', 'POST'])
def generar():
    if request.method == 'POST':
        try:
            prefijo = request.form['prefijo']
            
            if not prefijo.isalpha():
                raise ValueError("El prefijo debe contener solo letras.")
            
            identificacion = int(request.form['identificacion'])
            nombre = request.form['nombre']
            qr_path = generar_qr(prefijo, identificacion, nombre)
            mensaje = f"QR generado para la identificación {identificacion} y el nombre {nombre}"
            return render_template('generar.html', mensaje=mensaje, qr_path=qr_path)
        except ValueError as e:
            mensaje = str(e)
            return render_template('generar.html', mensaje=mensaje)
    return render_template('generar.html')

if __name__ == '__main__':
    app.run(debug=True)
