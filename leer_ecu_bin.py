import numpy as np
import struct
import matplotlib.pyplot as plt

with open ("cavalier_2018_stock.bin", "rb") as archivo:
    datos_binarios = archivo.read()

id_ecu = datos_binarios [0:32].decode('ascii', errors='ignore')
print(f"ECU Detectada: {id_ecu}")

offset = 0x0400
tamano_bytes = 256 * 2 
bloque_mapa = datos_binarios[offset : offset + tamano_bytes]

valores_enteros = struct.unpack('<256H', bloque_mapa)
matriz_inyeccion = np.array(valores_enteros, dtype=float).reshape((16, 16)) / 100.0

rpm = np.linspace(800, 6500, 16)
carga = np.linspace(0, 100, 16)
X, Y = np.meshgrid(rpm, carga)

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, matriz_inyeccion, cmap='jet', edgecolor='k', linewidth=0.3)
ax.set_title(f'Mapa Extraido de BIN: {id_ecu}')
ax.set_xlabel('RPM')
ax.set_ylabel('carga (%)')
ax.set_zlabel(':Inyección (ms)')

plt.tight_layout()
plt.show()