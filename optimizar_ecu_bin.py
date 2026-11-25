import numpy as np
import struct
import matplotlib.pyplot as plt

with open("cavalier_2018_stock.bin", "rb") as f:
    datos_binarios = bytearray(f.read())

offset = 0x0400
bloque_mapa = datos_binarios[offset : offset + 512]
valores = struct.unpack('<256H', bloque_mapa)
Z_stock = np.array(valores, dtype=float).reshape((16, 16)) / 100.0
 
rpm = np.linspace(800, 6500, 16)
carga = np.linspace(0, 100, 16)
X, Y = np.meshgrid(rpm, carga)

Z_mod =  Z_stock.copy()
zona_eco  =  (X >=1500) & (X <=3200) & (Y >= 15) & (Y <= 45)
Z_mod[zona_eco] *= 0.88

Z_suave = Z_mod.copy()
for _ in range(3):
    temp = Z_suave.copy()
    for fila in range(1, 15):
        for col in range(1, 15):
            vecinos = (temp[fila-1, col] + temp[fila+1, col] + temp[fila, col-1] + temp[fila, col+1]) / 4.0
            Z_suave[fila, col] = 0.5 * temp[fila, col] + 0.5 * vecinos

Z_suave[0, :] = Z_stock[0, :]

datos_nuevos = np.round(Z_suave * 100).astype(np.uint16).flatten()
bytes_nuevos = struct.pack('<256H', *datos_nuevos)
datos_binarios[offset : offset + 512] = bytes_nuevos

checksum = sum(datos_binarios[0:4094]) & 0xFFFF
datos_binarios[4094:4096] = struct.pack('<H', checksum)

with open ("cavalier_2018_eco.bin", "wb") as f:
    f.write(datos_binarios)

print(f"Archivo 'cavalier_2018_eco.bin' generado con exito. Checksum: {hex(checksum)}")

fig = plt.figure(figsize=(12, 5))
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(X, Y, Z_stock, cmap='viridis', edgecolor='k', linewidth=0.3)
ax1.set_title('Original (Stock .bin)')

ax2 = fig.add_subplot(122, projection='3d')
ax2.plot_surface(X, Y, Z_suave, cmap='viridis', edgecolor='k', linewidth=0.3)
ax2.set_title('Modificado ECO + Suavizado (.bin)')

plt.tight_layout()
plt.show()