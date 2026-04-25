import base64
import mimetypes
from langchain_core.messages import HumanMessage

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