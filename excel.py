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

def enviar_correo_excel(destinatario, asunto, cuerpo, adjunto_path):
    remitente = "sistemasmaestri@gmail.com"
    password = "ugtdrarcnbgsxnbu"

    # Configuración del servidor SMTP de Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(remitente, password)

    # Carga el archivo adjunto en memoria
    archivo_adjunto_memoria = open(adjunto_path, 'rb').read()

    # Crea el mensaje de correo electrónico
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    # Adjuntar el archivo Excel al mensaje
    adjunto = MIMEApplication(archivo_adjunto_memoria, _subtype="xlsx")
    adjunto.add_header('Content-Disposition', f'attachment; filename={os.path.basename(adjunto_path)}')
    mensaje.attach(adjunto)

    # Agregar el cuerpo del mensaje
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Enviar el correo electrónico
    server.sendmail(remitente, destinatario, mensaje.as_string())
    server.quit()