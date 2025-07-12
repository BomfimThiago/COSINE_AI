from typing import List

class TicketGenerator:
    """
    Service for generating project tickets from a project idea.
    In Phase 2, this will be replaced with a call to the LLM.
    """
    def generate_tickets(self, idea: str) -> List[dict]:
        """
        Generate a list of mock tickets from a project idea.
        In the future, this will call an LLM to generate the tickets.

        Args:
            idea (str): The project idea description.
        Returns:
            List[dict]: A list of ticket dicts.
        """
        return [
            {
                "title": "Crear la página principal",
                "description": "Desarrollar la interfaz de usuario para la página principal del proyecto.",
                "label": "frontend",
                "assignee": None,
                "linear_ticket": None,
            },
            {
                "title": "Configurar la base de datos",
                "description": "Implementar la configuración inicial de la base de datos y modelos.",
                "label": "backend",
                "assignee": None,
                "linear_ticket": None,
            }
        ]