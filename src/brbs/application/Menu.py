import streamlit as st

# Configuración inicial (Solo se pone aquí)
st.set_page_config(layout="wide", page_title="Hackathon Hub")

# Definimos las páginas apuntando a los otros archivos
pg = st.navigation([
    st.Page("chat.py", title="Chat", icon="💬"),
    st.Page("publi.py", title="Publicación", icon="📤")
])

# Ejecutar la navegación
pg.run()