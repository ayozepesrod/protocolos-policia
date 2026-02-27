import streamlit as st
import pandas as pd
import unicodedata
import re
import math

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Guía Operativa Policial", page_icon="🛡️", layout="wide")

# 2. ESTILO CSS ACTUALIZADO
# He cambiado .dato-importante a display: block para que las líneas se apilen correctamente
st.markdown("""
    <style>
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    .block-container { padding-top: 0rem !important; margin-top: -30px; }
    .titulo { margin: 0; padding: 10px 0; font-size: 2.5rem; color: #004488; text-align: center; font-weight: bold; }
    .seccion-header {
        color: #004488;
        font-weight: bold;
        border-bottom: 2px solid #004488;
        margin-top: 15px;
        margin-bottom: 10px;
        font-size: 1.2rem;
        text-transform: uppercase;
    }
    .dato-importante {
        background-color: #e8f0f7;
        padding: 8px 10px;
        border-radius: 5px;
        font-weight: bold;
        color: #d32f2f;
        display: block; 
        margin-top: 5px;
        line-height: 1.4;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🛡️ Sistema de Consulta Operativa</h1>", unsafe_allow_html=True)

# 3. FUNCIONES
def limpiar_texto(t):
    if not t:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(t).strip())
        if unicodedata.category(c) != 'Mn'
    ).lower()

def obtener_enlace_csv(url, gid="0"):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        doc_id = match.group(1)
        return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={gid}"
    return url

# Función para manejar multidenuncias (separa por / y pone saltos de línea)
def formatear_multivalor(valor, sufijo=""):
    if not valor: return "-"
    items = str(valor).split('/')
    return "<br>".join([f"{item.strip()}{sufijo}" for item in items])

# Mapa de emojis global
mapa_emojis = {
    "vmp": "🛴",
    "alcohol": "🍺",
    "movil": "📱"
}

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
        df['texto_busqueda'] = df.apply(
            lambda row: limpiar_texto(' '.join(row.astype(str))), axis=1
        )
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

    # --- 6. APP PRINCIPAL ---
    else:
        c1, c2 = st.columns([0.8, 0.2])
        c1.write(f"👤 Agente: **{st.session_state['usuario_nombre']}**")

        if c2.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

        busqueda = st.text_input("🔍 Buscar por infracción, artículo, puntos o palabra clave...")

        if busqueda:
            terminos = limpiar_texto(busqueda).split()
            resultado = protocolos_df[
                protocolos_df['texto_busqueda'].apply(
                    lambda texto: all(t in texto for t in terminos)
                )
            ]

            if not resultado.empty:
                st.write(f"✅ Se han encontrado {len(resultado)} protocolos:")

                for _, row in resultado.iterrows():
                    titulo = row.get('titulo', 'Sin título')

                    # Gestión de Emojis
                    emoji = row.get('emoji')
                    if not emoji or (isinstance(emoji, float) and math.isnan(emoji)):
                        categoria = str(row.get('categoria', '')).lower()
                        emoji = mapa_emojis.get(categoria, '⚖️')
                    else:
                        emoji = str(emoji).strip()

                    # Renderizado del Expander
                    norma_principal = str(row.get('norma', '')).split('/')[0]
                    art_principal = str(row.get('art', '')).split('/')[0]
                    
                    with st.expander(f"{emoji} {titulo} | {norma_principal} Art. {art_principal}"):

                        if row.get('palabras_clave'):
                            st.caption(f"🔑 Palabras clave: {row['palabras_clave']}")

                        st.markdown("<div class='seccion-header'>🚨 PROTOCOLO DE ACTUACIÓN</div>", unsafe_allow_html=True)
                        st.info(row.get('diligencias', 'No especificadas'))

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.markdown("<div class='seccion-header'>📌 Código</div>", unsafe_allow_html=True)
                            # Unimos Norma, Art, Apt y Opc de forma inteligente
                            n_list = str(row.get('norma', '')).split('/')
                            a_list = str(row.get('art', '')).split('/')
                            ap_list = str(row.get('apt', '')).split('/')
                            o_list = str(row.get('opc', '')).split('/')
                            
                            codigos_formateados = []
                            for i in range(len(n_list)):
                                n = n_list[i].strip()
                                a = a_list[i].strip() if i < len(a_list) else ""
                                ap = ap_list[i].strip() if i < len(ap_list) else ""
                                o = o_list[i].strip() if i < len(o_list) else ""
                                codigos_formateados.append(f"{n} {a} {ap} {o}".strip())
                            
                            st.markdown(f"<div class='dato-importante'>{'<br>'.join(codigos_formateados)}</div>", unsafe_allow_html=True)

                        with col2:
                            st.markdown("<div class='seccion-header'>⭐ Puntos</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='dato-importante'>{formatear_multivalor(row.get('ptos', '0'), ' ptos')}</div>", unsafe_allow_html=True)

                        with col3:
                            st.markdown("<div class='seccion-header'>⚠️ Calif.</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='dato-importante'>{formatear_multivalor(row.get('calif', 'Grave'))}</div>", unsafe_allow_html=True)

                        with col4:
                            st.markdown("<div class='seccion-header'>💰 Multa</div>", unsafe_allow_html=True)
                            # Lógica para emparejar Multa con Importe Reducido
                            m_raw = str(row.get('multa', '0')).split('/')
                            rd_raw = str(row.get('imp_rd', '0')).split('/')
                            multas_finales = []
                            for i in range(len(m_raw)):
                                m_val = m_raw[i].strip()
                                rd_val = rd_raw[i].strip() if i < len(rd_raw) else "?"
                                multas_finales.append(f"{m_val}€ ({rd_val}€)")
                            st.markdown(f"<div class='dato-importante'>{'<br>'.join(multas_finales)}</div>", unsafe_allow_html=True)

                        st.markdown("<div class='seccion-header'>📝 TEXTO ÍNTEGRO PARA DENUNCIA</div>", unsafe_allow_html=True)
                        st.success(row.get('texto_denuncia_integro', 'No disponible'))

                        st.markdown("<div class='seccion-header'>📑 NOTAS COMPLEMENTARIAS</div>", unsafe_allow_html=True)
                        st.warning(row.get('notas', 'Sin notas adicionales'))
            else:
                st.warning(f"No hay resultados para: {busqueda}")
        else:
            st.info("Utilice el buscador superior para localizar el protocolo.")

except Exception as e:
    st.error(f"Error en el sistema: {e}")
