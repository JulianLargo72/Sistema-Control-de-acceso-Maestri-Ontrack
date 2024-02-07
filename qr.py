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

#Función para generar el código QR y devolver la ruta y la información completa
def generar_qr(prefijo, identificacion, nombre):
    if not prefijo.isalpha():
        raise ValueError("El prefijo debe contener solo letras.")
    
    ascii_prefijo = str(ord(prefijo))  # Convertir letra a código ASCII
    id_completo = ascii_prefijo + str(identificacion)
    info_completa = f"{id_completo} - {nombre}"
    qr = pyqrcode.create(info_completa, error='L')
    qr_path = f'static/qr_images/{prefijo}{identificacion}.png'
    qr.png(qr_path, scale=6)
    return qr_path, info_completa  # Devolver la ruta y la información completa

# Función para enviar el correo electrónico
def enviar_correo(destinatario, asunto, cuerpo, adjunto_path):
    remitente = "sistemasmaestri@gmail.com"
    password = "ugtdrarcnbgsxnbu"

        # Configuración del servidor SMTP de Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(remitente, password)

    # Construir el mensaje del correo electrónico
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Adjuntar la imagen del código QR al mensaje
    with open(adjunto_path, 'rb') as archivo_adjunto:
        adjunto = MIMEImage(archivo_adjunto.read(), name='qr.png')
        mensaje.attach(adjunto)

    # Enviar el correo electrónico
    server.sendmail(remitente, destinatario, mensaje.as_string())
    server.quit()