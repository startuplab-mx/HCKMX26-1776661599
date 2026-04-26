import base64
import mimetypes
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def extraer_texto_imagen(ruta_imagen, llm):
    """
    Extrae todo el texto visible de una imagen utilizando un modelo multimodal.

    Args:
        ruta_imagen (str): Ruta del archivo de imagen que se desea procesar.
        llm (object): Instancia de un modelo de lenguaje (LLM) compatible con entrada multimodal 
                      que implemente el método `invoke`.

    Returns:
        str: Texto extraído de la imagen en un solo párrafo, respetando el contenido original 
             (incluyendo emojis, hashtags, menciones y signos), y reemplazando saltos de línea por espacios.

    Raises:
        ValueError: Si no se puede determinar el tipo MIME del archivo de imagen.
    """

    # Detectar tipo MIME del archivo (por ejemplo: image/png, image/jpeg)
    mime_type, _ = mimetypes.guess_type(ruta_imagen)

    # Validar que el tipo MIME sea detectable
    if mime_type is None:
        raise ValueError(f"No se pudo detectar el tipo de archivo: {ruta_imagen}")

    # Abrir la imagen en modo binario y codificarla a base64. Esto permite enviarla como parte de un mensaje multimodal
    with open(ruta_imagen, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")

    # Instrucciones para el modelo
    prompt = """Extrae todo el texto visible de esta imagen. No cambies, corrijas, elimines ni agregues nada.
    Incluye todos los emojis visibles sin importar si no vienen seguidos de texto. Incluye hashtags, menciones y signos tal como aparecen.
    Devuelve el resultado en un solo párrafo, reemplazando saltos de línea por espacios, sin perder el orden original del texto.
    Si la imagen es una captura de una publicación en una red social, extrae únicamente el texto principal del contenido publicado
    y excluye cualquier elemento de interfaz o metadatos de la plataforma."""

    # Construir mensaje multimodal con texto + imagen en base64
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}
            }
        ]
    )

    # Enviar el mensaje al modelo y obtener la respuesta
    response = llm.invoke([message])

    # Retornar únicamente el contenido textual de la respuesta
    return response.content


# Esquemas de Pydantic
class AnalisisOutput(BaseModel):
    es_reclutador: bool = Field(
        ..., 
        description="Indica si la publicación corresponde a un reclutador de actividades ilícitas (True/False)."
    )
    analisis: str = Field(
        ..., 
        description="Análisis breve de los elementos encontrados que llevaron a la conclusión."
    )


def analizar_reclutamiento(data_input: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Analiza una publicación de texto e imagen para detectar posibles señales de reclutamiento criminal.

    Args:
        data_input (Dict[str, Optional[str]]):
            Diccionario de entrada con la siguiente estructura:
            - "texto_publicacion": str | None
              Texto principal de la publicación en redes sociales.
            - "texto_imagen": str | None
              Texto extraído mediante OCR u otro método desde imágenes asociadas.

    Returns:
        Dict[str, Any]:
            Diccionario con el resultado estructurado del análisis:
            - "es_reclutador": bool
              Indica si la publicación corresponde a un posible reclutamiento criminal.
            - "analisis": str
              Explicación breve de los indicios detectados que llevaron a la decisión.
    """
    
    load_dotenv("../.env")
    api_key = os.getenv("OPENAI_API_KEY")

    # Configuración del LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key
    ).with_structured_output(AnalisisOutput)

    # Preparación de datos de entrada
    texto_pub = data_input.get("texto_publicacion") or ""
    texto_img = data_input.get("texto_imagen") or ""

    # Normalización del texto para análisis
    texto_completo = f"{texto_pub} {texto_img}".lower()

    # Emojis y hashtags comúnmente utilizados en publicaciones de reclutamiento
    emojis_dict = {
        "🥷": "Es utilizado para representar a los ladrones o las personas que operan para los cárteles y que aprecen encapuchados en contenido multimedia.",
        "🪖": "Es utilizado en videos donde aparecen personas fuertemente armadas. A veces estas personas posan desde camionetas y automóviles de lujo, utilizando vestimenta militar.",
        "👿": "Representa el mal",
        "👺": "Representa a Namahague, un ogro japonés. Se utiliza como una variante del diablo. Aparece constantemente en publicaciones que incorporan canciones de Makabélico.",
        "🧿": "Está asociado con la protección del mal de ojo y las malas energías. Se utliza para referenciasl directamente a 'la maña'",
        "🍕": "Aparece sistemáticamente en las cuentas asociadas con el Cártel de Sinaloa, especificamente con la facción encabezada por Joaquín (El Chapo) Guzmán, Este emoji casi siempre es utilizado después de las letras 'ch' para formar la palabra 'chapizza'",
        "🐓": "Figura en las publicaciones de las cuentas reclutadoras del CJNG. Se utiliza para referencias a Nemesio Oseguera Cervantes (El Mencho), también apodado 'El señor de los gallos', quien es el principal líder de esta organización criminal.",
        "🆖": "Aparece en las publicaciones de las cuentas reclutadoras del CJNG. Las siglas significan 'Nueva Generación'. A menudo es utilizado después del número 4."
    }

    hashtag_list = ["#gentedelmz", "#mayozambada", "#operativamz", "#gentedelmayozambada",
                    "#nuevageneraión", "#4letras", "#4l", "#ng", "#mencho", "#mencho (sic.)", "#señormencho", "#ElSeñorDeLosGallos",
                    "#maña", "#trabajoparalamaña", "#belicones", "#fracesbelicas (sic.)",
                    "#makabelico_oficial", "#ondeado", "#victormendivil", "#makabelico"]

    # Definición del Prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """Eres un analista experto en seguridad y detección de reclutamiento criminal.
        Tu tarea es determinar si una publicación de red social es un intento de reclutamiento para el crimen organizado.
        
        Contexto de emojis: {emojis_dict}
        Contexto de hashtags: {hashtag_list}
        
        Criterios: Uso de lenguaje ambiguo sobre empleos, ofertas de dinero fácil, rápido o sin requisitos claros, presencia de los emojis o hashtags de referencia."""),
        ("human", "Analiza el siguiente texto: {texto_completo}")
    ])

    # Construcción de la cadena LLM + Prompt
    chain = prompt_template | llm
    
    # Ejecución del análisis
    resultado = chain.invoke({
        "emojis_dict": emojis_dict,
        "hashtag_list": hashtag_list,
        "texto_completo": texto_completo
    })

    return resultado.model_dump() # Retorno del resultado en formato JSON (dict)