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

def generar_qr(identificacion, nombre):
    id_completo = '65' + str(identificacion)
    info_completa = f"{id_completo} - {nombre}"
    qr = pyqrcode.create(info_completa, error='L')
    qr_path = f'static/qr_images/A{identificacion}.png'
    qr.png(qr_path, scale=6)
    return qr_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            identificacion = int(request.form['identificacion'])
            nombre = request.form['nombre']
            qr_path = generar_qr(identificacion, nombre)
            mensaje = f"QR generado para la identificación {identificacion} y el nombre {nombre}"
            return render_template('generar.html', mensaje=mensaje, qr_path=qr_path)
        except ValueError:
            mensaje = "Por favor, ingrese un número entero válido."
            return render_template('generar.html', mensaje=mensaje)
    return render_template('generar.html')

if __name__ == '__main__':
    app.run(host='192.168.0.44', port=5000, debug=True)
