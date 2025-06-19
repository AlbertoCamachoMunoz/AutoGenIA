
# 📖 Documentación del Proyecto – AutoGenIA 🪄🤖

## 1️⃣ Arquitectura del Proyecto (Clean Architecture)

Este proyecto implementa la **Clean Architecture**, separando claramente la lógica de negocio de los detalles de infraestructura y presentación.  
Se aplica además **Inversión de Dependencias** mediante inyección de dependencias para que las capas superiores (Application) no dependan de las inferiores (Infrastructure).  
El resultado es un código **modular, escalable y fácil de mantener**.

---

### 📂 **Estructura del Proyecto**
```
<pre><code>
📁 AutoGenIA
│
├── application                # Reglas de negocio (DTOs, interfaces, casos de uso)
│   ├── dtos                   # Data Transfer Objects
│   ├── enums                  # Enumeradores
│   ├── factories              # Patrones Factory
│   ├── interfaces             # Interfaces/abstracciones
│   ├── use_cases              # Casos de uso
│   ├── buffer                 # Buffer thread-safe compartido
│   └── config                 # Configuración global (API keys, rutas, ...)
│
├── infrastructure             # Servicios externos concretos
│   ├── autogen_adapters       # Wrappers → AutoGen
│   ├── agents                 # Agentes concretos (WebScraper, Email, Wikipedia...)
│   └── llms_providers         # Proveedores LLM (Gemini, LLM Studio)
│
├── presentation               # Capa de presentación
│   ├── api                    # API REST (Flask)
│   ├── cli                    # CLI interactiva
│   └── front_app              # Frontend (HTML + CSS + JS)
│       ├── generated_audio    # (reservado futuro)
│       ├── temp_uploads       # (reservado futuro)
│       └── utils              # Utilidades (validadores, helpers…)
</code></pre>
```

---

## 2️⃣ Explicación de cada carpeta

### 📂 **application/**  
Define la lógica de negocio **independiente de frameworks**:

| Sub‑carpeta | Descripción |
|-------------|-------------|
| **dtos** | Objetos de transferencia de datos utilizados entre capas. |
| **enums** | Enumeraciones tipadas (p.ej. `StatusCode`, `LLMProvider`). |
| **factories** | Implementa **Factory Pattern** para seleccionar proveedores LLM. |
| **interfaces** | Contratos que infraestructura debe implementar (`LLMInterface`, `AgentInterface`). |
| **use_cases** | Casos de uso orquestados desde presentación (p.ej. `autogen_runtime.py`). |

### 📂 **config/**  
Parámetros globales: URLs, API‑keys, rutas de audio, SMTP, etc.  
Incluye `settings.py` (producción) y `settings.dev.py` (desarrollo).

### 📂 **infrastructure/**  
Implementaciones concretas que cumplen las interfaces de `application`.

- **agents/** → Agentes de dominio (WebScraper, Email, Wikipedia).  
- **llms_providers/** → Adaptadores a servicios LLM (Google Gemini, LLM Studio).  
- **autogen_adapters/** → Wrappers que exponen los agentes a **AutoGen** vía *function calling*.  
- **autogen_agents/** → Planner estricto que solo emite llamadas JSON de herramienta válidas.

### 📂 **presentation/**  
Interactúa con el usuario mediante **API REST + CLI + Frontend**.

| Sub‑carpeta | Rol |
|-------------|-----|
| **api/** | Servicio Flask que recibe `/chat` y despacha al planner. |
| **cli/** | Terminal interactiva (`python -m presentation.cli_app`). |
| **front_app/** | Interfaz web (Bootstrap 5) con modales y estilo *tech‑elegante*. |

---

## 3️⃣ Explicación de `presentation/api.py`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/`        | Devuelve la SPA (`index.html`). |
| `POST` | `/chat`    | Cuerpo JSON → `{"prompt": "...", "llm_type": "llm_studio"}` ; retorna un JSON con la conversación ejecutada por AutoGen. |

### ▶️ Levantar el servidor Flask
```bash
python -m presentation.api
```

El backend quedará disponible en <http://127.0.0.1:5000/>

### 🛰️ Ejemplo de llamada cURL
```bash
curl -X POST http://127.0.0.1:5000/chat      -H "Content-Type: application/json"      -d '{"prompt": "🎩 scrape thefansofmagicstore.com", "llm_type": "llm_studio"}'
```

Respuesta típica:
```json
{
  "status": "success",
  "data": {
    "products": [
      {"description": "...", "price": "€19,95", "sku": "SKU123"}
    ],
    "status": "SUCCESS",
    "message": "OK"
  }
}
```

---

## 4️⃣ Uso de la CLI
```bash
python -m presentation.cli_app
```
1. Selecciona el proveedor LLM.  
2. Escribe tu prompt (o `exit` para salir).  
La CLI imprimirá el JSON resultante de AutoGen.

---

## 5️⃣ Notas Adicionales

- **Inyección de dependencias** mediante `DependencyInjector` para cachear proveedores LLM y reutilizar instancias de agentes.  
- **Manejo de errores & logging** detallado en infraestructura (HTTP, SMTP, LLM).  
- **DTOs + Factory + Strategy** permiten añadir nuevos agentes/LLMs sin tocar lógica de negocio.  
- El **Planner** penaliza cualquier salida que no sea un *tool call* JSON, garantizando robustez.

---

## 6️⃣ Requisitos Previos

| Requisito | Versión recomendada |
|-----------|--------------------|
| **Python** | ≥ 3.10 |
| **pip** | Última |
| **Modelo LLM** | *Hermes‑2‑Pro‑Llama‑3‑8B* cargado en **LM Studio** u **Ollama** |
| **Servidor LLM** | API accesible en `http://localhost:1234/v1` (editar en `config/settings.py` si cambia) |
| **SMTP** | Cuenta Mailtrap de pruebas (o configurar la tuya) |

> ⚠️ **Importante:** Si cambias la URL del servidor LLM recuerda actualizarla en  
> `config/settings.py → LLM_STUDIO_API_URL`.

---

## 7️⃣ Instalación Rápida

1. Clona el repositorio  
   ```bash
   git clone <tu‑repo>.git && cd AutoGenIA
   ```
2. Crea entorno virtual  
   ```bash
   python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Instala dependencias  
   ```bash
   pip install -r requirements.txt
   ```
4. Inicia el backend  
   ```bash
   python -m presentation.api
   ```
5. Navega a <http://127.0.0.1:5000/> y ¡disfruta!

---

## 8️⃣ Licencia
Este proyecto se proporciona con fines **educativos y demostrativos**.  
Úsalo bajo tu propia responsabilidad.
