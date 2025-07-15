from ..utils.prompts import BACKEND_AGENT_PROMPT
from ..utils.langchain_helpers import get_llm
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
import json
import re

class BackendAgent:
    prompt = BACKEND_AGENT_PROMPT

    def __init__(self):
        system_template = SystemMessagePromptTemplate.from_template(self.prompt.strip())
        # Updated: instruct strictly JSON only, never markdown or extra text
        human_template = HumanMessagePromptTemplate.from_template(
            "Descripción del ticket:\n{input}\n\n"
            "Devuelve SOLO un JSON ESTRICTAMENTE VÁLIDO con las claves exactas 'codigo' (snippet JS) y 'comentario' (explicación breve en español). Nunca devuelvas otro texto fuera del JSON. Nunca uses Markdown ni comentarios fuera del JSON."
        )
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=ChatPromptTemplate.from_messages([system_template, human_template])
        )

    def _extract_json(self, text):
        match = re.search(r'(\{.*?\})', text, re.DOTALL)
        if match:
            return match.group(1)
        return None

    def run(self, ticket_data: dict) -> dict:
        descripcion = ticket_data.get("descripcion", "")
        try:
            output = self.chain.run(input=descripcion)
            try:
                result = json.loads(output)
            except Exception:
                extracted = self._extract_json(output)
                result = json.loads(extracted) if extracted else {}
            # Must contain both keys
            if "codigo" in result and "comentario" in result:
                return result
            else:
                return {"codigo": "", "comentario": "", "raw_output": output}
        except Exception:
            return {"codigo": "", "comentario": "", "raw_output": output if 'output' in locals() else "ERROR"}