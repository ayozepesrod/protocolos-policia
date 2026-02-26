import streamlit as st
import pandas as pd
import unicodedata
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="wide")

# 2. ESTILO CSS ACTUALIZADO
st.markdown("""
    <style>
    /* Ocultar elementos nativos */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}

    /* Subir el contenido al borde superior */
    .block-container {
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important;
        margin-top: -30px; 
    }

    /* Estilo del título */
    .titulo {
        margin: 0;
        padding: 10px 0;
        font-size: 2.5rem;
        color: #004488;
        text-align: center;
    }

    /* AJUSTE DEL BOTÓN "OJO" (VER CONTRASEÑA) */
    /* Lo hacemos más pequeño y lo desplazamos un poco a la derecha */
    button[aria-label="Show password"] {
        transform: scale(0.7); /* Reduce el tamaño al 70% */
        margin-right: -10px;    /* Lo pega más al borde derecho */
        opacity: 0.7;          /* Lo hace un poco más sutil */
    }

    /* Estilo para el formulario */
    div[data-testid="stForm"] {
        margin-top: 10px;
    }

    div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
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

    /* Estilo de los inputs */
    div[data-testid="stTextInput"] input {
        height: 4rem !important;
        background-color: #e0e0e0 !important; /* Gris un poco más suave */
        border-radius: 12px !important; 
    }
    </style>
""", unsafe_allow_html=True)

# 3. TÍTULO
st.markdown("<h1 class='titulo'>🛡️ Sistema de Consulta Operativa</h1>", unsafe_allow_html=True)

# 4. FUNCIONES
def limpiar(t):
    if not t: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').lower()

def obtener_enlace_csv(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=csv"
    return url

# 5. URLS
url_protocolos = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"
url_usuarios = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"

# 6. LÓGICA
try:
    enlace_final = obtener_enlace_csv(url_protocolos)

    @st.cache_data(ttl=300)
    def cargar_datos(url):
        return pd.read_csv(url)

    @st.cache_data(ttl=300)
    def cargar_usuarios(url):
        return pd.read_csv(obtener_enlace_csv(url))

    df = cargar_datos(enlace_final)
    usuarios_df = cargar_usuarios(url_usuarios)

    # Formulario
    with st.form(key='login_form'):
        nombre = st.text_input("Nombre")
        contrasena = st.text_input("Contraseña", type="password")
        login_button = st.form_submit_button(label='Iniciar Sesión')

    if login_button:
        usuario = usuarios_df[(usuarios_df['nombre'].astype(str) == nombre) & 
                             (usuarios_df['contraseña'].astype(str) == contrasena)]
        
        if not usuario.empty:
            st.success("Inicio de sesión exitoso")
        else:
            st.error("Credenciales incorrectas")

except Exception as e:
    st.error(f"Error crítico: {e}")
