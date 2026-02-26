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
    .titulo { margin: 0; padding: 10px 0; font-size: 2.5rem; color: #004488; text-align: center; }
    button[aria-label="Show password"] { transform: scale(0.7); margin-right: -10px; opacity: 0.6; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🛡️ Sistema de Consulta Operativa</h1>", unsafe_allow_html=True)

# 3. FUNCIONES
def limpiar_texto(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').lower()

def obtener_enlace_csv(url, gid="0"):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        doc_id = match.group(1)
        return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={gid}"
    return url

# --- CONFIGURACIÓN DE HOJAS ---
URL_DOCUMENTO = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit"
GID_PROTOCOLOS = "0"
GID_USUARIOS = "142130076" 

# 4. CARGA DE DATOS Y LOGICA
try:
    @st.cache_data(ttl=300)
    def cargar_datos(url, gid):
        enlace = obtener_enlace_csv(url, gid)
        df = pd.read_csv(enlace)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df

    usuarios_df = cargar_datos(URL_DOCUMENTO, GID_USUARIOS)
    protocolos_df = cargar_datos(URL_DOCUMENTO, GID_PROTOCOLOS)

    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    # --- LOGIN ---
    if not st.session_state['autenticado']:
        with st.form(key='login_form'):
            st.subheader("Acceso de Usuario")
            nombre_input = st.text_input("Nombre de Usuario")
            contrasena_input = st.text_input("Contraseña", type="password")
            login_button = st.form_submit_button(label='ENTRAR')

        if login_button:
            usuario_encontrado = usuarios_df[
                (usuarios_df['nombre'].astype(str).str.strip().str.lower() == nombre_input.strip().lower()) & 
                (usuarios_df['contraseña'].astype(str).str.strip() == str(contrasena_input).strip())
            ]
            
            if not usuario_encontrado.empty:
                st.session_state['autenticado'] = True
                st.session_state['usuario_nombre'] = usuario_encontrado.iloc[0]['nombre']
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    # --- PANTALLA PRINCIPAL TRAS LOGIN ---
    else:
        col_user, col_logout = st.columns([0.8, 0.2])
        col_user.success(f"Bienvenido/a, {st.session_state['usuario_nombre']}")
        if col_logout.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

        # Buscador
        busqueda = st.text_input("🔍 Buscar protocolo...")

        if busqueda:
            termino = limpiar_texto(busqueda)
            # Filtra en todas las columnas
            resultado = protocolos_df[
                protocolos_df.apply(lambda row: termino in limpiar_texto(' '.join(row.astype(str))), axis=1)
            ]

            if not resultado.empty:
                st
