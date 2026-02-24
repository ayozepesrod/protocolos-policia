import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA (Esto debe ir SIEMPRE primero)
st.set_page_config(page_title="Protocolos Policiales", layout="centered")

# 2. OCULTAR MENÚS Y ESTILOS (Corregido)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Guía Operativa Policial")

# 3. CONEXIÓN A TU GOOGLE SHEETS
# Sustituye lo que hay entre comillas por tu enlace .csv de Google Sheets
url_gsheets = https://docs.google.com/spreadsheets/d/e/2PACX-1vSayq81IwpszZ9-bjhssGEKBv8C-GUPA1HTyn8UE98M1elo9Xqmw71vwdpxCWdsx8V7V9OOgYDrT5Yv/pub?output=csv

try:
    # Cargamos los datos
    df = pd.read_csv(url_gsheets)
    
    # 4. BUSCADOR
    query = st.text_input("Escribe el hecho o palabras clave (ej: novel alcohol):").lower()

    if query:
        palabras = query.split()
        # Filtra si TODAS las palabras buscadas están en 'tema' o 'busqueda'
        mask = df.apply(lambda r: all(p in (str(r['tema']) + str(r['busqueda'])).lower() for p in palabras), axis=1)
        res = df[mask]

        if not res.empty:
            for _, row in res.iterrows():
                with st.expander(f"✅ {row['tema']}", expanded=True):
                    st.subheader("📋 Protocolo")
                    st.write(row['protocolo'])
                    st.subheader("⚖️ Denuncia")
                    st.code(row['denuncia'], language=None)
                    st.caption("Selecciona el texto superior para copiarlo")
        else:
            st.error("No se encontraron resultados para esa combinación.")
            
except Exception as e:
    st.error("Configuración pendiente: Por favor, conecta el enlace CSV de tu Google Sheets.")
    # Esto es solo para que no de error feo si aún no has puesto el link
