import streamlit as st
import pandas as pd
import unicodedata
import re

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="wide")

# ESTILO CSS ACTUALIZADO
st.markdown("""
    <style>
    /* Ocultar elementos de la interfaz de Streamlit */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}

    /* ELIMINAR ESPACIO SUPERIOR (Padding del contenedor principal) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 95%;
    }

    /* Ajuste del título */
    .titulo {
        margin: 0;
        padding: 0;
        font-size: 2.5rem;
        color: #004488;
        text-align: center;
        /* Eliminamos el 'top: -20px' anterior para usar el padding del contenedor */
    }

    div[data-testid="stForm"] {
        margin-top: 20px;
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

    div[data-testid="stTextInput"] input {
        height: 4rem !important;
        background-color: #d3d3d3 !important;
        border-radius: 12px !important; 
    }
    </style>
""", unsafe_allow_html=True)

# TÍTULO PERSONALIZADO (Ahora estará pegado arriba)
st.markdown("<h1 class='titulo'>🛡️ Sistema de Consulta Operativa</h1>", unsafe_allow_html=True)

# --- RESTO DE TU CÓDIGO (Funciones y Lógica) ---
# ... (Mantén aquí el resto de tus funciones y el formulario de login)
