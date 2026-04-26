# BRBS - Agente de Detección de Reclutamiento Criminal

## Descripción General

BRBS es una solución de seguridad digital que analiza publicaciones y mensajes de chat para detectar patrones de reclutamiento criminal dirigidos a jóvenes. Utilizando modelos de lenguaje avanzados y agentes de IA, el sistema clasifica el comportamiento de usuarios y contenido en tiempo real, permitiendo identificar amenazas potenciales de forma automática.

### Objetivo Principal

Proteger a menores de edad de intentos de reclutamiento por parte de organizaciones criminales a través de:
- Análisis de mensajes y publicaciones en redes sociales
- Detección de patrones lingüísticos sospechosos
- Clasificación de riesgo en tiempo real
- Corrección y normalización de "leet speak" y lenguaje ofuscado

## Arquitectura del Proyecto

El proyecto está organizado en dos capas principales:

### 📁 Estructura

```
brbs/
├── application/          # Interfaz Streamlit (Prototipo visual)
│   ├── Menu.py          # Navegación principal de la aplicación
│   ├── chat.py          # Interfaz de chat interactivo
│   └── publi.py         # Panel de análisis de archivos/publicaciones
│
└── domain/              # Lógica de Filtros y Agentes
    ├── agents.py        # Agentes de IA para clasificación
    ├── extractor.py     # Extracción de información
    └── prompts.py       # Templates de prompts para LLM
```

### Componentes Principales

#### **Domain (Filtros de Agentes)**
- **agents.py**: Contiene los agentes de IA que clasifican usuarios y contenido
  - `corrector_texto()`: Normaliza "leet speak" a texto plano
  - `analizar_chat_reclutamiento()`: Agente para clasificar comportamiento (normal, advertencia, sospechoso)
  
- **extractor.py**: Extracción de características y análisis de contenido

#### **Application (Interfaz Streamlit)**
- **Menu.py**: Router principal que gestiona la navegación entre páginas
- **chat.py**: Interfaz conversacional para análisis de mensajes
- **publi.py**: Panel para subir y analizar archivos/publicaciones

## Instalación

### Requisitos Previos

- Python 3.11 o superior
- Clave de API de OpenAI
- `uv` package manager (recomendado)

### Instalación con UV

1. **Instalar UV** (si no lo tienes):
   ```bash
   pip install uv
   ```

2. **Instalar dependencias**:
   ```bash
   uv sync
   ```

   Esto instalará automáticamente todas las dependencias especificadas en `pyproject.toml`:
   - langchain >= 1.2.15
   - langchain-openai >= 1.2.1
   - langchain-core >= 1.3.2
   - streamlit >= 1.56.0
   - python-dotenv >= 0.9.9
   - ipykernel >= 7.2.0

4. **Configurar variables de entorno**:
   
   Crea un archivo `.env` en la raíz del proyecto:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```


## Uso

### Ejecutar la Aplicación

```bash
cd src/brbs/application
streamlit run Menu.py
```

La aplicación se abrirá en tu navegador

### Video de uso
El siguiente enlace tiene un video de información de cómo usar la aplicación
[enlace]

### Características Disponibles

1. **Chat**: 
   - Interfaz conversacional para analizar mensajes individuales
   - Ingresa mensajes de usuarios sospechosos
   - El sistema detecta patrones de reclutamiento
   - Obtén clasificación de riesgo en tiempo real

2. **Panel de Archivos**:
   - Análisis masivo de contenido
   - Sube archivos con publicaciones o mensajes
   - Procesa múltiples registros automáticamente
   - Genera reportes de riesgo



## Licencia

Ver archivo [LICENSE](LICENSE)

## Autores

Francisco Javier Torres Santana  
francisco.torressa@uaem.edu.mx  
Yamile Montecinos Rodríguez  
yamile.montecinos@uaem.edu.mx  
Humberto Santiago García Torres  
humberto.garciat@uaem.edu.mx

