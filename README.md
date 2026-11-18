# Nexo Intelligence

**AI Engineering | Python 3.12 | Coderhouse**

Nexo Intelligence es un proyecto de AI Engineering desarrollado en dos etapas. La primera implementa un cliente asíncrono para trabajar con modelos de OpenAI y Anthropic. La segunda incorpora un pipeline de procesamiento de textos técnicos mediante LangChain, LCEL y Pydantic.

El proyecto está organizado en dos paquetes independientes:

- `nexo_llm`: cliente unificado para generación de respuestas y streaming.
- `nexo_pipeline`: extracción estructurada de tecnologías, nivel de criticidad y resumen técnico.

**Repositorio:** https://github.com/gastonjaureguib-stack/nexo-llm

---

## 1. Objetivos

### Pre-entrega 1 — Unified Async LLM Client

Desarrollar un cliente asíncrono que permita interactuar con diferentes proveedores de modelos de lenguaje mediante una interfaz común.

La implementación incluye:

- Integración con OpenAI y Anthropic.
- Generación de respuestas asíncronas.
- Streaming de respuestas.
- Validación de mensajes y configuraciones con Pydantic.
- Selección del proveedor mediante `AsyncLLMManager`.
- Manejo de excepciones específicas.
- Configuración mediante variables de entorno.
- Pruebas automatizadas con `unittest`.

### Pre-entrega 2 — Pipeline de procesamiento validado

Implementar un pipeline que reciba texto técnico y devuelva información estructurada y validada.

Los objetivos son:

- Extraer las tecnologías mencionadas explícitamente.
- Clasificar el nivel de criticidad como `baja`, `media` o `alta`.
- Generar un resumen técnico.
- Validar la respuesta mediante Pydantic.
- Construir una cadena con LangChain Expression Language (LCEL).
- Implementar reintentos ante errores de parseo, validación o truncamiento.
- Ejecutar el procesamiento de manera asíncrona.
- Registrar los eventos relevantes mediante logging.

La segunda entrega se incorpora sin modificar la implementación del cliente original.

---

## 2. Tecnologías utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.12 | Lenguaje principal |
| OpenAI SDK | 3.45.0 | Integración con OpenAI |
| Anthropic SDK | 2.4.0 | Integración con Anthropic |
| Pydantic | 2.14.2 | Modelos y validación de datos |
| python-dotenv | 1.2.4 | Variables de entorno |
| langchain-core | 1.8.0 | Prompts, LCEL y reintentos |
| langchain-openai | 1.7.4 | Integración de ChatOpenAI |
| unittest | Biblioteca estándar | Pruebas automatizadas |
| unittest.mock | Biblioteca estándar | Simulación de dependencias |
| setuptools | Sistema de construcción | Instalación del proyecto |

Las dependencias están declaradas en `pyproject.toml` y `requirements.txt`.

---

## 3. Estructura del proyecto

```text
nexo-intelligence/
├── src/
│   ├── nexo_llm/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   ├── base_client.py
│   │   ├── openai_client.py
│   │   ├── anthropic_client.py
│   │   ├── manager.py
│   │   └── exceptions.py
│   │
│   └── nexo_pipeline/
│       ├── __init__.py
│       ├── schemas.py
│       └── chain.py
│
├── tests/
│   ├── __init__.py
│   ├── test_manager.py
│   ├── test_clients.py
│   ├── test_anthropic.py
│   ├── test_schemas.py
│   └── test_pipeline.py
│
├── main.py
├── probar_pipeline.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Responsabilidad de los módulos

**`src/nexo_llm/`**

Contiene la implementación correspondiente a la Pre-entrega 1.

- `schemas.py`: modelos Pydantic para mensajes, configuración y respuestas.
- `base_client.py`: interfaz abstracta de los clientes.
- `openai_client.py`: implementación del cliente OpenAI.
- `anthropic_client.py`: implementación del cliente Anthropic.
- `manager.py`: selección y delegación de operaciones.
- `exceptions.py`: excepciones personalizadas.

**`src/nexo_pipeline/`**

Contiene la implementación de la Pre-entrega 2.

- `schemas.py`: modelo de extracción y validaciones.
- `chain.py`: prompt, cadena LCEL, reintentos, logging y función de procesamiento.

**Archivos ejecutables**

- `main.py`: ejemplo de generación y streaming de la primera entrega.
- `probar_pipeline.py`: ejemplo de extracción técnica de la segunda entrega.

**`tests/`**

Contiene las pruebas automatizadas de ambas entregas.

---

## 4. Instalación

### Requisitos

- Python 3.12.
- Git y pip.
- Para ejecutar los ejemplos con solicitudes reales, una clave API válida, conectividad y cuota disponible en el proveedor correspondiente.

### Clonar el repositorio

```bash
git clone https://github.com/gastonjaureguib-stack/nexo-llm.git nexo-intelligence
cd nexo-intelligence
```

### Crear el entorno virtual

En Windows:

```bash
py -3.12 -m venv .venv
```

Activarlo desde Git Bash:

```bash
source .venv/Scripts/activate
```

En PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, usá `.\.venv\Scripts\python.exe` en lugar de `python` en los comandos de instalación y ejecución.

### Instalar las dependencias

```bash
python -m pip install -e .
```

La instalación editable permite trabajar directamente sobre los paquetes ubicados en `src/`.

No es necesario configurar manualmente `PYTHONPATH`.

Para comprobar la instalación:

```bash
python -m pip check
```

El resultado esperado, si no existen conflictos entre dependencias, es:

```text
No broken requirements found.
```

### Si se mueve la carpeta del proyecto

Los entornos virtuales pueden conservar rutas absolutas. Si se traslada el proyecto, puede ser necesario recrear el entorno e instalar nuevamente las dependencias.

En ese caso, desde la nueva ubicación:

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install -e .
```

---

## 5. Variables de entorno

El proyecto utiliza `python-dotenv` para cargar la configuración.

Crear un archivo `.env` en la raíz a partir de `.env.example`.

Ejemplo:

```dotenv
LLM_PROVIDER=openai

OPENAI_API_KEY=TU_CLAVE_OPENAI
ANTHROPIC_API_KEY=

OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=
```

### Variables disponibles

| Variable | Descripción |
|---|---|
| `LLM_PROVIDER` | Proveedor seleccionado para `main.py` |
| `OPENAI_API_KEY` | Clave de OpenAI |
| `ANTHROPIC_API_KEY` | Clave de Anthropic |
| `OPENAI_MODEL` | Modelo de OpenAI |
| `ANTHROPIC_MODEL` | Modelo de Anthropic |

El cliente de la primera entrega permite seleccionar OpenAI o Anthropic.

El pipeline de la segunda entrega utiliza `ChatOpenAI` y requiere `OPENAI_API_KEY`. Si `OPENAI_MODEL` no está definido o está vacío, utiliza `gpt-4o-mini`.

El archivo `.env` está excluido del repositorio mediante `.gitignore`. Las claves reales no deben incluirse en los commits.

Las solicitudes a los proveedores pueden generar costos.

---

## 6. Pre-entrega 1 — Cliente LLM asíncrono

### Arquitectura

La primera entrega utiliza una interfaz abstracta y un administrador que selecciona el proveedor correspondiente.

```text
main.py
   |
   v
AsyncLLMManager
   |
   +---- OpenAIClient
   |         |
   |         v
   |     AsyncOpenAI
   |
   +---- AnthropicClient
             |
             v
       AsyncAnthropic
```

### Modelos Pydantic

**ChatMessage**

Representa los mensajes enviados al modelo.

- `role`: `system`, `user` o `assistant`.
- `content`: contenido textual obligatorio.

**ModelConfig**

Define la configuración de generación.

- `model`: identificador del modelo.
- `temperature`: valor entre 0 y 2.
- `max_tokens`: entero mayor que 0.

Los valores predeterminados son `temperature=0.7` y `max_tokens=500`.

**ModelResponse**

Normaliza la respuesta mediante:

- `provider`: proveedor utilizado.
- `model`: modelo utilizado.
- `content`: respuesta textual.

### Interfaz BaseLLMClient

La clase abstracta define dos operaciones principales.

**`generate()`**

Realiza una solicitud asíncrona y devuelve una respuesta completa mediante `ModelResponse`.

**`stream()`**

Permite consumir los fragmentos de respuesta utilizando un generador asíncrono.

### AsyncLLMManager

El administrador recibe el proveedor configurado, selecciona el cliente correspondiente y delega las operaciones de generación y streaming.

Esto permite mantener una interfaz común sin incorporar en el Manager los detalles particulares de cada SDK.

### Manejo de excepciones

El proyecto define excepciones para representar errores conocidos de los proveedores.

| Excepción | Situación |
|---|---|
| `LLMError` | Excepción base |
| `LLMAuthenticationError` | Error de autenticación |
| `LLMConnectionError` | Error de conexión o timeout |
| `LLMRateLimitError` | Límite de solicitudes |
| `LLMAPIError` | Error general de la API |

### Ejecución

Desde la raíz del proyecto:

```bash
python main.py
```

El script utiliza la pregunta:

**¿Qué es la entropía?**

Realiza una generación completa y una generación mediante streaming.

El comportamiento depende del proveedor, modelo y credenciales configurados.

---

## 7. Pre-entrega 2 — Pipeline de extracción técnica

La segunda entrega incorpora un pipeline de procesamiento de textos técnicos mediante LangChain y Pydantic.

Recibe un texto, identifica las tecnologías mencionadas, determina el nivel de criticidad y genera un resumen técnico.

### 7.1. Modelo de datos

El archivo `src/nexo_pipeline/schemas.py` define `ExtraccionTecnica`.

```python
class ExtraccionTecnica(BaseModel):
    tecnologias: list[str] = Field(min_length=1)
    nivel_de_criticidad: NivelCriticidad
    resumen_tecnico: str = Field(min_length=1)
```

El esquema establece tres campos obligatorios.

| Campo | Tipo | Validación |
|---|---|---|
| `tecnologias` | `list[str]` | Al menos una tecnología; sin nombres vacíos |
| `nivel_de_criticidad` | Enum | `baja`, `media` o `alta` |
| `resumen_tecnico` | `str` | Texto no vacío |

El enum `NivelCriticidad` restringe los valores admitidos.

Además, se utilizan validadores para rechazar nombres de tecnologías o resúmenes que contengan únicamente espacios.

Si una respuesta incumple el esquema, Pydantic genera un error de validación.

### 7.2. Prompt modular

El archivo `chain.py` contiene las instrucciones de extracción y construye un `ChatPromptTemplate`.

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{instrucciones}"),
        ("human", "{texto}")
    ]
).partial(instrucciones=INSTRUCCIONES_EXTRACCION)
```

Las instrucciones se mantienen separadas del texto que se desea procesar.

El prompt establece los criterios de criticidad:

- **Baja:** información general, operaciones normales o avisos menores.
- **Media:** errores parciales, degradación del servicio o problemas recuperables.
- **Alta:** interrupciones del servicio, pérdida de datos o fallos críticos.

También indica que no deben inventarse tecnologías que no estén mencionadas explícitamente.

### 7.3. Cadena LCEL

La extracción se construye mediante LangChain Expression Language:

```python
cadena = prompt | modelo.with_structured_output(
    ExtraccionTecnica,
    include_raw=True
)
```

La composición conecta el prompt con el modelo configurado para producir una salida estructurada.

`with_structured_output()` utiliza el esquema Pydantic como contrato de salida.

La opción `include_raw=True` permite conservar la respuesta original junto con el resultado interpretado y los posibles errores de parseo.

Esto es necesario para verificar el estado de finalización de la respuesta antes de aceptarla.

### 7.4. Flujo de procesamiento

```text
probar_pipeline.py
        |
        v
process_text(text)
        |
        v
crear_cadena()
        |
        v
ChatPromptTemplate
        |
        v
ChatOpenAI
        |
        v
Salida estructurada
        |
        v
Validación y control de truncamiento
        |
        +---- Error recuperable
        |          |
        |          v
        |       Reintento
        |
        v
ExtraccionTecnica
        |
        v
JSON
```

La función `process_text()` es el punto de entrada del pipeline.

Recibe un texto, verifica que no esté vacío y ejecuta la cadena de manera asíncrona.

```python
async def process_text(text: str) -> ExtraccionTecnica:
```

La ejecución utiliza `.ainvoke()` y devuelve una instancia validada de `ExtraccionTecnica`.

### 7.5. Validación y reintentos

La cadena implementa resiliencia mediante `.with_retry()`.

Se permiten **hasta tres intentos en total**, incluyendo la ejecución inicial.

Los reintentos se aplican a errores de:

- Parseo de la respuesta.
- Validación de Pydantic.
- Truncamiento de la salida.

La configuración desactiva la espera exponencial con jitter mediante `wait_exponential_jitter=False`.

También se desactivan los reintentos internos del modelo con `max_retries=0`, para evitar la multiplicación de intentos entre diferentes capas.

Cada reintento vuelve a solicitar una respuesta al modelo. El pipeline no modifica manualmente el JSON inválido.

Si se agotan los intentos, se propaga el error correspondiente.

### 7.6. Detección de truncamiento

El pipeline inspecciona `finish_reason` en los metadatos de la respuesta.

Cuando el valor es `length`, se considera que la generación terminó por alcanzar el límite de tokens.

En ese caso se genera `RespuestaTruncadaError`, incluso si la información recibida parece válida.

También se contempla `LengthFinishReasonError`, que puede producirse cuando el SDK detecta el truncamiento antes de devolver la respuesta.

El modelo está configurado con un máximo de 1000 tokens por intento.

### 7.7. Logging

Se utiliza el módulo estándar `logging` de Python para registrar eventos del procesamiento.

Los registros incluyen:

- Inicio del procesamiento.
- Validación correcta.
- Errores de extracción.
- Intentos de recuperación.
- Fallo definitivo.

Los mensajes no incluyen las claves API ni el contenido completo del texto procesado o de la respuesta del proveedor.

### 7.8. Ejecución del pipeline

El archivo `probar_pipeline.py` contiene un ejemplo asíncrono.

Para ejecutarlo:

```bash
python probar_pipeline.py
```

El script procesa el siguiente texto:

```text
El servidor Node.js dejó de responder. La API devuelve errores 500 y los usuarios no pueden acceder al sistema.
```

El resultado se muestra como JSON mediante `model_dump_json(indent=2)`.

### 7.9. Ejemplo de salida

Una respuesta posible es:

```json
{
  "tecnologias": [
    "Node.js"
  ],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "El servidor Node.js dejó de responder, la API devuelve errores 500 y los usuarios no pueden acceder al sistema."
}
```

La salida es ilustrativa. El contenido exacto del resumen puede variar según la respuesta del modelo.

La criticidad esperada es alta porque el texto describe una interrupción del servicio que impide el acceso de los usuarios.

**Importante:** `probar_pipeline.py` realiza una solicitud real a OpenAI. Requiere credenciales válidas, conectividad, acceso a un modelo compatible y cuota disponible.

---

## 8. Pruebas automatizadas

El proyecto utiliza `unittest` y herramientas de simulación para verificar el comportamiento sin depender de solicitudes reales a las APIs.

### Ejecutar todas las pruebas

Desde la raíz del proyecto, después de instalarlo en modo editable con el intérprete del entorno virtual:

```bash
python -m unittest discover -v
```

Las pruebas funcionan sin archivo `.env` ni claves de API. Los SDK se simulan en las pruebas de los clientes. La prueba de integración de LangChain usa un transporte HTTP en memoria y el trazado externo está desactivado durante las pruebas del pipeline.

### Ejecutar únicamente las pruebas del pipeline

```bash
python -m unittest tests.test_pipeline -v
```

### Resultados

| Componente | Pruebas aprobadas |
|---|---:|
| AsyncLLMManager | 5 |
| OpenAIClient | 7 |
| AnthropicClient | 7 |
| Esquemas de la Pre-entrega 1 | 15 |
| Pipeline de la Pre-entrega 2 | 14 |
| **Total** | **48** |

### Pruebas de la Pre-entrega 1

Se comprueban:

- Selección y rechazo de proveedores.
- Delegación de generación y streaming.
- Manejo de errores de autenticación.
- Errores de conexión y límites de solicitudes.
- Generación y streaming simulados.
- Validación de los modelos Pydantic.

### Pruebas de la Pre-entrega 2

Se comprueban:

- Extracción asíncrona con respuestas simuladas.
- Validación de campos obligatorios.
- Rechazo de valores inválidos.
- Errores de parseo.
- Reintentos después de respuestas inválidas.
- Recuperación después de un error.
- Agotamiento de los intentos.
- Detección de respuestas truncadas.
- Manejo de errores no recuperables.
- Rechazo de textos vacíos.
- Registro de eventos mediante logging.
- Integración del parser de `ChatOpenAI` sin acceso a la red.

Las pruebas de la segunda entrega utilizan modelos simulados y mocks para comprobar la lógica del pipeline.

Los 34 tests originales de la primera entrega se mantienen y se ejecutan junto con los 14 nuevos.

---

## 9. Seguridad y limitaciones

### Seguridad

- Las claves se gestionan mediante variables de entorno.
- `.env` está excluido del repositorio.
- Se utiliza un entorno virtual independiente.
- Los datos estructurados se validan mediante Pydantic.
- Los errores recuperables se controlan mediante reintentos limitados.
- El logging evita registrar claves y contenido completo de las solicitudes.

### Limitaciones

La Pre-entrega 1 permite trabajar con OpenAI y Anthropic mediante una interfaz común, mientras que el pipeline de la segunda entrega utiliza específicamente OpenAI.

La extracción requiere al menos una tecnología identificable. Si el texto no menciona ninguna, el esquema no admite una lista vacía y el modelo debe cumplir esa restricción.

El pipeline no incluye interfaz gráfica, persistencia de resultados ni almacenamiento de conversaciones.

Las pruebas automatizadas comprueban el comportamiento utilizando simulaciones. **No se ha verificado una ejecución real del pipeline contra OpenAI durante esta implementación.**

Por lo tanto, los tests aprobados no garantizan la disponibilidad de credenciales, conectividad, cuota o acceso al modelo en una ejecución real.

---

## 10. Estado del proyecto

**Pre-entrega 1 — Unified Async LLM Client**

Implementada y conservada en `src/nexo_llm/`.

**Pre-entrega 2 — Pipeline de procesamiento validado**

Implementada en `src/nexo_pipeline/`, con extracción estructurada, validación, reintentos, logging y ejecución asíncrona.

**Pruebas automatizadas:** 48 aprobadas.

---

## Autor

**Gastón Jaureguiberry**

AI Engineering — Coderhouse

GitHub: https://github.com/gastonjaureguib-stack

Repositorio: https://github.com/gastonjaureguib-stack/nexo-llm
