import streamlit as st
import pandas as pd
import unicodedata
import re

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="wide")

# 2. ESTILO CSS
st.markdown("""
    <style>
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    .block-container { padding-top: 0rem !important; margin-top: -30px; }
    .titulo { margin: 0; padding: 10px 0; font-size: 2.5rem; color: #004488; text-align: center; font-weight: bold; }
    .seccion-header {
        color: #004488;
        font-weight: bold;
        border-bottom: 1px solid #ddd;
        margin-top: 10px;
        margin-bottom: 5px;
        font-size: 1.1rem;
    }
    .dato-importante {
        background-color: #e8f0f7;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        color: #d32f2f;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🛡️ Sistema de Consulta Operativa</h1>", unsafe_allow_html=True)

# 3. FUNCIONES
def limpiar_texto(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t).strip())
                  if unicodedata.category(c) != 'Mn').lower()

def obtener_enlace_csv(url, gid="0"):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        doc_id = match.group(1)
        return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={gid}"
    return url

# --- 4. CARGA DE DATOS ---
URL_DOCUMENTO = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit"
GID_PROTOCOLOS = "0"
GID_USUARIOS = "142130076" 

try:
    @st.cache_data(ttl=300)
    def cargar_datos(url, gid):
        enlace = obtener_enlace_csv(url, gid)
        df = pd.read_csv(enlace).fillna("")
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df

    usuarios_df = cargar_datos(URL_DOCUMENTO, GID_USUARIOS)
    protocolos_df = cargar_datos(URL_DOCUMENTO, GID_PROTOCOLOS)

    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    # --- 5. LOGIN ---
    if not st.session_state['autenticado']:
        with st.form(key='login_form'):
            st.subheader("Acceso de Usuario")
            nombre_input = st.text_input("Nombre de Usuario")
            # AQUÍ ESTABA EL ERROR (Línea 72)
            contrasena_input = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button(label='ENTRAR'):
                user = usuarios_df[
                    (usuarios_df['nombre'].astype(str).str.lower() == nombre_input.lower().strip()) & 
                    (usuarios_df['contraseña'].astype(str) == contrasena_input.strip())
                ]
                if not user.empty:
                    st.session_state['autenticado'] = True
                    st.session_state['usuario_nombre'] = user.iloc[0]['nombre']
                    st.rerun()
                else: 
                    st.error("Credenciales incorrectas")

    # --- 6. BUSCADOR Y RESULTADOS ---
    else:
        c1, c2 = st.columns([0.8, 0.2])
        c1.write(f"👤 Agente: **{st.session_state['usuario_nombre']}**")
        if c2.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

        busqueda = st.text_input("🔍 Buscar por infracción, artículo o palabra clave...")

        if busqueda:
            termino = limpiar_texto(busqueda)
            
            def buscar_en_fila(row):
                texto_fila = limpiar_texto(' '.join(row.astype(str)))
                return termino in texto_fila

            resultado = protocolos_df[protocolos_df.apply(buscar_en_fila, axis=1)]

            if not resultado.empty:
                st.write(f
