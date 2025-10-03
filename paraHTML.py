import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go

# 📁 Rutas
#carpeta = r"C:\UniCABA\Programacion Avanzada para Cs Datos\TP-modulo_2"
#csv_path = os.path.join(carpeta, "ESTADISTICAS CLIMATICAS NORMALES.CSV")
#txt_path = os.path.join(carpeta, "ESTACIONES METEOROLOGICAS.TXT")
#db_path = os.path.join(carpeta, "clima.db")
#html_path = os.path.join(carpeta, "dashboard_climatico.html")
#mapas_path = os.path.join(carpeta, "mapas")
#os.makedirs(mapas_path, exist_ok=True)

import os

# 📁 Rutas dinámicas basadas en ubicación del script
base_dir = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(base_dir, "datasets", "ESTADISTICAS CLIMATICAS NORMALES.CSV")
txt_path = os.path.join(base_dir, "datasets", "ESTACIONES METEOROLOGICAS.TXT")
db_path = os.path.join(base_dir, "clima.db")
html_path = os.path.join(base_dir, "dashboard_climatico.html")
mapas_path = os.path.join(base_dir, "mapas")
os.makedirs(mapas_path, exist_ok=True)

if not os.path.exists(csv_path):
    raise FileNotFoundError(f"❌ No se encontró el archivo CSV en: {csv_path}")

if not os.path.exists(txt_path):
    raise FileNotFoundError(f"❌ No se encontró el archivo TXT en: {txt_path}")


# 📥 Leer archivos
df_csv = pd.read_csv(csv_path, sep=";", encoding="latin1")
df_txt = pd.read_csv(txt_path, sep=",", encoding="latin1")

# 🧼 Normalizar columnas y textos
df_csv.columns = df_csv.columns.str.strip().str.upper()
df_txt.columns = df_txt.columns.str.strip().str.upper()

def normalizar(s):
    return (str(s).upper().strip()
            .replace("Á", "A").replace("É", "E").replace("Í", "I")
            .replace("Ó", "O").replace("Ú", "U").replace("Ñ", "N"))

df_csv["ESTACIÓN"] = df_csv["ESTACIÓN"].apply(normalizar)
df_txt["NOMBRE"] = df_txt["NOMBRE"].apply(normalizar)

# 📐 CSV a formato largo
df_largo = df_csv.melt(
    id_vars=["ESTACIÓN", "VALOR MEDIO DE"],
    var_name="MES",
    value_name="VALOR"
)

# 🔗 Unir con coordenadas
df_final = df_largo.merge(
    df_txt[["NOMBRE", "LATITUD", "LONGITUD"]],
    left_on="ESTACIÓN",
    right_on="NOMBRE",
    how="left"
).drop(columns=["NOMBRE"])

# 🗃️ Guardar en base SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS datos_climaticos")
df_final.to_sql("datos_climaticos", conn, index=False)

# 🔄 Correcciones manuales
correcciones = [
    {"ESTACIÓN": "BUENOS AIRES", "LATITUD": -34.61315, "LONGITUD": -58.37723},
    {"ESTACIÓN": "LA QUIACA OBS.", "LATITUD": -22.10448, "LONGITUD": -65.59646},
    {"ESTACIÓN": "MALARGÜE AERO", "LATITUD": -35.47791, "LONGITUD": -69.58521},
    {"ESTACIÓN": "PIGÜE AERO", "LATITUD": -37.60255, "LONGITUD": -62.40836},
    {"ESTACIÓN": "PILAR OBS.", "LATITUD": -34.45867, "LONGITUD": -58.91398},
    {"ESTACIÓN": "SAN MIGUEL", "LATITUD": -34.54335, "LONGITUD": -58.71229},
    {"ESTACIÓN": "VILLA MARIA DEL RIO SECO", "LATITUD": -29.90651, "LONGITUD": -63.72260}
]

for item in correcciones:
    cursor.execute("""
        UPDATE datos_climaticos
        SET LATITUD = ?, LONGITUD = ?
        WHERE ESTACIÓN LIKE ?
    """, (item["LATITUD"], item["LONGITUD"], item["ESTACIÓN"]))

conn.commit()
conn.close()

# 📥 Leer desde SQLite
conn = sqlite3.connect(db_path)
df = pd.read_sql("SELECT * FROM datos_climaticos", conn)
conn.close()

# 🧼 Preparar datos
df["VALOR MEDIO DE"] = df["VALOR MEDIO DE"].str.strip().str.upper()
df["VALOR LIMPIO"] = pd.to_numeric(df["VALOR"], errors="coerce")
df["LATITUD"] = pd.to_numeric(df["LATITUD"], errors="coerce")
df["LONGITUD"] = pd.to_numeric(df["LONGITUD"], errors="coerce")

# 🎯 KPIs
def calcular_promedio(df, categoria):
    filtro = df["VALOR MEDIO DE"] == categoria.upper()
    return df.loc[filtro, "VALOR LIMPIO"].dropna().mean()

temp_prom = calcular_promedio(df, "TEMPERATURA (°C)")
humedad_prom = calcular_promedio(df, "HUMEDAD RELATIVA (%)")
viento_prom = calcular_promedio(df, "VELOCIDAD DEL VIENTO (KM/H)")

# 📈 Gráficos por variable
def grafico_linea(df, variable):
    df_var = df[df["VALOR MEDIO DE"] == variable.upper()].copy()
    df_var = df_var.dropna(subset=["VALOR LIMPIO", "MES", "ESTACIÓN"])
    return px.line(df_var, x="MES", y="VALOR LIMPIO", color="ESTACIÓN", title=variable)

fig_temp = grafico_linea(df, "TEMPERATURA (°C)")
fig_humedad = grafico_linea(df, "HUMEDAD RELATIVA (%)")
fig_viento = grafico_linea(df, "VELOCIDAD DEL VIENTO (KM/H)")

# 🗺️ Mapas por mes
def generar_mapa(mes):
    df_mapa = df.copy() if mes == "Todos" else df[df["MES"] == mes]
    df_mapa = df_mapa.dropna(subset=["VALOR LIMPIO", "LATITUD", "LONGITUD", "ESTACIÓN"])

    for tipo in ["TEMPERATURA MÁXIMA (°C)", "TEMPERATURA MÍNIMA (°C)"]:
        df_temp = df_mapa[df_mapa["VALOR MEDIO DE"] == tipo].copy()
        if df_temp.empty:
            continue

        df_temp["VALOR SIZE"] = df_temp["VALOR LIMPIO"].abs()

        fig = px.scatter_map(df_temp,
                             lat="LATITUD", lon="LONGITUD",
                             color="VALOR LIMPIO", size="VALOR SIZE",
                             hover_name="ESTACIÓN",
                             zoom=4, height=500,
                             title=f"Mapa de temperatura {tipo.split()[1]} - {mes}")
        fig.update_layout(mapbox_style="open-street-map")

        nombre_archivo = f"mapa_{tipo.split()[1].lower()}_{mes}.html".replace(" ", "_")
        ruta_archivo = os.path.join(mapas_path, nombre_archivo)
        fig.write_html(ruta_archivo, include_plotlyjs="cdn", full_html=True)
        print(f"✅ Mapa guardado: {ruta_archivo}")

# 🧠 Generar mapas para todos los meses
meses = ["Todos"] + sorted(df["MES"].dropna().unique().tolist())
for mes in meses:
    generar_mapa(mes)

# 📊 Dashboard KPIs
dashboard = go.Figure()
dashboard.add_trace(go.Indicator(
    mode="number",
    value=temp_prom,
    title={"text": "🌡️ Temperatura Promedio (°C)"},
    domain={"row": 0, "column": 0}
))
dashboard.add_trace(go.Indicator(
    mode="number",
    value=humedad_prom,
    title={"text": "💧 Humedad Promedio (%)"},
    domain={"row": 0, "column": 1}
))
dashboard.add_trace(go.Indicator(
    mode="number",
    value=viento_prom,
    title={"text": "🌬️ Viento Promedio (km/h)"},
    domain={"row": 0, "column": 2}
))
dashboard.update_layout(grid={"rows": 1, "columns": 3}, title="📊 KPIs Climáticos")

# 🧾 Guardar dashboard completo
#with open(html_path, "w", encoding="utf-8") as f:
#    f.write(dashboard.to_html(full_html=False, include_plotlyjs='cdn'))
#    f.write(fig_temp.to_html(full_html=False, include_plotlyjs=False))
#    f.write(fig_humedad.to_html(full_html=False, include_plotlyjs=False))
#    f.write(fig_viento.to_html(full_html=True, include_plotlyjs=False))

with open(html_path, "w", encoding="utf-8") as f:
    # Incluir KPIs
    f.write(dashboard.to_html(full_html=False, include_plotlyjs='cdn'))

    # Incluir gráficos de línea
    f.write(fig_temp.to_html(full_html=False, include_plotlyjs=False))
    f.write(fig_humedad.to_html(full_html=False, include_plotlyjs=False))
    f.write(fig_viento.to_html(full_html=False, include_plotlyjs=False))

    # Incluir mapas de temperatura máxima y mínima (mes = "Todos")
    for tipo in ["TEMPERATURA MÁXIMA (°C)", "TEMPERATURA MÍNIMA (°C)"]:
        df_temp = df[df["VALOR MEDIO DE"] == tipo].copy()
        df_temp = df_temp.dropna(subset=["VALOR LIMPIO", "LATITUD", "LONGITUD", "ESTACIÓN"])
        if df_temp.empty:
            continue

        df_temp["VALOR SIZE"] = df_temp["VALOR LIMPIO"].abs()

        fig_map = px.scatter_map(df_temp,
                                 lat="LATITUD", lon="LONGITUD",
                                 color="VALOR LIMPIO", size="VALOR SIZE",
                                 hover_name="ESTACIÓN",
                                 zoom=4, height=500,
                                 title=f"Mapa de temperatura {tipo.split()[1]} - Todos")
        fig_map.update_layout(mapbox_style="open-street-map")

        f.write(fig_map.to_html(full_html=False, include_plotlyjs=False))

print(f"\n✅ Dashboard completo generado en: {html_path}")


print(f"\n✅ Dashboard generado en: {html_path}")
