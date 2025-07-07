from utils.prompts import FRONTEND_AGENT_PROMPT
from utils.langchain_helpers import get_llm
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
import json

class FrontendAgent:
    prompt = FRONTEND_AGENT_PROMPT

    def __init__(self):
        system_template = SystemMessagePromptTemplate.from_template(self.prompt.strip())
        human_template = HumanMessagePromptTemplate.from_template(
            "Descripción del ticket:\n{input}\n\n"
            "Devuelve SOLO un JSON válido con las claves 'codigo' (snippet JSX) y 'comentario' (explicación breve en español)."
        )
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=ChatPromptTemplate.from_messages([system_template, human_template])
        )
    
    def run(self, ticket_data: dict) -> dict:
        descripcion = ticket_data.get("descripcion", "")
        try:
            output = self.chain.run(input=descripcion)
            result = json.loads(output)
            if "codigo" in result and "comentario" in result:
                return result
            else:
                return {"codigo": "", "comentario": "", "raw_output": output}
        except Exception:
            return {"codigo": "", "comentario": "", "raw_output": output if 'output' in locals() else "ERROR"}