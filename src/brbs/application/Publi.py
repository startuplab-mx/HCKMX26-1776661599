import streamlit as st

# --- ESTILO VISUAL CORREGIDO ---
st.markdown("""
<style>
/* Fondo general */
.stApp { 
    background-color: #0B0F14; 
    font-family: 'Segoe UI', sans-serif;
}

/* Contenedor centrado */
.block-container {
    max-width: 1100px !important;
    margin: auto !important;
    padding-top: 2rem !important;
}

/* SOLO tipografía segura */
body, p, h1, h2, h3, button, input, textarea {
    font-family: 'Segoe UI', sans-serif !important;
}

/* Título */
h1 {
    color: white !important;
    text-align: center;
    font-size: 2rem !important;
    margin-bottom: 25px !important;
}

/* Línea divisoria central */
[data-testid="column"]:nth-of-type(1) {
    border-right: 3px solid white !important;
    padding-right: 40px !important;
}

[data-testid="column"]:nth-of-type(2) {
    padding-left: 40px !important;
}

/* Contenedores */
[data-testid="stVerticalBlockBorderWrapper"] { 
    border: 1px solid #334155 !important; 
    border-radius: 10px;
    padding: 15px !important;
}

/* Subtítulos */
h3 {
    color: white !important;
    text-align: center;
    font-size: 1.1rem !important;
    margin-bottom: 12px !important;
}

/* Inputs */
textarea, input {
    background-color: #1E293B !important;
    color: white !important;
    border: 1px solid #1F2937 !important;
    font-size: 1rem !important;
}

/* Botón */
div.stButton > button:first-child {
    background-color: #1F2937 !important;
    color: white !important;
    border: 1px solid #334155 !important;
    font-weight: bold;
    height: 3em;
    font-size: 1rem !important;
}

/* --- FIX FILE UPLOADER --- */
[data-testid="stFileUploader"] button div {
    font-size: 0 !important;
}

[data-testid="stFileUploader"] button::after {
    content: "Subir archivo";
    font-size: 14px;
    color: #E5E7EB;
}

/* Estilo uploader */
[data-testid="stFileUploader"] button {
    background-color: #1F2937 !important;
    border: 1px solid #334155 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown("<h1>Panel de Publicación</h1>", unsafe_allow_html=True)

# --- COLUMNAS ---
col_izq, col_der = st.columns(2)

# --- IZQUIERDA ---
with col_izq:
    st.markdown("<h3>Imagen</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        img_file = st.file_uploader(
            "Selecciona una foto",
            type=['png', 'jpg', 'jpeg'],
            label_visibility="collapsed"
        )

        if img_file:
            st.image(img_file, use_container_width=True)
        else:
            st.markdown(
                "<div style='height: 100px; text-align: center; color: #475569; padding-top: 35px;'>Cargar imagen</div>",
                unsafe_allow_html=True
            )

    st.write("")

    st.markdown("<h3>Descripción</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        texto_pub = st.text_area(
            "Texto",
            placeholder="¿Qué estás pensando?...",
            height=120,
            label_visibility="collapsed"
        )

        if st.button("PUBLICAR AHORA", use_container_width=True):
            if texto_pub or img_file:
                st.success("¡Listo!")
            else:
                st.warning("Vacío")

# --- DERECHA ---
with col_der:
    st.markdown("<h3>Panel de Control</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            "<div style='height: 385px; display: flex; align-items: center; justify-content: center; color: #475569;'>Espacio reservado para nueva función</div>",
            unsafe_allow_html=True
        )