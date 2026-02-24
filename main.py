import streamlit as st
import pandas as pd
import unicodedata
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="centered")

# 2. ESTILO CSS PARA EL BOTÓN AZUL Y DISEÑO MÓVIL
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* FORZADO DEL BOTÓN AZUL POLICIAL */
    button[kind="primaryFormSubmit"] {
        background-color: #004488 !important;
        color: white !important;
        width: 100% !important;
        border: none !important;
        height: 3.5rem !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2) !important;
        transition: background-color 0.3s !important;
    }
    
    button[kind="primaryFormSubmit"]:hover {
        background-color: #002244 !important;
    }

    /* Ajuste caja de texto */
    .stTextInput>div>div>input {
        height: 3.5rem;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# Función para limpiar texto
def limpiar(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').lower()

# Función para convertir enlace de Google Sheets a Excel
def obtener_enlace_excel(url):
    if "pubhtml" in url:
        return url.replace("pubhtml", "pub?output=xlsx")
    elif "edit" in url:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if match:
            return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=xlsx"
    return url

# 3. CARGA DE DATOS
# SUSTITUYE AQUÍ TU ENLACE
url_input = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"

st.title("🛡️ Sistema de Consulta Operativa")

try:
    enlace_final = obtener_enlace_excel(url_input)
    # Carga el Excel (requiere openpyxl en requirements.txt)
    df = pd.read_excel(enlace_final)
    df.columns = df.columns.str.lower().str.strip()

    # 4. BUSCADOR (Formulario para móvil)
    with st.form(key='buscador_policial'):
        query = st.text_input("¿Qué hecho quieres consultar?", placeholder="ej: alcohol penal, vmp acera...")
        boton_enviar = st.form_submit_button(label='🔍 BUSCAR AHORA')

    if query:
        query_limpia = limpiar(query)
        palabras_clave = query_limpia.split()

        def filtro_inteligente(fila):
            # Busca en columnas 'tema' y 'busqueda'
            texto_fila = limpiar(str(fila['tema']) + " " + str(fila['busqueda']))
            return all(p in texto_fila for p in palabras_clave)

        res = df[df.apply(filtro_inteligente, axis=1)]

        if not res.empty:
            st.caption(f"Resultados encontrados: {len(res)}")
            for _, row in res.iterrows():
                # Detectamos si es penal por el título
                es_penal = "PENAL" in str(row['tema']).upper()
                
                # Formato de tarjeta
                with st.expander(f"{'🚨' if es_penal else '✅'} {str(row['tema']).upper()}", expanded=es_penal):
                    if es_penal:
                        st.error("⚠️ CASO PENAL: Confeccionar boletín municipal y añadir Diligencia de Paralización.")
                    
                    st.markdown("#### 📋 Protocolo de Actuación")
                    st.info(row['protocolo'])
                    
                    st.markdown("#### ⚖️ Precepto y Sanción")
                    st.code(row['denuncia'], language=None)
                    
                    # Columna de Diligencias (si existe en el Excel)
                    if 'diligencia' in row and pd.notna(row['diligencia']):
                        st.markdown("#### ✍️ Diligencia Tipo (Copiar para Atestado)")
                        st.code(row['diligencia'], language=None)
        else:
            st.warning("No se han encontrado protocolos. Intenta con palabras sueltas (ej: itv).")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    st.info("Revisa que el enlace de Google Sheets sea correcto y que las columnas se llamen: tema, busqueda, protocolo, denuncia, diligencia.")
