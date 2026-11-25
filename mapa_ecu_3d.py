import numpy as np
import matplotlib.pyplot as plt

rpm = np.linspace(800, 6500, 16)
carga = np.linspace(0, 100, 16)
X, Y = np.meshgrid(rpm, carga)

Z_original = (Y / 100.0) * 14.0 + (X / 6500.0) * 4.5 + 1.8
Z_original [0, 3:] = 0.0

Z_eco = Z_original.copy()
zona_crucero = (X >= 1500) & (X <=3200) & (Y <= 45)
Z_eco[zona_crucero] *= 0.88

fig = plt.figure(figsize=(12, 5))

ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(X, Y, Z_original, cmap='jet', edgecolor='k', linewidth=0.3)
ax1.set_title('Mapa Original ECU (Inyección ms)')
ax1.set_xlabel('RPM')
ax1.set_ylabel('Carga (%)')
ax1.set_zlabel('Inyección (ms)')

ax2 = fig.add_subplot(122, projection='3d')
ax2.plot_surface(X, Y, Z_eco, cmap='viridis', edgecolor='k', linewidth=0.3)
ax2.set_title('Mapa Optimizado ECO (-12% en crucero)')
ax2.set_xlabel('RPM')
ax2.set_ylabel('Carga (%)')
ax2.set_zlabel('Inyección (ms)')

plt.tight_layout()
plt.show()