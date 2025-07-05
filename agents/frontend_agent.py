from utils.prompts import FRONTEND_AGENT_PROMPT

class FrontendAgent:
    prompt = FRONTEND_AGENT_PROMPT

    def run(self, ticket_data: dict) -> dict:
        descripcion = ticket_data.get("descripcion", "")
        # Simulación de código JSX y comentario
        codigo = (
            "```jsx\n"
            "function DemoComponent() {\n"
            f"    // {descripcion}\n"
            "    return <div>Hola, soy un componente simulado!</div>;\n"
            "}\n"
            "```"
        )
        comentario = "Componente React funcional basado en la descripción del ticket."
        return {
            "codigo": codigo,
            "comentario": comentario
        }