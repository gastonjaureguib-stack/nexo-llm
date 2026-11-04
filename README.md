# Nexo LLM

### Unified Async LLM Client | Python 3.12

**Pre-entrega 1 — AI Engineering | Coderhouse**

Nexo LLM es un cliente unificado, robusto y asíncrono para interactuar con modelos de lenguaje de **OpenAI y Anthropic** mediante una interfaz común.

El proyecto implementa generación de respuestas, streaming asíncrono, validación de datos con Pydantic, manejo centralizado de errores y pruebas automatizadas.

**Repositorio:** https://github.com/gastonjaureguib-stack/nexo-llm

---

## 1. Objetivos del proyecto

El objetivo principal es desarrollar un cliente LLM extensible que permita utilizar diferentes proveedores sin modificar la lógica principal de la aplicación.

La implementación contempla:

- Una interfaz abstracta común para los proveedores.
- Integración con los SDK oficiales de OpenAI y Anthropic.
- Solicitudes asíncronas mediante `async` y `await`.
- Streaming mediante generadores asíncronos, `yield` y `async for`.
- Validación de mensajes y configuraciones mediante Pydantic.
- Selección dinámica del proveedor a través de un Manager.
- Manejo de excepciones específicas.
- Configuración segura mediante variables de entorno.
- Pruebas automatizadas con `unittest`.

## 2. Tecnologías utilizadas

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.12 | Lenguaje principal |
| OpenAI SDK | 3.45.0 | Integración con OpenAI |
| Anthropic SDK | 2.4.0 | Integración con Anthropic |
| Pydantic | 2.14.2 | Validación de datos |
| python-dotenv | 1.2.4 | Gestión de variables de entorno |
| unittest | Biblioteca estándar | Pruebas automatizadas |
| unittest.mock | Biblioteca estándar | Simulación de APIs |
| setuptools | Sistema de construcción | Instalación del paquete |

## 3. Arquitectura del proyecto

El proyecto utiliza una arquitectura modular basada en una interfaz abstracta, implementaciones específicas por proveedor y un Manager encargado de seleccionar y delegar las operaciones.

```text
pre-entrega-1/
│
├── src/
│   └── nexo_llm/
│       ├── __init__.py
│       ├── schemas.py
│       ├── base_client.py
│       ├── openai_client.py
│       ├── anthropic_client.py
│       ├── manager.py
│       └── exceptions.py
│
├── tests/
│   ├── test_manager.py
│   ├── test_clients.py
│   ├── test_anthropic.py
│   └── test_schemas.py
│
├── main.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Responsabilidad de cada módulo

**`schemas.py`**

Define los modelos de datos utilizados por la aplicación mediante Pydantic.

**`base_client.py`**

Establece el contrato abstracto que deben implementar los clientes de los distintos proveedores.

**`openai_client.py`**

Implementa la comunicación asíncrona con OpenAI, incluyendo generación, streaming y traducción de errores.

**`anthropic_client.py`**

Implementa la comunicación asíncrona con Anthropic, incluyendo el tratamiento específico de mensajes de sistema.

**`manager.py`**

Selecciona el cliente correspondiente al proveedor configurado y delega las operaciones de generación y streaming.

**`exceptions.py`**

Centraliza las excepciones personalizadas de la aplicación.

**`main.py`**

Funciona como punto de entrada y demuestra la generación normal y en streaming.

**`tests/`**

Contiene las pruebas automatizadas de los componentes principales.

## 4. Flujo de funcionamiento

El flujo general de Nexo LLM es:

```text
main.py
   |
   v
AsyncLLMManager
   |
   +---- OpenAIClient
   |        |
   |        +---- AsyncOpenAI
   |
   +---- AnthropicClient
            |
            +---- AsyncAnthropic
```

1. `main.py` carga la configuración del entorno.
2. Se selecciona el proveedor indicado en `LLM_PROVIDER`.
3. `AsyncLLMManager` instancia el cliente correspondiente.
4. El cliente valida y utiliza los datos recibidos mediante los esquemas definidos.
5. Se ejecuta la solicitud asíncrona al proveedor.
6. La respuesta se devuelve de forma normalizada o mediante fragmentos de streaming.
7. Los errores conocidos se traducen a excepciones comunes de Nexo LLM.

## 5. Instalación

### Requisitos previos

- Python 3.12.
- pip.
- Git.
- Conexión a internet para utilizar las APIs.
- Una clave API válida del proveedor seleccionado.
- Acceso a un modelo compatible y cuota disponible.

### Clonar el repositorio

```bash
git clone https://github.com/gastonjaureguib-stack/nexo-llm.git
cd nexo-llm
```

### Crear el entorno virtual

En Windows:

```bash
py -3.12 -m venv .venv
```

### Activar el entorno virtual

Git Bash:

```bash
source .venv/Scripts/activate
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Instalar el proyecto

```bash
python -m pip install -e .
```

Este comando instala Nexo LLM en modo editable, junto con las dependencias declaradas en `pyproject.toml`.

La instalación editable permite trabajar directamente sobre los archivos de `src/nexo_llm/` sin reinstalar el paquete después de cada modificación.

No es necesario configurar manualmente `PYTHONPATH`.

También se incluye `requirements.txt` como referencia de las dependencias utilizadas.

### Verificar las dependencias

```bash
python -m pip check
```

Si la instalación es correcta, el resultado esperado es:

```text
No broken requirements found.
```

## 6. Configuración de variables de entorno

El proyecto utiliza `python-dotenv` para cargar las variables de entorno.

Crear un archivo `.env` en la raíz del proyecto tomando como referencia `.env.example`.

### Ejemplo de configuración para OpenAI

```dotenv
LLM_PROVIDER=openai

OPENAI_API_KEY=TU_CLAVE_OPENAI
ANTHROPIC_API_KEY=

OPENAI_MODEL=MODELO_OPENAI_COMPATIBLE
ANTHROPIC_MODEL=
```

### Ejemplo de configuración para Anthropic

```dotenv
LLM_PROVIDER=anthropic

OPENAI_API_KEY=
ANTHROPIC_API_KEY=TU_CLAVE_ANTHROPIC

OPENAI_MODEL=
ANTHROPIC_MODEL=MODELO_ANTHROPIC_COMPATIBLE
```

### Variables disponibles

| Variable | Descripción |
|---|---|
| `LLM_PROVIDER` | Proveedor activo: `openai` o `anthropic` |
| `OPENAI_API_KEY` | Clave de autenticación de OpenAI |
| `ANTHROPIC_API_KEY` | Clave de autenticación de Anthropic |
| `OPENAI_MODEL` | Identificador del modelo de OpenAI |
| `ANTHROPIC_MODEL` | Identificador del modelo de Anthropic |

Los identificadores de modelo deben corresponder a modelos habilitados para la cuenta del proveedor y compatibles con los parámetros utilizados.

**Seguridad:** nunca incluir claves reales en el repositorio. El archivo `.env` está excluido mediante `.gitignore`.

Las solicitudes reales pueden generar costos según las condiciones de cada proveedor.

## 7. Ejecución de la aplicación

Desde la raíz del proyecto, con el entorno virtual activado y el paquete instalado:

```bash
python main.py
```

La aplicación ejecuta la pregunta establecida en la consigna:

**¿Qué es la entropía?**

Se realizan dos operaciones consecutivas.

### Generación normal

Se utiliza `await` para obtener una respuesta completa:

```python
response = await manager.generate(
    messages,
    config
)

print(response.content)
```

### Generación mediante streaming

Se utiliza `async for` para procesar los fragmentos de respuesta a medida que se reciben:

```python
async for fragment in manager.stream(
    messages,
    config
):
    print(fragment, end="", flush=True)
```

La aplicación presenta el proveedor, el modelo y la pregunta utilizada.

Si se produce un error conocido, se muestra un mensaje controlado.

## 8. Interfaz abstracta BaseLLMClient

`BaseLLMClient` define los métodos comunes que deben implementar los proveedores.

### generate()

Método asíncrono encargado de solicitar una respuesta completa.

Recibe:

- `messages`: lista de objetos `ChatMessage`.
- `config`: objeto `ModelConfig`.

Devuelve:

- `ModelResponse`.

### stream()

Método que permite consumir una respuesta mediante un iterador asíncrono de fragmentos de texto.

Esta interfaz permite que `AsyncLLMManager` utilice ambos proveedores sin incorporar lógica específica de sus SDK.

## 9. Modelos de datos con Pydantic

### ChatMessage

Representa un mensaje de conversación.

| Campo | Tipo | Validación |
|---|---|---|
| `role` | Literal | `system`, `user` o `assistant` |
| `content` | str | No puede estar vacío |

### ModelConfig

Representa la configuración de generación.

| Campo | Tipo | Validación |
|---|---|---|
| `model` | str | No puede estar vacío |
| `temperature` | float | Entre 0 y 2 |
| `max_tokens` | int | Mayor que 0 |

Valores predeterminados:

- `temperature`: 0.7.
- `max_tokens`: 500.

### ModelResponse

Normaliza las respuestas de los proveedores mediante tres campos obligatorios:

- `provider`: proveedor utilizado.
- `model`: modelo que generó la respuesta.
- `content`: contenido textual de la respuesta.

Las validaciones de Pydantic controlan la estructura y los límites definidos en los esquemas. Las restricciones específicas de cada proveedor también deben respetarse.

## 10. Manejo de excepciones

Nexo LLM utiliza una jerarquía de excepciones personalizadas para representar errores de manera uniforme.

| Excepción | Situación |
|---|---|
| `LLMError` | Excepción base |
| `LLMAuthenticationError` | Credenciales rechazadas |
| `LLMConnectionError` | Fallo de conexión o timeout |
| `LLMRateLimitError` | Límite de solicitudes o cuota |
| `LLMAPIError` | Error HTTP general del proveedor |

Los clientes capturan errores conocidos de sus respectivos SDK y los transforman en excepciones propias de Nexo LLM.

Esto permite que la aplicación maneje los errores sin depender directamente de las clases específicas de cada proveedor.

## 11. Pruebas automatizadas

El proyecto utiliza `unittest`, `AsyncMock` y `MagicMock` para verificar el comportamiento de los componentes sin realizar solicitudes reales a las APIs.

### Ejecutar todas las pruebas

```bash
python -m unittest discover -s tests -v
```

### Resultados verificados

| Componente | Pruebas aprobadas |
|---|---:|
| AsyncLLMManager | 5 |
| OpenAIClient | 7 |
| AnthropicClient | 7 |
| Esquemas Pydantic | 15 |
| **Total** | **34** |

Resultado de la ejecución local:

```text
Ran 34 tests in 0.367s

OK
```

### Escenarios comprobados

**AsyncLLMManager**

- Selección de OpenAI.
- Selección de Anthropic.
- Rechazo de proveedores desconocidos.
- Delegación de generación asíncrona.
- Delegación de streaming asíncrono.

**OpenAIClient**

- Autenticación fallida.
- Límite de solicitudes.
- Error de conexión.
- Error HTTP general.
- Error de autenticación durante streaming.
- Generación exitosa simulada.
- Streaming exitoso simulado.

**AnthropicClient**

- Autenticación fallida.
- Límite de solicitudes.
- Error de conexión.
- Error HTTP general.
- Error de autenticación durante streaming.
- Generación exitosa simulada.
- Streaming exitoso simulado.

**Pydantic**

- Roles válidos e inválidos.
- Contenido obligatorio.
- Valores predeterminados.
- Límites de temperatura.
- Valores válidos e inválidos de tokens.
- Identificador de modelo obligatorio.
- Campos obligatorios de respuesta.

### Alcance de las pruebas

Las 34 pruebas automatizadas utilizan simulaciones de las respuestas y errores de los proveedores.

Se verificó también:

- Instalación editable del paquete.
- Importaciones sin `PYTHONPATH`.
- Consistencia de dependencias mediante `pip check`.

**No se ha confirmado todavía una ejecución real de `main.py` contra las APIs de OpenAI o Anthropic.** Por lo tanto, las pruebas automatizadas no deben interpretarse como evidencia de conectividad real, disponibilidad de modelos o credenciales válidas.

## 12. Seguridad y buenas prácticas

El proyecto aplica las siguientes prácticas:

- Uso de variables de entorno para credenciales.
- Exclusión de `.env` del repositorio.
- Entorno virtual independiente.
- Separación modular de responsabilidades.
- Interfaz abstracta común.
- Validación de entradas mediante Pydantic.
- Manejo centralizado de errores conocidos.
- Pruebas automatizadas independientes de servicios externos.
- Dependencias con versiones fijadas.
- Configuración de instalación mediante `pyproject.toml`.

## 13. Alcance y limitaciones

Esta implementación corresponde a la primera pre-entrega de AI Engineering y se concentra en construir una base funcional para interactuar con proveedores LLM.

Incluye generación normal, streaming, validación, selección de proveedores y manejo de errores conocidos.

No incluye interfaz gráfica, persistencia de conversaciones ni almacenamiento de respuestas.

Tampoco implementa una política propia de reintentos; el comportamiento de reintentos del SDK depende de su configuración y versión.

La ejecución real requiere credenciales, conectividad y modelos compatibles.

---

## Autor

**Gastón Jaureguiberry**

AI Engineering — Coderhouse

GitHub: https://github.com/gastonjaureguib-stack

Repositorio: https://github.com/gastonjaureguib-stack/nexo-llm

---

**Nexo LLM — Pre-entrega 1 | AI Engineering | Coderhouse**