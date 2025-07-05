from utils.prompts import BACKEND_AGENT_PROMPT

class BackendAgent:
    prompt = BACKEND_AGENT_PROMPT

    def run(self, ticket_data: dict) -> dict:
        descripcion = ticket_data.get("descripcion", "")
        # Simulación de código Node.js y explicación
        codigo = (
            "```js\n"
            "// " + descripcion + "\n"
            "function handler(req, res) {\n"
            "    res.json({ mensaje: 'Función backend simulada!' });\n"
            "}\n"
            "module.exports = handler;\n"
            "```"
        )
        comentario = "Función handler de Node.js simulada que responde con un JSON."
        return {
            "codigo": codigo,
            "comentario": comentario
        }