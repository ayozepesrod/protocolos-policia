import streamlit as st
import pandas as pd
import unicodedata
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="centered")

# 2. INYECCIÓN DE ESTILO RADICAL (Forzado directo)
st.markdown(
    """
    <style>
    /* Ocultar elementos innecesarios */
    #MainMenu, footer, header, .stDeployButton {display:none !important;}

    /* FORZAR AZUL EN EL BOTÓN DE FORMULARIO */
    div[data-testid="stForm"] button {
        background-color: #004488 !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1rem !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.8rem !important;
        font-size: 1.2rem !important;
        cursor: pointer !important;
    }

    /* Cambio de color al pulsar (Efecto táctil) */
    div[data-testid="stForm"] button:active, div[data-testid="stForm"] button:hover {
        background-color: #002244 !important;
        color: #ffffff !important;
    }

    /* Estilo de la caja de texto */
    div[data-testid="stTextInput"] input {
        height: 3.5rem !important;
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def limpiar(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').lower()

def obtener_enlace_excel(url):
    if "pubhtml" in url:
        return url.replace("pubhtml", "pub?output=xlsx")
    elif "edit" in url:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if match:
            return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=xlsx"
    return url

# 3. CARGA DE DATOS
url_input = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"

st.title("🛡️ Sistema de Consulta Operativa")

try:
    enlace_final = obtener_enlace_excel(url_input)
    df = pd.read_excel(enlace_final)
    df.columns = df.columns.str.lower().str.strip()

    # 4. BUSCADOR (Formulario)
    with st.form(key='buscador_policial'):
        query = st.text_input("¿Qué hecho quieres consultar?", placeholder="ej: alcohol penal, vmp acera...")
        # El botón de Streamlit hereda el estilo CSS de arriba por el data-testid
        st.form_submit_button(label='🔍 BUSCAR AHORA')

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
                with st.expander(f"{'🚨' if es_penal else '✅'} {str(row['tema']).upper()}", expanded=False):
                    if es_penal:
                        st.error("⚠️ CASO PENAL: Confeccionar boletín municipal y añadir Diligencia de Paralización.")
                    st.markdown("#### 📋 Protocolo de Actuación")
                    st.info(row['protocolo'])
                    st.markdown("#### ⚖️ Precepto y Sanción")
                    st.code(row['denuncia'], language=None)
                    if 'diligencia' in row and pd.notna(row['diligencia']):
                        st.markdown("#### ✍️ Diligencia Tipo (Copiar para Atestado)")
                        st.code(row['diligencia'], language=None)
        else:
            st.warning("No se han encontrado protocolos.")

except Exception as e:
    st.error(f"Error técnico: {e}")
