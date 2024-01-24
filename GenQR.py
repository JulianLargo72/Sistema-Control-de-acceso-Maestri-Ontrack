# Importamos las librerias
import pyqrcode
import png
from pyqrcode import QRCode


def generar_qr(identificacion, nombre):
    id_completo = '65' + str(identificacion)
    info_completa = f"{id_completo} - {nombre}"
    qr = pyqrcode.create(info_completa, error='L')
    qr.png('A' + str(identificacion) + '.png', scale=6)

# Preguntar al usuario si desea crear más códigos QR
while True:
    try:
        identificacion = int(input("Ingrese la identificación (número entero): "))
        nombre = input("Ingrese el nombre: ")
        generar_qr(identificacion, nombre)
        print(f"QR generado para la identificación {identificacion} y el nombre {nombre}")
    except ValueError:
        print("Por favor, ingrese un número entero válido.")

    opcion = input("¿Desea crear más códigos QR? (s/n): ")
    if opcion.lower() != 's':
        break