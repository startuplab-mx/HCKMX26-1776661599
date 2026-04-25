import streamlit as st

st.title("Chat Interactivo Dual")

# Estilos específicos para esta página
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1 { color: #F1C40F !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1F2937 !important;
        border: 2px solid #30363D !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

if "historial_u1" not in st.session_state: st.session_state.historial_u1 = []
if "historial_u2" not in st.session_state: st.session_state.historial_u2 = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("Usuario 1")
    with st.container(height=400, border=True):
        for msg in st.session_state.historial_u1:
            avatar = "🔵" if "Usuario 1" in msg["content"] else "🟢"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
    
    with st.form("form_u1", clear_on_submit=True):
        p1 = st.text_input("Escribe aquí:", key="txt_u1")
        if st.form_submit_button("Enviar") and p1:
            m = f"**Usuario 1:** {p1}"
            st.session_state.historial_u1.append({"role": "user", "content": m})
            st.session_state.historial_u2.append({"role": "assistant", "content": m})
            st.rerun()

with col2:
    st.subheader("Usuario 2")
    with st.container(height=400, border=True):
        for msg in st.session_state.historial_u2:
            avatar = "🟢" if "Usuario 2" in msg["content"] else "🔵"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    with st.form("form_u2", clear_on_submit=True):
        p2 = st.text_input("Escribe aquí:", key="txt_u2")
        if st.form_submit_button("Enviar") and p2:
            m = f"**Usuario 2:** {p2}"
            st.session_state.historial_u2.append({"role": "user", "content": m})
            st.session_state.historial_u1.append({"role": "assistant", "content": m})
            st.rerun()