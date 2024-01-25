import os

from flask import Flask, render_template, Response
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from datetime import datetime
import openpyxl as xl
import time

app = Flask(__name__)

cap = cv2.VideoCapture(1)  # Inicializar la cámara
mañana = []
tiempo_ultima_registro = {}

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

# Construir la ruta completa al archivo Excel en la nueva carpeta
hora, fecha_actual = infhora()
ruta_archivo_excel = os.path.join(nombre_carpeta_registros, f"{fecha_actual}.xlsx")

try:
    wb = xl.load_workbook(ruta_archivo_excel)
    hojam = wb["Actual"]
except FileNotFoundError:
    # Si el archivo no existe, crear uno nuevo en la nueva carpeta
    wb = xl.Workbook()
    hojam = wb.create_sheet("Actual")
    hojam.append(["ID", "Nombre", "Fecha", "Hora"])  # Encabezados
    # Guardar en la nueva carpeta
    wb.save(ruta_archivo_excel)

def generate_frames():
    cap = cv2.VideoCapture(1)
    while True:
        ret, frame = cap.read()

        hora, fecha = infhora()
        diasem = datetime.today().weekday()

        a, me, d = fecha[0:4], fecha[5:7], fecha[8:10]
        h, m, s = int(hora[0:2]), int(hora[3:5]), int(hora[6:8])

        texth = f"{h}:{m}:{s}"
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

            if 6 >= diasem >= 0:
                cv2.polylines(frame, [pts], True, (255, 255, 0), 5)

                if codigo not in mañana or (codigo in mañana and time.time() - tiempo_ultima_registro.get(codigo, 0) > 60):
                    mañana.append(codigo)
                    tiempo_ultima_registro[codigo] = time.time()

                    codigo_despues_del_primer_digito = info.split('-')[0][2:].strip()
                    hojam.append([codigo_despues_del_primer_digito, nombre, fecha, texth])
                    wb.save(ruta_archivo_excel)

                    cv2.putText(frame, f"{letr}0{num}", (xi - 15, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 55, 0), 2)
                    print("El usuario es accionista de la empresa \nNúmero de Identificación:", codigo, "Fecha de registro:", fecha, "Hora de registro:", texth)

                elif codigo in mañana:
                    cv2.putText(frame, f"El ID {codigo}", (xi - 65, yi - 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    cv2.putText(frame, "Fue registrado", (xi - 65, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    print(mañana)

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('leer.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
