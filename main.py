import streamlit as st
import pandas as pd
import unicodedata
import re

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="wide")

# 2. ESTILO CSS (Mantiene el título arriba y el diseño limpio)
st.markdown("""
    <style>
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    .block-container { padding-top: 0rem !important; margin-top: -30px; }
    .titulo { margin: 0; padding: 10px 0; font-size: 2.5rem; color: #004488; text-align: center; }
    button[aria-label="Show password"] { transform: scale(0.7); margin-right: -10px; opacity: 0.6; }
    div[data-testid="stForm"] { margin-top: 15px; border-radius: 15px; }
    div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
        background-color: #004488 !important; color: white !important;
        border-radius: 12px !important; width: 100% !important; height: 3.8rem !important;
    }
    div[data-testid="stTextInput"] input { height: 3.5rem !important; background-color: #f0f2f6 !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🛡️ Sistema de Consulta Operativa</h1>", unsafe_allow_html=True)

# 3. FUNCIONES DE CARGA Y LIMPIEZA
def obtener_enlace_csv(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=csv"
    return url

@st.cache_data(ttl=300)
def cargar_datos_seguros(url):
    df = pd.read_csv(obtener_enlace_csv(url))
    # LIMPIEZA DE COLUMNAS: Quita espacios y pone todo en minúsculas para evitar el error 'nombre'
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

# 4. LÓGICA DE LOGIN
url_base = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"

# Inicializar estado de autenticación
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

try:
    usuarios_df = cargar_datos_seguros(url_base)

    if not st.session_state['autenticado']:
        with st.form(key='login_form'):
            st.subheader("Acceso de Usuario")
            nombre_input = st.text_input("Nombre de Usuario")
            contrasena_input = st.text_input("Contraseña", type="password")
            login_button = st.form_submit_button(label='ENTRAR')

        if login_button:
            # Buscamos de forma robusta
            usuario_encontrado = usuarios_df[
                (usuarios_df['nombre'].astype(str).str.strip().str.lower() == nombre_input.strip().lower()) & 
                (usuarios_df['contraseña'].astype(str).str.strip() == contrasena_input.strip())
            ]
            
            if not usuario_encontrado.empty:
                st.session_state['autenticado'] = True
                st.session_state['usuario_nombre'] = usuario_encontrado.iloc[0]['nombre']
                st.rerun() # Recarga la página para quitar el formulario
            else:
                st.error("Usuario o contraseña incorrectos")
    else:
        # --- ESTO SE MUESTRA CUANDO YA ESTÁ LOGUEADO ---
        st.success(f"Bienvenido/a, {st.session_state['usuario_nombre']}")
        if st.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()
        
        # Aquí puedes poner tu buscador de protocolos
        st.info("Aquí aparecerá el buscador de protocolos...")

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Asegúrate de que la columna se llame 'nombre' en tu Excel.")
