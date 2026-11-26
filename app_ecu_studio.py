import streamlit as st
import xml.etree.ElementTree as ET
import numpy as np
import struct
import matplotlib.pyplot as plt

st.set_page_config(page_title="ECU Studio 3D", layout="wide")
st.title("🚗 ECU Studio 3D — Analizador y Calibrador Binario")
st.markdown("Herramienta de visualización 3D, calibración en zona de crucero y verificación de checksum.")

st.sidebar.header("1. Fuente de Datos")
usar_demo = st.sidebar.checkbox("Usar datos de ejemplo (cavalier 1.5L)", value=True)

if not usar_demo:
    archivo_xdf = st.sidebar.file_uploader("Plantilla de definición (.xdf)", type=["xdf", "xml"])
    archivo_bin = st.sidebar.file_uploader("Meemoria de la ECU (.bin)", type=["bin"])
else:
    archivo_xdf = "cavalier_e83.xdf"
    archivo_bin = "cavalier_2018_atock.bin"

st.sidebar.header("2. Parámetros de Calibración ECO")
recorte_pct = st.sidebar.slider("Recorte de combustible en crucero (%)", 0, 20, 12)
rpm_min, rpm_max = st.sidebar.slider("Rango de RPM crucero", 1000, 5000, (1500, 3200), step=100)
carga_min, carga_max = st.sidebar.slider("Rango de Carga del motor (%)", 5, 70, (15, 45), step=5)
pasadas_suavizado = st.sidebar.slider("Pasadas de suavizado espacial", 0, 5, 3)

if archivo_xdf is not None and archivo_bin is not None:
    tree = ET.parse(archivo_xdf)
    root = tree.getroot()
    titulo_ecu = root.find('.//deftitle').text
    tabla = root.find('.//XDFTABLE')
    
    nombre_mapa = tabla.find('title').text
    offset = int(tabla.find('offset').text, 16)
    filas = int(tabla.find('rows').text)
    cols = int(tabla.find('cols').text)
    factor = float(tabla.find('factor').text)
    unidades = tabla.find('units').text

    total_celdas = filas * cols
    if isinstance(archivo_bin, str):
        datos_binarios = bytearray([0xFF] * 4096)
        rpm_sim = np.linspace(800, 6500, cols)
        carga_sim = np.linspace(0, 100, filas)
        X_s, Y_s = np.meshgrid(rpm_sim, carga_sim)
        mapa_sim = (Y_s / 100.0) * 14.0 + (X_s / 6500.0) * 4.5 + 1.8
        mapa_sim[0, 3:] = 0.0
        crudos = np.round(mapa_sim / factor).astype(np.uint16).flatten()
        datos_binarios[offset : offset + (total_celdas * 2)] = struct.pack(f'<{total_celdas}H', *crudos)
    else:
        datos_binarios = bytearray(archivo_bin.read())

    bloque = datos_binarios[offset : offset + (total_celdas * 2)]
    valores = struct.unpack(f'<{total_celdas}H', bloque)
    Z_stock = np.array(valores, dtype=float).reshape((filas, cols)) * factor

    rpm = np.linspace(800, 6500, cols)
    carga = np.linspace(0, 100, filas)
    X, Y = np.meshgrid(rpm, carga)

    Z_mod = Z_stock.copy()
    zona_eco = (X >= rpm_min) & (X <= rpm_max) & (Y >= carga_min) & (Y <= carga_max)
    Z_mod[zona_eco] *= (1.0 - recorte_pct / 100.0)

    Z_suave = Z_mod.copy()
    for _ in range(pasadas_suavizado):
        temp = Z_suave.copy()
        for f in range(2, filas - 1):
            for c in range(1, cols - 1):
                vecinos = (temp[f-1, c] + temp[f+1, c] + temp[f, c-1] + temp[f, c+1]) / 4.0
                Z_suave[f, c] = 0.5 * temp[f, c] + 0.5 * vecinos

    Z_suave[0, :] = Z_stock[0, :]
    Z_suave[1, :] = Z_stock[1, :]
    Z_delta = Z_suave - Z_stock

    datos_nuevos = np.round(Z_suave / factor).astype(np.uint16).flatten()
    datos_binarios[offset : offset + (total_celdas * 2)] = struct.pack(f'<{total_celdas}H', *datos_nuevos)
    checksum = sum(datos_binarios[:-2]) & 0xFFFF
    datos_binarios[-2:] = struct.pack('<H', checksum)

    st.subheader(f"Perfil activo: {titulo_ecu} — {nombre_mapa}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Offset Memoria", hex(offset))
    col2.metric("Ahorro Máximo", f"{np.min(Z_delta):.2f} {unidades}")
    col3.metric("Ahorro Promedio Zona", f"{np.mean(Z_delta[zona_eco]):.2f} {unidades}")
    col4.metric("Checksum Calculado", hex(checksum))

    fig = plt.figure(figsize=(14, 5))
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot_surface(X, Y, Z_suave, cmap='viridis', edgecolor='k', linewidth=0.3)
    ax1.set_title(f"Mapa Calibrado ECO ({unidades})")
    ax1.set_xlabel("RPM")
    ax1.set_ylabel("Carga (%)")

    ax2 = fig.add_subplot(122, projection='3d')
    ax2.plot_surface(X, Y, Z_delta, cmap='coolwarm', edgecolor='k', linewidth=0.3)
    ax2.set_title(f"Mapa Delta: Diferencia Real ({unidades})")
    ax2.set_xlabel("RPM")
    ax2.set_ylabel("Carga (%)")

    plt.tight_layout()
    st.pyplot(fig)

    st.download_button(
        label="⬇️ Descargar Archivo Calibrado (.bin)",
        data=bytes(datos_binarios),
        file_name="ecu_calibrada_eco.bin",
        mime="application/octet-stream"
    )
else:
    st.info("👈 Sube tu archivo *.xdf* y *.bin* en el menú de la izquierda para comenzar.")