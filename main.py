import streamlit as st
import pandas as pd
import unicodedata
import re

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="wide")

# 2. ESTILO CSS (Título arriba, inputs limpios y botón de contraseña pequeño)
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}

    /* Eliminar el espacio superior del contenedor principal */
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

    /* Ajuste del botón "ojo" (ver contraseña) para que sea más pequeño y discreto */
    button[aria-label="Show password"] {
        transform: scale(0.7); /* Reduce el tamaño */
        margin-right: -10px;    /* Lo desplaza a la derecha */
        opacity: 0.6;          /* Lo hace más tenue */
    }

    /* Estilo para el formulario */
    div[data-testid="stForm"] {
        margin-top: 15px;
        border: 1px solid #ddd;
        padding: 2rem;
        border-radius: 15px;
    }

    /* Estilo del botón de acceso */
    div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
        background-color: #004488 !important;
        color: white !important;
        border-radius: 12px !important;
        width: 100% !important;
        height: 3.8rem !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
    
    div[data-testid="stForm"] button:active { background-color: #002244 !important; }

    /* Estilo de los cuadros de texto */
    div[data-testid="stTextInput"] input {
        height: 3.5rem !important;
        background-color: #f0f2f6 !important;
        border-radius: 10px !important; 
    }
    </style>
""", unsafe_allow_html=True)

# 3. TÍTULO (Pegado a la parte superior)
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

# 5. URLS DE GOOGLE SHEETS
url_base = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit?usp=sharing"

# 6. LÓGICA DE CARGA Y LOGIN
try:
    @st.cache_data(ttl=300)
    def cargar_usuarios(url):
        # Cargamos la hoja que contiene la tabla de usuarios
        return pd.read_csv(obtener_enlace_csv(url))

    usuarios_df = cargar_usuarios(url_base)

    # Formulario de Inicio de Sesión
    with st.form(key='login_form'):
        st.subheader("Acceso de Usuario")
        nombre_input = st.text_input("Nombre de Usuario")
        contrasena_input = st.text_input("Contraseña", type="password")
        login_button = st.form_submit_button(label='ENTRAR')

    if login_button:
        # Validamos nombre y contraseña ignorando mayúsculas/minúsculas en el nombre
        # Asegúrate de que las columnas en tu Excel se llamen exactamente 'nombre' y 'contraseña'
        usuario_encontrado = usuarios_df[
            (usuarios_df['nombre'].astype(str).str.strip().str.lower() == nombre_input.strip().lower()) & 
            (usuarios_df['contraseña'].astype(str) == contrasena_input)
        ]
        
        if not usuario_encontrado.empty:
            # Si hay duplicados de nombre, el sistema ahora puede usar el ID interno 
            # para saber exactamente quién entró
            id_real = usuario_encontrado.iloc[0]['id']
            nombre_real = usuario_encontrado.iloc[0]['nombre']
            
            st.success(f"Sesión iniciada: {nombre_real} (ID: {id_real})")
            # Aquí iría el resto de tu programa (buscador de protocolos)
        else:
            st.error("Usuario o contraseña incorrectos")

except Exception as e:
    st.error(f"Error de conexión: {e}")
