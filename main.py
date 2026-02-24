import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Protocolos Policiales", layout="centered")

st.title("🛡️ Guía Operativa Policial")

# 1. Base de datos (Luego la conectaremos a tu Excel)
# De momento la dejamos aquí para que la app funcione ya.
data = [
    {"tema": "Alcoholemia", "busqueda": "alcohol 0.15 novel 0.25 aire", "protocolo": "1. Informar derechos.\n2. Esperar 10 min.\n3. Acta de signos.\n4. Inmovilizar.", "denuncia": "Art. 20 RGC: 500-1000€"},
    {"tema": "Drogas", "busqueda": "drogas porro coca saliva", "protocolo": "1. Prueba saliva.\n2. Envío laboratorio.\n3. Acta de signos.\n4. Inmovilizar.", "denuncia": "Art. 14 LSV: 1000€ y 6 puntos"},
    {"tema": "Pesos", "busqueda": "camion bascula exceso peso mma", "protocolo": "1. Pesaje.\n2. Si >20%, inmovilización.\n3. Trasvase de carga.", "denuncia": "LOTT: Sanción según baremo."}
]
df = pd.DataFrame(data)

# 2. Buscador
query = st.text_input("Escribe el hecho o palabras clave (ej: novel alcohol):").lower()

if query:
    # Lógica de búsqueda: busca en el tema y en las palabras clave
    mask = df.apply(lambda r: query in r['tema'].lower() or query in r['busqueda'].lower(), axis=1)
    res = df[mask]

    if not res.empty:
        for _, row in res.iterrows():
            with st.expander(f"✅ {row['tema']}", expanded=True):
                st.info(row['protocolo'])
                st.warning(f"⚖️ {row['denuncia']}")
                # Botón visual de copiar (Streamlit ya permite seleccionar texto fácil)
                st.write("👉 *Selecciona y copia el texto de arriba para el boletín.*")
    else:
        st.error("No hay protocolos para esa búsqueda.")

st.markdown("---")
st.caption("Uso exclusivo profesional.")
