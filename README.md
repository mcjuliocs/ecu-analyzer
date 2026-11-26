# 🚗 ECU Studio 3D — Analizador y Calibrador Binario

Herramienta interactiva desarrollada en Python para la lectura, visualización topográfica en 3D y recalibración de mapas de inyección en archivos binarios (.bin) de computadoras automotrices (ECU).

## Funcionalidades principales
* *Soporte de definiciones XDF/XML:* Extrae dinámicamente offsets, dimensiones de matriz, tipos de datos (uint16_le) y factores de escala.
* *Calibración Modo ECO con suavizado espacial:* Recorta el pulso de inyección en zonas de velocidad crucero aplicando un filtro de vecindad para evitar transiciones bruscas o tirones.
* *Protección de zonas críticas:* Preserva intactas las tablas de corte de combustible en desaceleración (Fuel Cut-Off) y ralentí.
* *Análisis Delta 3D:* Compara la superficie calibrada contra el mapa original (Stock) y calcula métricas de ahorro en tiempo real.
* *Integridad de memoria:* Recalcula el Checksum de 16 bits al exportar el nuevo archivo binario .bin.

## Instalación y uso