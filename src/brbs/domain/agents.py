from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv("../.env")
api_key = os.getenv("OPENAI_API_KEY")

def corrector_texto(mensaje_usuario: str) -> str:
    """
    Toma un mensaje escrito en "leet speak" (palabras con números o símbolos) 
    y lo traduce a texto normal utilizando un modelo de lenguaje de OpenAI.
    
    Reglas del asistente:
    - Solo devuelve el texto corregido (sin explicaciones extra).
    - Deja intactas las palabras incomprensibles.
    - Deja intactos los emojis y emoticonos.
    
    Args:
        mensaje_usuario (str): El mensaje en leet speak que se desea corregir.
        api_key (str, optional): Tu clave de API de OpenAI. Si no se provee, 
                                 intentará leer la variable de entorno OPENAI_API_KEY.
                                 
    Returns:
        str: El mensaje corregido a texto normal.
    """
    
    # Inicializamos el modelo. Usamos temperature=0 para que las respuestas 
    # sean deterministas y no se ponga "creativo" añadiendo texto no deseado.
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0, 
        openai_api_key= api_key)
    

    # Definimos las instrucciones del sistema con ejemplos (Few-Shot Prompting)
    instrucciones_sistema = """Eres un asistente especializado en corregir mensajes escritos en 'leet speak' a texto normal en español. 
    Tienes reglas estrictas que debes seguir sin excepción:
    1. Tu respuesta DEBE contener ÚNICAMENTE el texto corregido. No agregues saludos, introducciones ni explicaciones.
    2. Si una palabra es incomprensible o parece una cadena de letras sin sentido, déjala exactamente como está.
    3. Debes dejar todos los emojis, emoticonos y signos de puntuación exactamente como están y en su misma posición.

    Ejemplos de cómo debes comportarte:
    Usuario: h014 4m1g05 👽
    Asistente: Hola amigos 👽

    Usuario: 3st0 3s g3n14l kjhgf
    Asistente: esto es genial kjhgf

    Usuario: m3 p@5@5 7u 1n579r@m?
    Asistente: ¿me pasas tu instagram?

    Usuario: @79u13n 713n3 ❄️ para hoy?
    Asistente: ¿Alguien tiene ❄️ para hoy?
    """

    # Creamos el template del prompt combinando el sistema y el usuario
    prompt = ChatPromptTemplate.from_messages([
        ("system", instrucciones_sistema),
        ("human", "{mensaje}")
    ])

    # Construimos la cadena: Prompt -> LLM -> Parseador a String plano
    cadena = prompt | llm | StrOutputParser()

    # Ejecutamos la cadena con el mensaje del usuario
    respuesta = cadena.invoke({"mensaje": mensaje_usuario})
    
    return respuesta


class AccionUsuario(BaseModel):
    usuario: str = Field(..., description="Nombre del usuario evaluado.")
    estado: Literal["normal", "advertencia", "sospechoso"] = Field(
        ..., 
        description="Clasificación del comportamiento del usuario."
    )
    accion_sistema: str = Field(
        ..., 
        description="Instrucción de sistema a ejecutar (ej. 'entregar mensaje', 'bloquear y guardar para revisión manual', 'enviar advertencia')."
    )
    mensaje_resultante: Optional[str] = Field(
        None, 
        description="El texto exacto que recibirá este usuario. "
                    "Si es NORMAL (receptor): el mensaje original. "
                    "Si es ADVERTENCIA (receptor): el mensaje original + un recordatorio de seguridad. "
                    "Si es ADVERTENCIA (emisor): un aviso de infracción. "
                    "Si es SOSPECHOSO (receptor): Ninguno (no se entrega). "
                    "Si es SOSPECHOSO (emisor): Notificación de bloqueo."
    )


class AnalisisReclutamiento(BaseModel):
    chain_of_thought: str = Field(
        ..., 
        description="Tu análisis paso a paso evaluando si hay peticiones de datos personales, manipulación o intentos de reclutamiento criminal."
    )
    posible_reclutador_detectado: bool = Field(
        ..., 
        description="True si detectaste a un posible reclutador pidiendo datos o haciendo ofertas sospechosas."
    )
    acciones: List[AccionUsuario] = Field(
        ..., 
        description="Lista con la resolución y acción a tomar para CADA usuario involucrado en la conversación."
    )


def analizar_chat_reclutamiento(historial_mensajes: List[dict]) -> AnalisisReclutamiento:
    """
    Analiza los últimos mensajes de un chat para prevenir el reclutamiento criminal 
    o el robo de datos personales antes de entregar el último mensaje al receptor.
    
    Args:
        historial_mensajes (List[dict]): Lista de hasta 5 diccionarios con las claves 'user', 'hora' y 'mensaje'.
        api_key (str, optional): Tu clave de API de OpenAI.
        
    Returns:
        AnalisisReclutamiento: Objeto Pydantic con el análisis y las acciones a tomar.
    """
    # Inicializamos el modelo 
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0, 
        openai_api_key=api_key
    )
    
    # Enlazamos el LLM con el esquema de Pydantic
    llm_estructurado = llm.with_structured_output(AnalisisReclutamiento)

    # Definimos las instrucciones del sistema
    instrucciones = """Eres un sistema de seguridad experto en ciberseguridad y prevención de reclutamiento de grupos criminales.
    Tu objetivo es analizar una conversación de chat (los últimos 5 mensajes) justo antes de que el último mensaje sea entregado al receptor.

    Debes detectar si algún usuario está pidiendo datos personales confidenciales, haciendo promesas de dinero fácil, o mostrando patrones de reclutamiento.

    Realiza un 'Chain of Thought' (pensamiento paso a paso) en el campo correspondiente antes de dar tu veredicto.

    Reglas para clasificar el estado de los usuarios:
    1. "normal": La conversación es segura. El mensaje debe entregarse tal cual.
    2. "advertencia": Hay un comportamiento ligeramente sospechoso o petición de datos menores. 
    - Al emisor se le envía una advertencia sobre las normas. 
    - Al receptor se le entrega el mensaje original PERO con una nota adicional del sistema recordándole mantener su seguridad en internet.
    3. "sospechoso": Es un intento claro de reclutamiento o extracción de datos graves.
    - El mensaje NO se entrega a la víctima. 
    - El emisor es bloqueado y se marca para revisión manual.

    Evalúa la conversación y genera el JSON con la estructura solicitada."""

    # Creamos el template
    prompt = ChatPromptTemplate.from_messages([
        ("system", instrucciones),
        ("human", "Analiza la siguiente conversación:\n{conversacion}")
    ])

    # Convertimos la lista de diccionarios a un string legible para el prompt
    conversacion_str = "\n".join(
        [f"[{m['hora']}] {m['user']}: {m['mensaje']}" for m in historial_mensajes]
    )

    # Creamos la cadena (Chain)
    cadena = prompt | llm_estructurado

    # Ejecutamos
    resultado = cadena.invoke({"conversacion": conversacion_str})
    
    return resultado