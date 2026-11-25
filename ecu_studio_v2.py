import xml.etree.ElementTree as ET
import numpy as np
import struct
import matplotlib.pyplot as plt

def cargar_definicion_xdf(ruta_xdf):
    tree = ET.parse(ruta_xdf)
    root = tree.getroot()
    titulo_ecu = root.find('.//deftitle').text
    tabla = root.find('.//XDFTABLE')

    config = {
        "ecu": titulo_ecu,
        "nombre_mapa": tabla.find('title').text,
        "offset": int(tabla.find('offset').text, 16),
        "filas": int(tabla.find('rows').text),
        "cols": int(tabla.find('cols').text),
        "factor": float(tabla.find('factor').text),
        "unidades": tabla.find('units').text
    }
    return config

def extraer_mapa(ruta_bin, config):
    with open(ruta_bin, "rb") as f:
        datos = f.read()

        total_celdas = config["filas"] * config["cols"]
        tamano_bytes = total_celdas * 2
        bloque = datos [config["offset"] : config["offset"] + tamano_bytes]

        valores = struct.unpack(f'<{total_celdas}H', bloque)
        matriz = np.array(valores, dtype=float).reshape((config["filas"], config["cols"])) * config["factor"]
        return matriz

config = cargar_definicion_xdf("cavalier_e83.xdf")
print(f"Cargando perfil: {config['ecu']} | Tabla: {config['nombre_mapa']} en {hex(config['offset'])}")

Z_stock = extraer_mapa("cavalier_2018_stock.bin", config)
Z_eco = extraer_mapa("cavalier_2018_eco.bin", config)

Z_delta = Z_eco - Z_stock

rpm = np.linspace(800, 6500, config["cols"])
carga = np.linspace(0, 100, config["filas"])
X, Y = np.meshgrid(rpm, carga)

fig = plt.figure(figsize=(13, 5))

ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(X, Y, Z_eco, cmap='viridis', edgecolor='k', linewidth=0.3)
ax1.set_title(f"{config['nombre_mapa']} - ECO ({config['unidades']})")

ax2 = fig.add_subplot(122, projection='3d')
ax2.plot_surface(X, Y, Z_delta, cmap='coolwarm', edgecolor='k', linewidth=0.3)
ax2.set_title(f"Mapa Delta: Ahorro Real ({config['unidades']})")
ax2.set_zlabel('Diferencia (ms)')

plt.tight_layout()
plt.show()