import streamlit as st
import pandas as pd
import unicodedata

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="centered")

# ESTILO PARA OCULTAR MENÚS Y MEJORAR INTERFAZ
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    background-color: #004488;
    color: white;
}
    </style>
    """, unsafe_allow_html=True)

# Función de limpieza de tildes y mayúsculas
def limpiar(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').lower()

# 2. CARGA DE DATOS (Pega tu enlace de Google Sheets aquí)
# Puede ser el enlace de "Publicar en la web" o el de "Compartir"
url_input = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"

# TRUCO TÉCNICO: Convertimos el enlace normal en un enlace de descarga de Excel
def obtener_enlace_excel(url):
    if "pubhtml" in url:
        return url.replace("pubhtml", "pub?output=xlsx")
    elif "edit" in url:
        import re
        # Extrae el ID de la hoja de cálculo
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if match:
            return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=xlsx"
    return url

st.title("🛡️ Sistema de Consulta Operativa")

try:
    # Leemos el Excel directamente
    enlace_final = obtener_enlace_excel(url_input)
    df = pd.read_excel(enlace_final)
    
    # Limpiamos nombres de columnas (quita espacios y pone minúsculas)
    df.columns = df.columns.str.lower().str.strip()

    # 3. BUSCADOR
    # 3. BUSCADOR CON BOTÓN FÍSICO
    with st.form(key='buscador_form'):
        col1, col2 = st.columns([0.8, 0.2]) # Dividimos la fila para que el botón esté al lado o debajo
        
        with col1:
            query = st.text_input("Buscar concepto (ej: alcohol 0.60):", key="input_text")
        
        with col2:
            # Añadimos un espacio para alinear el botón con el input en PC, 
            # en móvil se verá uno sobre otro o ajustado
            st.write(" ") 
            submit_button = st.form_submit_button(label='🔍 BUSCAR')

    # La lógica se ejecuta si se pulsa Enter O si se pulsa el botón
    if query:
        query_limpia = limpiar(query)
        palabras_clave = query_limpia.split()

        def filtro_inteligente(fila):
            # Busca en las columnas 'tema' y 'busqueda'
            texto_fila = limpiar(str(fila['tema']) + " " + str(fila['busqueda']))
            return all(p in texto_fila for p in palabras_clave)

        res = df[df.apply(filtro_inteligente, axis=1)]

        if not res.empty:
            st.caption(f"Encontrados {len(res)} protocolos:")
            for _, row in res.iterrows():
                # Detección de casos penales por el título
                es_penal = "PENAL" in str(row['tema']).upper()
                
                with st.expander(f"{'🚨' if es_penal else '✅'} {str(row['tema']).upper()}", expanded=es_penal):
                    if es_penal:
                        st.error("⚠️ CASO PENAL: Recordar diligencia de paralización del boletín municipal.")
                    
                    st.markdown("#### 📋 Protocolo de Actuación")
                    st.info(row['protocolo'])
                    
                    st.markdown("#### ⚖️ Precepto y Sanción")
                    st.code(row['denuncia'], language=None)
                    
                    if 'diligencia' in row and pd.notna(row['diligencia']):
                        st.markdown("#### ✍️ Diligencia Tipo (Copiar para Atestado)")
                        st.code(row['diligencia'], language=None)
        else:
            st.warning("No hay resultados exactos. Prueba con términos más simples.")

except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")
    st.info("Asegúrate de haber puesto un enlace válido de Google Sheets y que las columnas se llamen: tema, busqueda, protocolo, denuncia, diligencia.")
