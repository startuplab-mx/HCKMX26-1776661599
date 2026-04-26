import streamlit as st
import tempfile
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from brbs.domain.extractor import extraer_texto_imagen, analizar_reclutamiento

# Cargar variables de entorno (para la API Key de OpenAI)
load_dotenv()

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

# --- INICIALIZAR ESTADO DE SESIÓN ---
# Esto guarda el resultado para que no se borre al recargar la página
if "resultado_analisis" not in st.session_state:
    st.session_state.resultado_analisis = None

# --- TÍTULO ---
st.markdown("<h1>Panel de Publicación</h1>", unsafe_allow_html=True)

# --- COLUMNAS ---
col_izq, col_der = st.columns(2)

# --- IZQUIERDA (Entrada de Datos) ---
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
                with st.spinner("Analizando publicación con IA..."):
                    try:
                        texto_extraido_imagen = ""
                        
                        # 1. Si hay imagen, extraemos el texto
                        if img_file:
                            # Guardamos la imagen en un archivo temporal
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                                tmp_file.write(img_file.getvalue())
                                temp_path = tmp_file.name
                            
                            # Instanciamos el LLM para pasárselo a tu función
                            # (Usamos gpt-4o-mini que soporta capacidades de visión)
                            llm_vision = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                            
                            # Extraemos el texto
                            texto_extraido_imagen = extraer_texto_imagen(temp_path, llm_vision)
                            
                            # Limpiamos el archivo temporal
                            os.remove(temp_path)

                        # 2. Ejecutamos el agente de análisis
                        datos_analisis = {
                            "texto_publicacion": texto_pub,
                            "texto_imagen": texto_extraido_imagen
                        }
                        
                        resultado = analizar_reclutamiento(datos_analisis)
                        
                        # Guardamos el resultado en el estado
                        st.session_state.resultado_analisis = resultado

                    except Exception as e:
                        st.error(f"Ocurrió un error en el análisis: {e}")
            else:
                st.warning("Sube una imagen o escribe un texto para publicar.")

# --- DERECHA (Salida de Datos) ---
with col_der:
    st.markdown("<h3>Panel de Control</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        if st.session_state.resultado_analisis:
            resultado = st.session_state.resultado_analisis
            
            # Evaluación principal
            if resultado.get("es_reclutador"):
                st.error("⚠️ **ALERTA DE SEGURIDAD**\n\nSe detectaron indicios de reclutamiento criminal en esta publicación.")
            else:
                st.success("✅ **PUBLICACIÓN SEGURA**\n\nNo se detectaron indicios de reclutamiento criminal.")
            
            # Mostrar la justificación del agente
            st.markdown("#### Análisis del Agente:")
            st.info(resultado.get("analisis", "Sin análisis disponible."))
            
        else:
            st.markdown(
                "<div style='height: 385px; display: flex; align-items: center; justify-content: center; text-align: center; color: #475569;'>"
                "Sube una publicación para<br>ver el análisis de seguridad aquí."
                "</div>",
                unsafe_allow_html=True
            )