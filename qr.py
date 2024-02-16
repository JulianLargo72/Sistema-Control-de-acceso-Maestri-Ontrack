import smtplib
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
