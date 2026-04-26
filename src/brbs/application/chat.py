import streamlit as st

# --- Estilos CSS Personalizados ---
st.markdown("""
<style>
/* Títulos */
h1 {
    color: white !important;
    margin-bottom: 30px !important;
}

/* Ocultar avatares nativos de Streamlit */
[data-testid="stChatMessageAvatarUser"], 
[data-testid="stChatMessageAvatarAssistant"] {
    display: none !important;
}

/* LÍNEA BLANCA CENTRAL DIVISORIA */
[data-testid="column"]:nth-of-type(1) {
    border-right: 3px solid white !important;
    padding-right: 40px !important;
}
[data-testid="column"]:nth-of-type(2) {
    padding-left: 40px !important;
}

/* Ocultar fondo nativo de mensajes para usar nuestras burbujas */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* Contenedor para alinear a derecha o izquierda */
.chat-row {
    display: flex;
    margin-bottom: 10px;
    width: 100%;
}

.sent { justify-content: flex-end; } /* Derecha */
.received { justify-content: flex-start; } /* Izquierda */

/* ESTILO DE LA BURBUJA */
.bubble {
    padding: 10px 15px;
    border-radius: 15px;
    max-width: 85%;
    border: 1px solid #1F2937;
    background-color: #121821;
    color: white;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}

/* Colores de los nombres */
.sujeto1-name { color: #F87171; font-weight: bold; }
.sujeto2-name { color: #34D399; font-weight: bold; }

/* Input y Botones */
[data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #334155 !important; }
.stChatInput input { background-color: #1E293B !important; color: white !important; }
            
/* PROTEGER EXPLÍCITAMENTE LOS ÍCONOS DE STREAMLIT (FLECHAS, NUBES, ETC.) */
.stIcon, 
span[class*="material-symbols"], 
i[class*="material-icons"],
svg {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons", sans-serif !important;
    font-size: inherit !important;
}
</style>
""", unsafe_allow_html=True)

# TÍTULO PRINCIPAL CENTRADO
st.markdown("<h1 style='text-align: center;'>Simulación de Chat Interactivo</h1>", unsafe_allow_html=True)

# --- Estado de sesión ---
if "historial_u1" not in st.session_state:
    st.session_state.historial_u1 = []
if "historial_u2" not in st.session_state:
    st.session_state.historial_u2 = []

# --- Layout de Columnas ---
col1, col2 = st.columns(2)

# --- COLUMNA 1: SUJETO 1 ---
with col1:
    with st.container(height=500, border=True):
        for msg in st.session_state.historial_u1:
            align = "sent" if msg["type"] == "own" else "received"
            st.markdown(f"""
                <div class="chat-row {align}">
                    <div class="bubble">{msg['content']}</div>
                </div>
            """, unsafe_allow_html=True)

    if p1 := st.chat_input("Mensaje como Sujeto 1...", key="input_s1"):
        cont_s1 = f"<span class='sujeto1-name'>Sujeto 1:</span> {p1}"
        st.session_state.historial_u1.append({"type": "own", "content": cont_s1})
        st.session_state.historial_u2.append({"type": "other", "content": cont_s1})
        st.rerun()

# --- COLUMNA 2: SUJETO 2 ---
with col2:
    with st.container(height=500, border=True):
        for msg in st.session_state.historial_u2:
            align = "sent" if msg["type"] == "own" else "received"
            st.markdown(f"""
                <div class="chat-row {align}">
                    <div class="bubble">{msg['content']}</div>
                </div>
            """, unsafe_allow_html=True)

    if p2 := st.chat_input("Mensaje como Sujeto 2...", key="input_s2"):
        cont_s2 = f"<span class='sujeto2-name'>Sujeto 2:</span> {p2}"
        st.session_state.historial_u2.append({"type": "own", "content": cont_s2})
        st.session_state.historial_u1.append({"type": "other", "content": cont_s2})
        st.rerun()

# --- Botón de Reinicio ---
st.markdown("<br>", unsafe_allow_html=True)
_, col_boton, _ = st.columns([1, 1, 1])
with col_boton:
    if st.button("Limpiar Conversación Total", use_container_width=True):
        st.session_state.historial_u1 = []
        st.session_state.historial_u2 = []
        st.rerun()