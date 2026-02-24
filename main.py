import streamlit as st
import pandas as pd
import unicodedata

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️")

# Ocultar menús innecesarios
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# Función de limpieza de tildes y mayúsculas
def limpiar(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').lower()

# 2. CARGA DE DATOS (Pon aquí tu enlace CSV de Google Sheets)
url_gsheets = "TU_ENLACE_AQUI_EL_QUE_TERMINA_EN_CSV"

st.title("🛡️ Sistema de Consulta Operativa")

try:
    df = pd.read_csv(url_gsheets)
    df.columns = df.columns.str.lower().str.strip()

    # 3. BUSCADOR
    query = st.text_input("Buscar por concepto (ej: alcohol penal):")

    if query:
        query_limpia = limpiar(query)
        palabras_clave = query_limpia.split()

        def filtro_inteligente(fila):
            texto_fila = limpiar(str(fila['tema']) + " " + str(fila['busqueda']))
            return all(p in texto_fila for p in palabras_clave)

        res = df[df.apply(filtro_inteligente, axis=1)]

        if not res.empty:
            st.caption(f"Encontrados {len(res)} protocolos:")
            for _, row in res.iterrows():
                # Detección de casos penales para aviso visual
                es_penal = "PENAL" in str(row['tema']).upper()
                
                with st.expander(f"{'🚨' if es_penal else '✅'} {str(row['tema']).upper()}", expanded=es_penal):
                    if es_penal:
                        st.error("⚠️ CASO PENAL: Recordar confeccionar boletín y añadir Diligencia de Paralización.")
                    
                    # Mostrar Protocolo
                    st.markdown("#### 📋 Protocolo de Actuación")
                    st.info(row['protocolo'])
                    
                    # Mostrar Denuncia
                    st.markdown("#### ⚖️ Precepto y Sanción")
                    st.code(row['denuncia'], language=None)
                    
                    # Mostrar Diligencia Tipo (Si existe)
                    if 'diligencia' in row and pd.notna(row['diligencia']):
                        st.markdown("#### ✍️ Diligencia Tipo (Copiar para Atestado)")
                        st.code(row['diligencia'], language=None)
                        st.caption("Toca el cuadro de arriba para copiar el texto")
        else:
            st.warning("No hay resultados. Prueba con palabras sueltas.")

except Exception as e:
    st.error(f"Error técnico: {e}")
