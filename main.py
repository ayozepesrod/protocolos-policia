import streamlit as st
import pandas as pd
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="centered")

# ESTILO CSS (Incluye el botón y la interfaz del móvil)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Estilo para el botón de buscar */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #004488;
        color: white;
        font-weight: bold;
        border: none;
    }
    
    /* Espaciado del buscador en móvil */
    .stTextInput>div>div>input {
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# Función de limpieza de tildes y mayúsculas
def limpiar(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').lower()

# 2. CARGA DE DATOS (Pega aquí tu enlace de Google Sheets compartido como "Cualquier persona")
url_input = "TU_ENLACE_DE_GOOGLE_SHEETS_AQUI"

def obtener_enlace_excel(url):
    if "pubhtml" in url:
        return url.replace("pubhtml", "pub?output=xlsx")
    elif "edit" in url:
        import re
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if match:
            return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=xlsx"
    return url

st.title("🛡️ Sistema de Consulta Operativa")

try:
    enlace_final = obtener_enlace_excel(url_input)
    # Importante: Asegúrate de tener openpyxl en requirements.txt
    df = pd.read_excel(enlace_final)
    df.columns = df.columns.str.lower().str.strip()

    # 3. BUSCADOR CON FORMULARIO (Botón + Enter)
    # Usamos un formulario para que el botón de enviar sea explícito
    with st.form(key='mi_buscador', clear_on_submit=False):
        query = st.text_input("Escribe el hecho (ej: alcohol 0.60):")
        boton_enviar = st.form_submit_button(label='🔍 BUSCAR AHORA')

    # La búsqueda se dispara al dar al botón O al dar a Enter
    if query:
        query_limpia = limpiar(query)
        palabras_clave = query_limpia.split()

        def filtro_inteligente(fila):
            texto_fila = limpiar(str(fila['tema']) + " " + str(fila['busqueda']))
            return all(p in texto_fila for p in palabras_clave)

        res = df[df.apply(filtro_inteligente, axis=1)]

        if not res.empty:
            st.caption(f"Resultados encontrados: {len(res)}")
            for _, row in res.iterrows():
                es_penal = "PENAL" in str(row['tema']).upper()
                
                with st.expander(f"{'🚨' if es_penal else '✅'} {str(row['tema']).upper()}", expanded=es_penal):
                    if es_penal:
                        st.error("⚠️ CASO PENAL: Recordar diligencia de paralización del boletín municipal.")
                    
                    st.markdown("#### 📋 Protocolo de Actuación")
                    st.info(row['protocolo'])
                    
                    st.markdown("#### ⚖️ Precepto y Sanción")
                    st.code(row['denuncia'], language=None)
                    
                    if 'diligencia' in row and pd.notna(row['diligencia']):
                        st.markdown("#### ✍️ Diligencia Tipo")
                        st.code(row['diligencia'], language=None)
        else:
            st.warning("No se han encontrado protocolos con esos términos.")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
