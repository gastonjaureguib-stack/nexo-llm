# Nexo LLM

**Cliente unificado, robusto y asíncrono para modelos de lenguaje (LLM)**

Proyecto desarrollado en Python 3.12 como parte de la Pre-entrega 1 del curso de AI Engineering de Coderhouse.

## 1. Descripción

Nexo LLM es una aplicación Python que unifica la interacción con los proveedores OpenAI y Anthropic mediante una interfaz común.

Permite realizar solicitudes asíncronas a modelos de lenguaje, recibir respuestas completas y procesar respuestas en streaming, sin necesidad de modificar la lógica principal al cambiar de proveedor.

La aplicación incorpora validación de datos mediante Pydantic, manejo de excepciones específicas y pruebas automatizadas.

## 2. Objetivos

- Implementar una interfaz abstracta común para distintos proveedores de LLM.
- Utilizar los SDK oficiales de OpenAI y Anthropic.
- Ejecutar solicitudes mediante `async` y `await`.
- Implementar streaming asíncrono utilizando `yield` y `async for`.
- Validar mensajes y configuraciones con Pydantic.
- Centralizar la selección del proveedor mediante un Manager.
- Gestionar errores de autenticación, conexión, límites de solicitudes y respuestas HTTP.
- Mantener una arquitectura modular, organizada y comprobable.

## 3. Tecnologías

| Tecnología | Versión | Función |
|---|---|---|
| Python | 3.12 | Lenguaje principal |
| OpenAI SDK | 3.45.0 | Integración con OpenAI |
| Anthropic SDK | 2.4.0 | Integración con Anthropic |
| Pydantic | 2.14.2 | Validación de datos |
| python-dotenv | 1.2.4 | Variables de entorno |
| unittest | Biblioteca estándar | Pruebas automatizadas |
| setuptools | Sistema de construcción | Instalación del paquete |

## 4. Estructura del proyecto

```text
pre-entrega-1/
├── src/
│   └── nexo_llm/
│       ├── __init__.py
│       ├── schemas.py
│       ├── base_client.py
│       ├── openai_client.py
│       ├── anthropic_client.py
│       ├── manager.py
│       └── exceptions.py
├── tests/
│   ├── test_manager.py
│   ├── test_clients.py
│   ├── test_anthropic.py
│   └── test_schemas.py
├── main.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Responsabilidades

**`schemas.py`**

Define los modelos Pydantic `ChatMessage`, `ModelConfig` y `ModelResponse`.

**`base_client.py`**

Define la interfaz abstracta `BaseLLMClient`, que establece los métodos de generación y streaming.

**`openai_client.py`**

Implementa la integración asíncrona con OpenAI.

**`anthropic_client.py`**

Implementa la integración asíncrona con Anthropic, incluyendo el tratamiento de mensajes de sistema.

**`manager.py`**

Selecciona el proveedor configurado y delega las operaciones a su cliente correspondiente.

**`exceptions.py`**

Define excepciones personalizadas para unificar el manejo de errores entre proveedores.

**`main.py`**

Es el punto de entrada de la aplicación y demuestra ambos modos de generación.

**`tests/`**

Contiene las pruebas automatizadas de los componentes principales.

## 5. Requisitos previos

- Python 3.12 o compatible.
- pip.
- Acceso a internet para utilizar las APIs.
- Una clave API válida del proveedor seleccionado.
- Acceso a un modelo compatible y cuota disponible.

Las solicitudes reales pueden generar costos según las condiciones de cada proveedor.

## 6. Instalación

Clonar el repositorio:

```bash
git clone URL_DEL_REPOSITORIO
cd pre-entrega-1
```

Crear el entorno virtual:

```bash
py -3.12 -m venv .venv
```

Activarlo en Git Bash (Windows):

```bash
source .venv/Scripts/activate
```

Instalar las dependencias y el paquete en modo editable:

```bash
python -m pip install -e .
```

La instalación editable permite importar `nexo_llm` directamente desde el código ubicado en `src/`, sin configurar manualmente `PYTHONPATH`.

También se incluye `requirements.txt` como referencia de las dependencias utilizadas.

## 7. Configuración

Crear un archivo `.env` en la raíz del proyecto tomando como referencia `.env.example`.

Ejemplo para OpenAI:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=TU_CLAVE_OPENAI
ANTHROPIC_API_KEY=
OPENAI_MODEL=MODELO_OPENAI_COMPATIBLE
ANTHROPIC_MODEL=
```

Ejemplo para Anthropic:

```dotenv
LLM_PROVIDER=anthropic
OPENAI_API_KEY=
ANTHROPIC_API_KEY=TU_CLAVE_ANTHROPIC
OPENAI_MODEL=
ANTHROPIC_MODEL=MODELO_ANTHROPIC_COMPATIBLE
```

Los nombres de modelo deben corresponder a modelos disponibles para la cuenta del proveedor y compatibles con los parámetros utilizados por la aplicación.

**Seguridad:** el archivo `.env` está excluido del control de versiones mediante `.gitignore`. Nunca deben publicarse claves API reales.

## 8. Ejecución

Desde la raíz del proyecto, con el entorno virtual activado y el paquete instalado:

```bash
python main.py
```

La aplicación utiliza la pregunta:

**¿Qué es la entropía?**

El flujo de ejecución realiza:

1. Carga de las variables de entorno.
2. Validación del proveedor seleccionado.
3. Verificación de la presencia de clave API y modelo.
4. Creación del `AsyncLLMManager`.
5. Generación de una respuesta completa.
6. Generación de una respuesta mediante streaming.
7. Presentación de los resultados en consola.

La aplicación ejecuta ambas solicitudes secuencialmente y utiliza operaciones asíncronas para comunicarse con el proveedor.

## 9. Interfaz unificada

`BaseLLMClient` establece el contrato que deben cumplir los proveedores.

**Generación normal**

El método `generate()` recibe una lista de mensajes y una configuración, y devuelve un `ModelResponse`.

**Streaming**

El método `stream()` permite recibir fragmentos de texto mediante un iterador asíncrono.

Esta separación permite que el Manager trabaje con ambos proveedores mediante operaciones comunes.

## 10. Validación con Pydantic

### ChatMessage

Representa un mensaje de conversación.

- `role`: `system`, `user` o `assistant`.
- `content`: texto no vacío.

### ModelConfig

Representa la configuración de una solicitud.

- `model`: identificador no vacío.
- `temperature`: valor entre 0 y 2; predeterminado 0.7.
- `max_tokens`: entero positivo; predeterminado 500.

### ModelResponse

Representa una respuesta normalizada.

- `provider`: proveedor utilizado.
- `model`: modelo que generó la respuesta.
- `content`: texto de la respuesta.

Estas validaciones controlan la estructura de los datos, pero no sustituyen las restricciones específicas que pueda imponer cada API.

## 11. Manejo de errores

Nexo LLM utiliza excepciones personalizadas para representar situaciones comunes:

| Excepción | Descripción |
|---|---|
| `LLMError` | Excepción base |
| `LLMAuthenticationError` | Credenciales rechazadas |
| `LLMConnectionError` | Error de conexión o timeout |
| `LLMRateLimitError` | Límite de solicitudes o cuota |
| `LLMAPIError` | Error HTTP general del proveedor |

Los clientes traducen errores de los SDK a excepciones comunes, que pueden ser procesadas por la aplicación.

## 12. Pruebas automatizadas

El proyecto utiliza `unittest` y simulaciones con `unittest.mock` para verificar el comportamiento sin depender de conexiones reales a las APIs.

Ejecutar todas las pruebas:

```bash
python -m unittest discover -s tests -v
```

### Cobertura de escenarios

| Componente | Pruebas |
|---|---:|
| AsyncLLMManager | 5 |
| OpenAIClient | 7 |
| AnthropicClient | 7 |
| Esquemas Pydantic | 15 |
| **Total** | **34** |

Se verificaron:

- Selección de proveedores.
- Rechazo de proveedores desconocidos.
- Delegación asíncrona.
- Generación normal simulada.
- Streaming simulado.
- Errores de autenticación.
- Límites de solicitudes.
- Errores de conexión.
- Errores HTTP.
- Roles válidos e inválidos.
- Campos obligatorios.
- Valores predeterminados.
- Límites de temperatura y tokens.

**Resultado verificado:** 34 pruebas ejecutadas y aprobadas.

También se comprobó la instalación editable del paquete, su importación sin `PYTHONPATH` y la consistencia de dependencias mediante `python -m pip check`.

### Alcance de las verificaciones

Las pruebas automatizadas utilizan respuestas y errores simulados. No constituyen evidencia de una conexión real exitosa con OpenAI o Anthropic.

La ejecución de `main.py` con claves reales y modelos habilitados queda sujeta a disponer de credenciales válidas y acceso a los servicios.

## 13. Seguridad y buenas prácticas

- Claves API gestionadas mediante variables de entorno.
- Exclusión de `.env` y `.venv/` del repositorio.
- Separación de responsabilidades por módulos.
- Contrato común mediante clase abstracta.
- Validación de datos con Pydantic.
- Manejo explícito de errores.
- Pruebas automatizadas independientes de servicios externos.
- Instalación reproducible mediante `pyproject.toml`.

## 14. Alcance de la entrega

Esta implementación corresponde a la primera pre-entrega de AI Engineering y está enfocada en la construcción de un cliente LLM unificado, asíncrono y verificable.

No incluye interfaz gráfica, almacenamiento de conversaciones, persistencia de datos ni mecanismos de reintentos adicionales.

---

**Nexo LLM — Pre-entrega 1 | AI Engineering | Coderhouse**