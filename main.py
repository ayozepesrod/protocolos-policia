import streamlit as st
import pandas as pd
import unicodedata
import re

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="centered")

# ESTILO CSS MEJORADO
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
    /* Estilo para resaltar la medida cautelar */
    .medida-alerta {
        padding: 10px;
        border-radius: 10px;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        color: #856404;
        font-weight: bold;
    }
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
    # Cargar datos y forzar nombres de columnas a minúsculas
    df = pd.read_excel(enlace_final)
    df.columns = df.columns.str.lower().str.strip()

    with st.form(key='buscador_policial'):
        query = st.text_input("¿Qué hecho quieres consultar?", placeholder="ej: vmp seguro, alcohol, drogas...")
        st.form_submit_button(label='🔍 BUSCAR AHORA')

    if query:
        query_limpia = limpiar(query)
        palabras_clave = query_limpia.split()

        def filtro_inteligente(fila):
            # Combina tema y busqueda para filtrar
            texto_fila = limpiar(str(fila.get('tema', '')) + " " + str(fila.get('busqueda', '')))
            return all(p in texto_fila for p in palabras_clave)

        res = df[df.apply(filtro_inteligente, axis=1)]

        if not res.empty:
            st.caption(f"Resultados encontrados: {len(res)}")
            for _, row in res.iterrows():
                # Detectar si el tema indica un caso penal
                tema_texto = str(row.get('tema', 'SIN TÍTULO')).upper()
                es_penal = "PENAL" in tema_texto
                
                with st.expander(f"{'🚨' if es_penal else '✅'} {tema_texto}", expanded=False):
                    if es_penal:
                        st.error("⚠️ CASO PENAL: Seguir protocolo de Atestado y paralizar sanción administrativa.")
                    
                    # 1. PROTOCOLO
                    st.markdown("#### 📋 Protocolo de Actuación")
                    st.info(row.get('protocolo', 'No definido'))
                    
                    # 2. DENUNCIA
                    st.markdown("#### ⚖️ Precepto y Sanción")
                    st.code(row.get('denuncia', 'No definido'), language=None)
                    
                    # 3. MEDIDA CAUTELAR (Nueva columna)
                    medida = row.get('medida_cautelar')
                    if pd.notna(medida) and str(medida).strip() != "":
                        st.markdown("#### 🚧 Medida Cautelar")
                        if "INMOVILIZ" in str(medida).upper() or "RETIRADA" in str(medida).upper() or "DEPOSITO" in str(medida).upper():
                            st.warning(f"⚠️ {medida}")
                        else:
                            st.write(f"👉 {medida}")
                    
                    #
