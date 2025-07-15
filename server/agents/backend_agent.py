from __future__ import annotations

from ..utils.prompts import BACKEND_AGENT_PROMPT
from ..utils.langchain_helpers import get_llm
from ..utils.ticket_loader import TicketLoader
from ..utils import clarity_checker

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
import json
import re
from typing import Any

class BackendAgent:
    prompt = BACKEND_AGENT_PROMPT

    def __init__(self):
        system_template = SystemMessagePromptTemplate.from_template(self.prompt.strip())
        human_template = HumanMessagePromptTemplate.from_template(
            "Descripción del ticket:\n{input}\n\n"
            "Devuelve SOLO un JSON ESTRICTAMENTE VÁLIDO con las claves exactas 'codigo' (snippet JS) y 'comentario' (explicación breve en español). Nunca devuelvas otro texto fuera del JSON. Nunca uses Markdown ni comentarios fuera del JSON."
        )
        self.chain = LLMChain(
            llm=get_llm(),
            prompt=ChatPromptTemplate.from_messages([system_template, human_template])
        )

    def _extract_json(self, text: str) -> str | None:
        match = re.search(r'(\{.*?\})', text, re.DOTALL)
        if match:
            return match.group(1)
        return None

    def load_and_check_ticket(self, ticket_identifier_or_data: dict | str) -> dict:
        """
        Loads ticket (if id given), checks clarity, returns dict:
        {
          "ticket_id": ...,
          "is_clear": bool,
          "missing": [str, ...]
        }
        """
        if isinstance(ticket_identifier_or_data, dict):
            ticket_data = ticket_identifier_or_data.copy()
            ticket_id = ticket_data.get("id") or ticket_data.get("identifier")
            # If 'id' is present and not an ephemeral/temporary ticket, reload from Linear
            if ticket_id:
                fresh = TicketLoader.load(ticket_id)
                if fresh:
                    ticket_data = fresh
        else:
            ticket_id = str(ticket_identifier_or_data)
            ticket_data = TicketLoader.load(ticket_id)
        ticket_id = ticket_data.get("id") if ticket_data else None
        is_clear, missing = clarity_checker.analyze(ticket_data or {})
        return {
            "ticket_id": ticket_id,
            "is_clear": is_clear,
            "missing": missing
        }

    def run(self, ticket_data: dict) -> dict:
        # Step 1: clarity check
        clarity_result = self.load_and_check_ticket(ticket_data)
        if not clarity_result["is_clear"]:
            return clarity_result
        # Step 2: continue with current LLM generation
        descripcion = ticket_data.get("descripcion", "") or ticket_data.get("description", "")
        try:
            output = self.chain.run(input=descripcion)
            try:
                result = json.loads(output)
            except Exception:
                extracted = self._extract_json(output)
                result = json.loads(extracted) if extracted else {}
            if "codigo" in result and "comentario" in result:
                return result
            else:
                return {"codigo": "", "comentario": "", "raw_output": output}
        except Exception:
            return {"codigo": "", "comentario": "", "raw_output": output if 'output' in locals() else "ERROR"}