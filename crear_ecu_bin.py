import numpy as np
import struct

memoria_flash =bytearray([0xFF] * 4096)

firma = b"GM_DELCO_E83_CAVALIER_1.5L_CAL_V2"
memoria_flash[0:len(firma)] = firma

rpm = np.linspace(800, 6500, 16)
carga = np.linspace(0, 100,16)
X, Y = np.meshgrid(rpm, carga)
mapa_ms = (Y / 100.0) * 14.0 + (X / 6500.0) * 4.5 + 1.8
mapa_ms[0,3:] = 0.0 

offset_inicio = 0x0400
datos_crudos = np.round(mapa_ms * 100).astype(np.uint16).flatten()

bytes_mapa = struct.pack(f'<{len(datos_crudos)}H', *datos_crudos)
memoria_flash[offset_inicio : offset_inicio + len(bytes_mapa)] = bytes_mapa

with open("cavalier_2018_stock.bin", "wb") as archivo:
    archivo.write(memoria_flash)

print("Archivo binario 'cavalier_2018_stock.bin' generado (4096 bytes).")