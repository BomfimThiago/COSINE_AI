# 🤖 Automatización de Tickets Multi-Agente con Slack y Linear

## ¿Qué es este proyecto? 🚀

Una solución inteligente de automatización de tickets que integra Slack y Linear mediante un sistema multi-agente. Olvídate de gestionar manualmente solicitudes: los agentes colaboran y automatizan la creación, seguimiento y cierre de tickets desde Slack, optimizando la comunicación y ahorrando tiempo.

---

## ✨ Características principales

- Integración bidireccional entre Slack y Linear.
- Orquestador multi-agente: separación de responsabilidades y colaboración entre agentes especializados.
- Soporte para colas de mensajes (Redis o RabbitMQ) para máxima escalabilidad.
- Prompts personalizables para ajustar el comportamiento de los agentes.
- Fácil despliegue local y extensible.
- Soporte para notificaciones y actualizaciones en tiempo real en Slack.
- Pruebas automatizadas y guía de contribución.

---

## 🛠️ Arquitectura del sistema

```
+-----------------+           +------------------+           +-------------------+
|     Usuario     |<--------->|     Slack Bot    |<--------->| OrchestratorAgent |
+-----------------+           +------------------+           +--------+----------+
                                                                      |
                                                                      v
                                                             +--------+----------+
                                                             |  FrontendAgent    |
                                                             +-------------------+
                                                                      |
                                                                      v
                                                             +--------+----------+
                                                             |  BackendAgent     |
                                                             +-------------------+
                                                                      |
                                                                      v
                                                      +---------------+---------------+
                                                      |         Colas (Redis/RabbitMQ) |
                                                      +---------------+---------------+
                                                                      |
                                                                      v
                                                             +--------+----------+
                                                             |    Linear API     |
                                                             +-------------------+
```

**Descripción de agentes y componentes:**

- **OrchestratorAgent**: Recibe solicitudes desde Slack, coordina el flujo y delega tareas a los agentes especializados.
- **FrontendAgent**: Comprende y refina los requerimientos del usuario, interactúa para aclarar detalles.
- **BackendAgent**: Gestiona la creación, actualización y cierre de tickets directamente en Linear.
- **Colas (Redis/RabbitMQ)**: Permiten comunicación asíncrona y escalabilidad entre agentes.
- **Slack**: Punto de contacto principal para los usuarios.
- **Linear**: Sistema de gestión de tickets y tareas.

---

## 📁 Estructura del repositorio

```
agents/
  orchestrator_agent.py
  frontend_agent.py
  backend_agent.py
integrations/
  slack_client.py
  linear_client.py
queues/
  redis_queue.py
  rabbitmq_queue.py
utils/
  prompts.py
  config.py
tests/
  test_agents.py
  test_integrations.py
  test_queues.py
README.md
requirements.txt
.env.example
```

---

## ⚙️ Tecnologías y dependencias clave

- **Python 3.11** 🐍
- [`slack-sdk`](https://slack.dev/python-slack-sdk/)
- [`linear-api`](https://developers.linear.app/docs/graphql/getting-started)
- [`langchain`](https://python.langchain.com/)
- **Redis** o **RabbitMQ** (según configuración)
- [`python-dotenv`](https://pypi.org/project/python-dotenv/)
- [`pytest`](https://docs.pytest.org/)
- Otros: `requests`, `typing`, `logging`, etc.

---

## 📋 Requisitos previos

- Python 3.11 instalado.
- Acceso a [Slack](https://slack.com/) (crear un bot y obtener credenciales).
- Cuenta en [Linear](https://linear.app/) (obtener API key).
- Instancia de Redis o RabbitMQ en funcionamiento (local o remota).
- Git.

---

## 🚦 Instalación y puesta en marcha local

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/tu-repo-ticket-bot.git
   cd tu-repo-ticket-bot
   ```

2. **Crea y activa un entorno virtual**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**
   - Copia el archivo `.env.example` a `.env` y complétalo con tus credenciales.

5. **Inicia los agentes**
   ```bash
   python agents/orchestrator_agent.py
   # En otras terminales puedes iniciar frontend_agent y backend_agent si se despliegan por separado
   ```

---

## 🔑 Variables de entorno necesarias

Configura un archivo `.env` en la raíz del proyecto con los siguientes valores:

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
LINEAR_API_KEY=...
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
LANGCHAIN_API_KEY=...
# Otros valores según integración
```

---

## ⚡ Guía rápida de uso

1. **Crea un ticket de prueba desde Slack**
   - Escribe en el canal de tu bot de Slack:  
     `@TuBot crear ticket: "No puedo acceder al sistema de facturación"`
2. **Respuesta automática**
   - El OrchestratorAgent y los agentes colaborarán para crear el ticket en Linear.
   - Recibirás una notificación en Slack con el número y enlace al ticket creado en Linear.

> **Tip:** Puedes personalizar el prompt o la interacción agregando detalles o archivos adjuntos.

---

## 🗣️ Prompts personalizados

Los prompts y flujos conversacionales se encuentran en `utils/prompts.py`.

- Edita los mensajes, instrucciones y templates para adaptar el comportamiento de los agentes a tu organización.
- Ejemplo:
  ```python
  # utils/prompts.py
  FRONTEND_AGENT_PROMPT = "Por favor, describe el problema con el mayor detalle posible..."
  ```

---

## 🧪 Cómo correr tests

1. **Ejecuta todos los tests**
   ```bash
   pytest tests/
   ```

2. **Cobertura y pruebas específicas**
   ```bash
   pytest tests/test_agents.py
   ```

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas!  
Por favor, abre issues o pull requests siguiendo la estructura del repo y buenas prácticas de Python.

1. Haz fork del repositorio y crea una rama descriptiva.
2. Agrega o modifica tests para tus cambios.
3. Asegúrate de pasar todos los tests antes de solicitar merge.

---

## 📄 Licencia

MIT License.  
Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

¿Dudas o sugerencias? Crea un issue o contacta a los mantenedores.

---