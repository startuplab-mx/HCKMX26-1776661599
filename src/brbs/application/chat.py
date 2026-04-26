import streamlit as st
from brbs.domain.agents import corrector_texto
from brbs.domain.agents import analizar_chat_reclutamiento
from brbs.domain.extractor import extraer_texto_imagen
from brbs.domain.extractor import analizar_reclutamiento
from datetime import datetime

# --- Estilos CSS Personalizados ---
st.markdown("""
<style>
/* Títulos */
h1 { color: white !important; margin-bottom: 30px !important; }

/* Ocultar avatares nativos de Streamlit */
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }

/* LÍNEA BLANCA CENTRAL DIVISORIA */
[data-testid="column"]:nth-of-type(1) { border-right: 3px solid white !important; padding-right: 40px !important; }
[data-testid="column"]:nth-of-type(2) { padding-left: 40px !important; }

/* Ocultar fondo nativo de mensajes para usar nuestras burbujas */
[data-testid="stChatMessage"] { background-color: transparent !important; border: none !important; padding: 0 !important; }

/* Contenedor para alinear a derecha o izquierda */
.chat-row { display: flex; margin-bottom: 10px; width: 100%; }
.sent { justify-content: flex-end; } 
.received { justify-content: flex-start; } 
.system { justify-content: center; } /* Mensajes del sistema al centro */

/* ESTILO DE LA BURBUJA */
.bubble {
    padding: 10px 15px; border-radius: 15px; max-width: 85%;
    border: 1px solid #1F2937; background-color: #121821; color: white;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}
.bubble-system { background-color: #450a0a; border-color: #ef4444; color: #fca5a5; font-size: 0.9em; text-align: center; }
.bubble-warning { background-color: #422006; border-color: #f59e0b; color: #fcd34d; }

/* Colores de los nombres */
.sujeto1-name { color: #F87171; font-weight: bold; }
.sujeto2-name { color: #34D399; font-weight: bold; }

/* Input y Botones */
[data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #334155 !important; }
.stChatInput input { background-color: #1E293B !important; color: white !important; }
            
/* PROTEGER ÍCONOS */
.stIcon, span[class*="material-symbols"], i[class*="material-icons"], svg {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons", sans-serif !important; font-size: inherit !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Simulación de Chat Interactivo</h1>", unsafe_allow_html=True)

# --- Estado de sesión ---
if "historial_u1" not in st.session_state:
    st.session_state.historial_u1 = []
if "historial_u2" not in st.session_state:
    st.session_state.historial_u2 = []
if "historial_global" not in st.session_state:
    st.session_state.historial_global = [] # Para el contexto de los últimos 5 mensajes
if "chat_bloqueado" not in st.session_state:
    st.session_state.chat_bloqueado = False

def procesar_mensaje(emisor, receptor, mensaje_raw, historial_emisor, historial_receptor, clase_emisor):
    # 1. El emisor ve su mensaje tal cual lo escribió en su pantalla (Inmediato)
    historial_emisor.append({"type": "own", "content": f"<span class='{clase_emisor}'>{emisor}:</span> {mensaje_raw}"})

    # 2. AGENTE 1: Corrector de Texto
    with st.spinner(f"Agente 1: Corrigiendo texto..."):
        texto_corregido = corrector_texto(mensaje_raw)

    # Añadir al historial global para que el Agente 2 tenga el contexto (usamos el corregido)
    st.session_state.historial_global.append({
        "user": emisor,
        "hora": datetime.now().strftime("%H:%M:%S"),
        "mensaje": texto_corregido
    })

    # 3. AGENTE 2: Análisis de Reclutamiento (Últimos 5 mensajes)
    ultimos_5 = st.session_state.historial_global[-5:]
    with st.spinner("Agente 2: Analizando riesgos de seguridad..."):
        analisis = analizar_chat_reclutamiento(ultimos_5)

    # 4. Buscamos ÚNICAMENTE la evaluación del usuario que acaba de enviar el mensaje (el emisor)
    accion_emisor = next((a for a in analisis.acciones if a.usuario == emisor), None)

    # Fallback de seguridad por si el LLM omite al usuario
    estado_emisor = accion_emisor.estado if accion_emisor else "normal"
    mensaje_sistema = accion_emisor.mensaje_resultante if accion_emisor else ""

    # --- LÓGICA DE ENTREGA (PYTHON CONTROLA EL FLUJO, NO EL LLM) ---
    
    # CASO A: BLOQUEO (Sospechoso)
    if analisis.posible_reclutador_detectado or estado_emisor == "sospechoso":
        st.session_state.chat_bloqueado = True
        st.error("🚨 SE HA DETECTADO UN POSIBLE RECLUTADOR. CHAT BLOQUEADO.")
        
        historial_emisor.append({"type": "system", "content": "<div class='bubble bubble-system'>🚨 <b>Sistema:</b> Tu cuenta ha sido bloqueada por infringir las normas.</div>"})
        historial_receptor.append({"type": "system", "content": f"<div class='bubble bubble-system'>🚨 <b>Sistema:</b> El usuario {emisor} ha sido bloqueado por seguridad.</div>"})
        return

    # CASO B: ADVERTENCIA
    elif estado_emisor == "advertencia":
        if mensaje_sistema:
            historial_emisor.append({"type": "system", "content": f"<div class='bubble bubble-warning'>⚠️ <b>Aviso:</b> {mensaje_sistema}</div>"})
        
        # Se entrega el mensaje al receptor, pero envuelto en una alerta visual
        historial_receptor.append({
            "type": "other", 
            "content": f"<div class='bubble bubble-warning'>🛡️ <b>Mensaje de <span class='{clase_emisor}'>{emisor}</span>:</b><br>{texto_corregido}<br><br><small><i>⚠️ Nota del sistema: Mantén precaución al compartir datos personales.</i></small></div>"
        })

    # CASO C: NORMAL
    else:
        # Entrega directa y limpia del texto corregido al receptor
        historial_receptor.append({"type": "other", "content": f"<span class='{clase_emisor}'>{emisor}:</span> {texto_corregido}"})
        
# --- Layout de Columnas ---
col1, col2 = st.columns(2)

# --- COLUMNA 1: SUJETO 1 ---
with col1:
    with st.container(height=300, border=True):
        for msg in st.session_state.historial_u1:
            if msg["type"] == "system":
                st.markdown(f"<div class='chat-row system'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                align = "sent" if msg["type"] == "own" else "received"
                # Si el contenido ya incluye una clase de burbuja (como las advertencias), no la envolvemos en otra
                if "class='bubble" in msg['content']:
                    st.markdown(f"<div class='chat-row {align}'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-row {align}'><div class='bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)

    # Input Sujeto 1
    if p1 := st.chat_input("Mensaje como Sujeto 1...", key="input_s1", disabled=st.session_state.chat_bloqueado):
        procesar_mensaje("Sujeto 1", "Sujeto 2", p1, st.session_state.historial_u1, st.session_state.historial_u2, "sujeto1-name")
        st.rerun()

# --- COLUMNA 2: SUJETO 2 ---
with col2:
    with st.container(height=300, border=True):
        for msg in st.session_state.historial_u2:
            if msg["type"] == "system":
                st.markdown(f"<div class='chat-row system'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                align = "sent" if msg["type"] == "own" else "received"
                if "class='bubble" in msg['content']:
                    st.markdown(f"<div class='chat-row {align}'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-row {align}'><div class='bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)

    # Input Sujeto 2
    if p2 := st.chat_input("Mensaje como Sujeto 2...", key="input_s2", disabled=st.session_state.chat_bloqueado):
        procesar_mensaje("Sujeto 2", "Sujeto 1", p2, st.session_state.historial_u2, st.session_state.historial_u1, "sujeto2-name")
        st.rerun()

# --- Botón de Reinicio ---
st.markdown("<br>", unsafe_allow_html=True)
_, col_boton, _ = st.columns([1, 1, 1])
with col_boton:
    if st.button("Limpiar Conversación Total", use_container_width=True):
        st.session_state.historial_u1 = []
        st.session_state.historial_u2 = []
        st.session_state.historial_global = []
        st.session_state.chat_bloqueado = False
        st.rerun()