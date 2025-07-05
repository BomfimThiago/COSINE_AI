from utils.prompts import ORCHESTRATOR_AGENT_PROMPT

class OrchestratorAgent:
    prompt = ORCHESTRATOR_AGENT_PROMPT

    def run(self, ticket_data: dict) -> dict:
        tipo = ticket_data.get("tipo")
        ticket_id = ticket_data.get("id")
        if tipo == "frontend":
            from agents.frontend_agent import FrontendAgent
            resultado = FrontendAgent().run(ticket_data)
            agente_asignado = "frontend"
        elif tipo == "backend":
            from agents.backend_agent import BackendAgent
            resultado = BackendAgent().run(ticket_data)
            agente_asignado = "backend"
        else:
            # Por ahora no manejar errores ni tareas mixtas
            resultado = None
            agente_asignado = None
        return {
            "ticket_id": ticket_id,
            "resultado": resultado,
            "agente_asignado": agente_asignado,
        }