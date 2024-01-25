import cv2
from pyzbar.pyzbar import decode
import numpy as np
from datetime import datetime
import openpyxl as xl
import time

cap = cv2.VideoCapture(0)

mañana = []
tiempo_ultima_registro = {}

def infhora():
    inf = datetime.now()
    fecha = inf.strftime('%Y-%m-%d')
    hora = inf.strftime('%H:%M:%S')
    return hora, fecha

# Crear el nombre del archivo con la fecha actual
hora, fecha_actual = infhora()
nomar = f"{fecha_actual}.xlsx"

# Intentar cargar el archivo existente
try:
    wb = xl.load_workbook(nomar)
    hojam = wb["Actual"]
except FileNotFoundError:
    # Si el archivo no existe, crear uno nuevo
    wb = xl.Workbook()
    hojam = wb.create_sheet("Actual")
    hojam.append(["ID", "Nombre", "Fecha", "Hora"])  # Encabezados

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
                    wb.save(nomar)

                    cv2.putText(frame, f"{letr}0{num}", (xi - 15, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 55, 0), 2)
                    print("El usuario es accionista de la empresa \nNúmero de Identificación:", codigo, "Fecha de registro:", fecha, "Hora de registro:", texth)

                elif codigo in mañana:
                    cv2.putText(frame, f"El ID {codigo}", (xi - 65, yi - 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    cv2.putText(frame, "Fue registrado", (xi - 65, yi - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    print(mañana)

    cv2.imshow("SISTEMA CONTROL DE ACCESO", frame)

    t = cv2.waitKey(5)
    if t == 27:
        break

wb.close()
cv2.destroyAllWindows()
cap.release()
