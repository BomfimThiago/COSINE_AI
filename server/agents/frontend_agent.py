from ..utils.prompts import FRONTEND_AGENT_PROMPT
from ..utils.langchain_helpers import get_llm
from ..utils import FrontendAgentOutput
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
import json
from typing import Any

class FrontendAgent:
    prompt = FRONTEND_AGENT_PROMPT

    def __init__(self):
        system_template = SystemMessagePromptTemplate.from_template(self.prompt.strip())
        # Updated human template to reference contract and JSON fields
        human_template = HumanMessagePromptTemplate.from_template(
            "Descripción del ticket:\n{input}\n\n"
            "Devuelve SOLO un JSON ESTRICTAMENTE válido y con las claves exactas: 'archivo', 'codigo', 'comentario', 'dependencias', 'test', 'css' (los opcionales en null si no aplica)."
            " NUNCA incluyas ningún texto extra fuera del JSON."
        )
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=ChatPromptTemplate.from_messages([system_template, human_template])
        )

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Strips markdown/code fences and returns the raw JSON content.
        """
        text = text.strip()
        # Remove markdown code fences if present
        if text.startswith("```") and text.endswith("```"):
            text = text.strip("` \n")
            # Optionally remove a language hint like ```json
            first_newline = text.find('\n')
            if first_newline != -1 and text[:first_newline].lower().startswith("json"):
                text = text[first_newline+1:]
        # Remove leading/trailing backticks or whitespace
        return text.strip("` \n")

    @staticmethod
    def try_json_loads(text: str) -> Any:
        """
        Attempts to load JSON from string, raises ValueError if fails.
        """
        try:
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"Invalid JSON: {e}")

    def run(self, ticket_data: dict) -> dict:
        descripcion = ticket_data.get("descripcion", "")
        last_raw = None
        for attempt in range(3):
            try:
                output = self.chain.run(input=descripcion)
                last_raw = output
                json_str = self._extract_json(output)
                result = FrontendAgentOutput.validate_output(json_str)
                return dict(result)
            except Exception:
                continue
        # If all attempts fail
        return {
            "codigo": "",
            "comentario": "",
            "error": "INVALID_OUTPUT",
            "raw_output": last_raw
        }