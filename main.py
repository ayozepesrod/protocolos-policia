import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="wide")

# 2. ESTILO CSS (Título arriba y diseño limpio)
st.markdown("""
    <style>
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    .block-container { padding-top: 0rem !important; margin-top: -30px; }
    .titulo { margin: 0; padding: 10px 0; font-size: 2.5rem; color: #004488; text-align: center; }
    button[aria-label="Show password"] { transform: scale(0.7); margin-right: -10px; opacity: 0.6; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🛡️ Sistema de Consulta Operativa</h1>", unsafe_allow_html=True)

# 3. FUNCIÓN PARA OBTENER HOJAS ESPECÍFICAS
def obtener_enlace_csv(url, gid="0"):
    # Extrae el ID del documento
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        doc_id = match.group(1)
        # Retorna el enlace forzando el GID de la hoja
        return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={gid}"
    return url

# --- CONFIGURACIÓN DE TUS HOJAS ---
# Pon aquí el enlace principal de tu archivo
URL_DOCUMENTO = "https://docs.google.com/spreadsheets/d/1soQluu2y1XMFGuN-Qur6084EcbqLBNd7aq1nql_TS9Y/edit"

# BUSCA ESTOS NÚMEROS EN TU NAVEGADOR AL PINCHAR EN CADA PESTAÑA:
GID_PROTOCOLOS = "0"          # Normalmente la primera hoja es 0
GID_USUARIOS = "142130076"    # <--- CAMBIA ESTE NÚMERO por el que veas en la pestaña de usuarios

# 4. CARGA DE DATOS
try:
    @st.cache_data(ttl=300)
    def cargar_datos(url, gid):
        enlace = obtener_enlace_csv(url, gid)
        df = pd.read_csv(enlace)
        df.columns = [str(c).strip().lower() for c in df.columns] # Limpia nombres de columnas
        return df

    # Cargamos cada hoja por separado
    usuarios_df = cargar_datos(URL_DOCUMENTO, GID_USUARIOS)
    protocolos_df = cargar_datos(URL_DOCUMENTO, GID_PROTOCOLOS)

    # 5. LÓGICA DE LOGIN
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        with st.form(key='login_form'):
            st.subheader("Acceso de Usuario")
            nombre_input = st.text_input("Nombre de Usuario")
            contrasena_input = st.text_input("Contraseña", type="password")
            login_button = st.form_submit_button(label='ENTRAR')

        if login_button:
            # Validación robusta
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
    else:
        # PANTALLA PRINCIPAL TRAS LOGIN
        st.success(f"Bienvenido/a, {st.session_state['usuario_nombre']}")
        
        # --- PARTE DE VISUALIZACIÓN DE PROTOCOLOS ---

if not resultado.empty:
    st.write(f"✅ Se han encontrado {len(resultado)} protocolos:")
    
    for i, row in resultado.iterrows():
        # Obtenemos el título y el contenido (ajusta a tus nombres de columna)
        # Usamos .get() para que si no existe la columna no de error
        titulo_protocolo = row.get('titulo', 'Protocolo sin nombre')
        contenido_protocolo = row.get('contenido', row.get('descripcion', 'Sin contenido detallado'))
        
        # Creamos el desplegable (Expander)
        # El emoji se puede personalizar o dejar uno fijo como 📄 o ⚖️
        with st.expander(f"🔹 {titulo_protocolo}"):
            st.markdown(f"""
                <div style='padding: 10px; border-radius: 5px; border-left: 3px solid #004488;'>
                    {contenido_protocolo}
                </div>
            """, unsafe_allow_html=True)
            
            # Si tienes una columna con enlaces o PDFs, puedes añadir un botón aquí
            if 'enlace' in row and pd.notnull(row['enlace']):
                st.link_button("Ver documento completo", row['enlace'])
else:
    st.warning("⚠️ No se encontraron protocolos que coincidan con la búsqueda.")

        if st.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Revisa que los GID de las hojas sean correctos.")
