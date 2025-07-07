from utils.prompts import ORCHESTRATOR_AGENT_PROMPT
from utils.langchain_helpers import get_llm
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains.router import LLMRouterChain, RouterOutputParser, MultiPromptChain
import json

class OrchestratorAgent:
    prompt = ORCHESTRATOR_AGENT_PROMPT

    def __init__(self):
        # Backend and frontend destination chains
        self.backend_agent = BackendAgent()
        self.frontend_agent = FrontendAgent()
        self.destinations = {
            "backend": self.backend_agent,
            "frontend": self.frontend_agent,
        }

        # Router chain setup
        system_template = SystemMessagePromptTemplate.from_template(self.prompt.strip())
        human_template = HumanMessagePromptTemplate.from_template(
            "Descripción del ticket:\n{input}\n\n"
            "Responde SOLO con un JSON válido de la forma: { \"destination\": \"backend\" } o { \"destination\": \"frontend\" }."
        )
        router_prompt = ChatPromptTemplate.from_messages([system_template, human_template])
        self.router_chain = LLMRouterChain(
            llm=get_llm(),
            prompt=router_prompt,
            output_parser=RouterOutputParser()
        )

        # MultiPromptChain for unified workflow
        self.multi_chain = MultiPromptChain(
            router_chain=self.router_chain,
            destination_chains={
                "backend": self.run_backend,
                "frontend": self.run_frontend,
            },
            default_chain=self.default_handler
        )

    def run_backend(self, ticket_data):
        return self.backend_agent.run(ticket_data)

    def run_frontend(self, ticket_data):
        return self.frontend_agent.run(ticket_data)
    
    def default_handler(self, ticket_data):
        return {"codigo": "", "comentario": "No se pudo determinar el destino del ticket.", "raw_output": ""}

    def run(self, ticket_data: dict) -> dict:
        ticket_id = ticket_data.get("id")
        # Prepare router input
        router_input = {"input": ticket_data.get("descripcion", "")}
        # Route to correct chain
        try:
            route = self.router_chain.run(**router_input)
            if isinstance(route, dict) and "destination" in route:
                dest = route["destination"]
            elif isinstance(route, str):
                # Try to parse JSON output
                try:
                    parsed = json.loads(route)
                    dest = parsed.get("destination")
                except Exception:
                    dest = None
            else:
                dest = None
        except Exception:
            dest = None

        if dest in self.destinations:
            resultado = self.destinations[dest].run(ticket_data)
            agente_asignado = dest
        else:
            resultado = self.default_handler(ticket_data)
            agente_asignado = None

        return {
            "ticket_id": ticket_id,
            "resultado": resultado,
            "agente_asignado": agente_asignado,
        }

if __name__ == "__main__":
    import sys
    import json as _json
    import argparse

    parser = argparse.ArgumentParser(description="OrchestratorAgent CLI")
    parser.add_argument("--stdin", action="store_true", help="Read ticket JSON from stdin")
    args = parser.parse_args()

    if args.stdin:
        try:
            ticket_data = _json.load(sys.stdin)
            agent = OrchestratorAgent()
            result = agent.run(ticket_data)
            print(_json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    else:
        print("Use --stdin to provide ticket JSON via stdin.", file=sys.stderr)