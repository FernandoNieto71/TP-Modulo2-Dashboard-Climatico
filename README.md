# 🌎 Dashboard Climático — TP Programación Avanzada para Ciencia de Datos

Este proyecto construye un dashboard en HTML a partir de datos climáticos históricos, combinando procesamiento de datos, limpieza, imputación, visualización y geolocalización.

---

## 📁 Fuentes de datos

Se utilizan dos datasets:

1. **Estadísticas Climáticas Normales**  
   Archivo: `ESTADISTICAS CLIMATICAS NORMALES.CSV`  
   Contiene valores mensuales por estación meteorológica y tipo de variable (temperatura, humedad, viento).

2. **Estaciones Meteorológicas**  
   Archivo: `ESTACIONES METEOROLOGICAS.TXT`  
   Incluye coordenadas geográficas (latitud y longitud) de cada estación.

---

## 🔄 Proceso de integración

- Se normalizan los nombres de estaciones y columnas para evitar errores de coincidencia.
- Se transforma el CSV climático a formato largo (`melt`) para facilitar el análisis por mes.
- Se realiza un `merge` entre ambos datasets para incorporar coordenadas.
- Se corrigen manualmente las coordenadas faltantes de 7 estaciones específicas mediante `UPDATE` en SQLite.

---

## 🧼 Limpieza y validación

- Se convierten los valores climáticos a formato numérico (`VALOR LIMPIO`).
- Se imputan valores faltantes por promedio mensual por estación (`VALOR FINAL`).
- Se revisan y corrigen los formatos de latitud, longitud y etiquetas de variables.

---

## 📊 Indicadores calculados (KPIs)

- 🌡️ **Temperatura promedio** (`TEMPERATURA (°C)`)
- 💧 **Humedad relativa promedio** (`HUMEDAD RELATIVA (%)`)
- 🌬️ **Velocidad del viento promedio** (`VELOCIDAD DEL VIENTO (KM/H)`)

---

## 📈 Gráficos generados

- **Evolución mensual por estación** para cada variable (líneas interactivas con Plotly).
- **Mapas interactivos** por mes para:
  - Temperatura máxima (`TEMPERATURA MÁXIMA (°C)`)
  - Temperatura mínima (`TEMPERATURA MÍNIMA (°C)`)


---

## 🧾 Salidas del proyecto

- `clima.db`: base SQLite con datos unificados y corregidos.
- `paraHTML.html`: dashboard principal con KPIs y gráficos de línea, contiene los mapas interactivos por mes en formato HTML..
- La base de datos clima.db se genera automáticamente en la raíz del proyecto al ejecutar paraHTML.py.

---

## 🛠️ Herramientas utilizadas

- **Python** (`pandas`, `sqlite3`, `plotly`)
- **Plotly Express** para visualización interactiva
- **SQLite** para persistencia y correcciones
- **HTML** como formato final para visualización y publicación

---

## ▶️ Ejecución

1. Ejecutar el script `paraHTML.py` desde consola:
   ```bash
   python paraHTML.py



🖥️ Cómo ejecutar el proyecto
Opción 1: Desde GitHub (si se publica)
Cloná el repositorio o descargá los archivos como ZIP.

Asegurate de tener Python instalado (versión 3.8 o superior).

Instalá las dependencias si no las tenés:
pip install pandas plotly

Ejecutá el script principal:
python paraHTML.py

Al finalizar, se generará el archivo dashboard_climatico.html en la misma carpeta, junto con los mapas en la subcarpeta mapas/.

Opción 2: Desde el notebook
Abrí modulo 2.ipynb en Jupyter o Colab.

Ejecutá las celdas en orden para visualizar los gráficos y mapas directamente.

Podés adaptar el código para guardar los gráficos como HTML si lo deseás.