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

    /* Ajuste del margen superior para el título */
    .titulo {
        margin-top: 10px; /* Ajusta este valor según lo necesites */
        font-size: 2.5rem; /* Tamaño del texto */
        color: #004488; /* Color del texto */
        text-align: center; /* Centrando el texto */
    }

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
    
    /* Estilo general para los campos de entrada */
    div[data-testid="stTextInput"] {
        margin-bottom: 1rem; /* Espaciado entre campos, ajustable */
    }

    div[data-testid="stTextInput"] input {
        height: 4rem !important; /* Aumenta la altura del cuadro de texto */
        background-color: #d3d3d3 !important; /* Color gris claro */
        border-radius: 12px !important; 
    }

    /* Mejora del botón 'Ver Contraseña' */
    div[data-testid="stTextInput"] div {
        display: inline; 
        color: #666; 
        cursor: pointer; 
        font-size: 0.9rem; 
        padding: 0; 
        background-color: transparent; 
        vertical-align: middle; /* Alinear verticalmente */
    }
    
    div[data-testid="stTextInput"] div:hover {
        color: #004488; 
    }
    </style>
""", unsafe_allow_html=True)

# TÍTULO PERSONALIZADO
st.markdown("<h1 class='titulo'>🛡️ Sistema de Consulta Operativa</h1>", unsafe_allow_html=True)

# FUNCIONES
def limpiar(t):
    if not t:
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(t))
                  if unicodedata.category(c) != 'Mn').lower()

def obtener_enlace_csv(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=csv"
    return url

# URL GOOGLE SHEETS
url_protocolos = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"
url_usuarios = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"

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

    # Formulario de Inicio de Sesión
    with st.form(key='login_form'):
        nombre = st.text_input("Nombre")
        contrasena = st.text_input("Contraseña", type="password")
        login_button = st.form_submit_button(label='Iniciar Sesión')

    if login_button:
        usuario = usuarios_df[(usuarios_df['nombre'] == nombre) & (usuarios_df['contraseña'] == contrasena)]
        
        if not usuario.empty:
            st.success("Inicio de sesión exitoso")
            # Lógica de búsqueda y protocolos...

        else:
            st.error("Credenciales incorrectas")

except Exception as e:
    st.error(f"Error crítico en el sistema: {e}")
    st.info("Verifica conexión con Google Sheets y estructura del archivo.")
