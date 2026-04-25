import streamlit as st

st.title("Panel de Publicación")

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1F2937 !important;
        border: 1px solid #30363D !important;
        border-radius: 10px;
        padding: 20px;
    }
    h3 { color: #F1C40F !important; }
    </style>
    """, unsafe_allow_html=True)

# Creamos solo 2 columnas ahora: Izquierda (Imagen) y Derecha (Texto/Botón)
col_izq, col_der = st.columns([2, 3], gap="large")

# --- COLUMNA IZQUIERDA: CARGA DE IMAGEN ---
with col_izq:
    st.subheader("Imagen de la publicación")
    with st.container(border=True):
        img_file = st.file_uploader("Selecciona una foto", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
        if img_file:
            st.image(img_file, use_container_width=True, caption="Previsualización")
        else:
            st.info("Sube una imagen para verla aquí.")

# --- COLUMNA DERECHA: TEXTO Y ACCIÓN ---
with col_der:
    st.subheader("Descripción")
    with st.container(border=True):
        texto_pub = st.text_area("¿Qué estás pensando?", placeholder="Escribe el pie de foto aquí...", height=200)
        
        st.write("") # Espacio estético
        
        if st.button("PUBLICAR AHORA", use_container_width=True, type="primary"):
            if texto_pub or img_file:
                st.success("¡Tu publicación ha sido compartida!")
                st.balloons()
            else:
                st.warning("No puedes publicar algo vacío. Agrega texto o una imagen.")