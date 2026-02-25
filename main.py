import streamlit as st
import pandas as pd
import unicodedata
import re

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="centered")

# ESTILO CSS
st.markdown("""
    <style>
    #MainMenu, footer, header, .stDeployButton {display:none !important;}
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
    div[data-testid="stForm"] button:active { background-color: #002244 !important; }
    div[data-testid="stTextInput"] input { height: 3.5rem !important; border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

def limpiar(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').lower()

def obtener_enlace_excel(url):
    if "pubhtml" in url: return url.replace("pubhtml", "pub?output=xlsx")
    elif "edit" in url:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if match: return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=xlsx"
    return url

# URL DE TU GOOGLE SHEETS
url_input = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"

st.title("🛡️ Sistema de Consulta Operativa")

try:
    enlace_final = obtener_enlace_excel(url_input)
    df = pd.read_excel(enlace_final)
    # Estandarizar nombres de columnas: minúsculas, sin tildes, sin espacios
    df.columns = [limpiar(col).replace(" ", "_") for col in df.columns]

    with st.form(key='buscador_policial'):
        query = st.text_input("¿Qué hecho quieres consultar?", placeholder="ej: vmp seguro, alcohol...")
        st.form_submit_button(label='🔍 BUSCAR AHORA')

    if query:
        query_limpia = limpiar(query)
        palabras_clave = query_limpia.split()

        def filtro_inteligente(fila):
            texto_fila = limpiar(str(fila.get('tema', '')) + " " + str(fila.get('busqueda', '')))
            return all(p in texto_fila for p in palabras_clave)

        res = df[df.apply(filtro_inteligente, axis=1)]

        if not res.empty:
            st.caption(f"Resultados encontrados: {len(res)}")
            for _, row in res.iterrows():
                tema_val = str(row.get('tema', 'SIN TÍTULO')).upper()
                es_penal = "PENAL" in tema_val
                
                with st.expander(f"{'🚨' if es_penal else '✅'} {tema_val}", expanded=False):
                    if es_penal:
                        st.error("⚠️ CASO PENAL: Instruir Atestado y paralizar vía administrativa.")
                    
                    st.markdown("#### 📋 Protocolo de Actuación")
                    st.info(row.get('protocolo', 'Información no disponible'))
                    
                    st.markdown("#### ⚖️ Precepto y Sanción")
                    st.code(row.get('denuncia', 'No definido'), language=None)
                    
                    # Columna de Medida Cautelar
                    medida = row.get('medida_cautelar')
                    if pd.notna(medida) and str(medida).strip() != "":
                        st.markdown("#### 🚧 Medida Cautelar")
                        if any(x in str(medida).upper() for x in ["INMOVILIZ", "RETIRADA", "DEPOSITO"]):
                            st.warning(f"⚠️ {medida}")
                        else:
                            st.write(f"👉 {medida}")
                    
                    # Columna de Diligencia
                    diligencia = row.get('diligencia')
                    if pd.notna(diligencia) and str(diligencia).strip() != "":
                        st.markdown("#### ✍️ Diligencia Tipo")
                        st.code(diligencia, language=None)
        else:
            st.warning("No se han encontrado protocolos.")

except Exception as e:
    st.error(f"Error crítico en el sistema: {e}")
    st.info("Revisa que el Excel tenga las columnas: tema, busqueda, protocolo, denuncia, medida_cautelar, diligencia")
