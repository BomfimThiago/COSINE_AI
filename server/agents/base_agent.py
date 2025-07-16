import json
from abc import ABC, abstractmethod

from ..utils.langchain_helpers import get_llm
from ..utils.linear_api import LinearAPI
from ..utils.github_api import GitHubAPI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

ANALYZE_TICKET_PROMPT = """
Analyze the provided software ticket description to determine if it's ready for development.
A ticket is sufficient if it has a clear goal, specific requirements, and no obvious ambiguities.

Respond with only "true" if the ticket is sufficient, or "false" if it is not.

Ticket Description:
---
{description}
---
"""

class BaseAgent(ABC):
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.linear_api = LinearAPI()
        self.github_api = GitHubAPI()
        self.llm = get_llm()

        # LLM Chain for analyzing ticket sufficiency
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(ANALYZE_TICKET_PROMPT)
        )

    def _analyze_ticket_sufficiency(self, ticket: dict) -> dict:
        """
        Uses an LLM to analyze the ticket description.
        Returns a dictionary with 'sufficient' (bool) and 'comment' (str).
        """
        print(f"[{self.agent_type}] Analyzing ticket: {ticket.get('identifier')}")
        description = ticket.get("description", "")
        
        try:
            analysis_result = self.analysis_chain.run(description=description).strip().lower()
            print(f"[{self.agent_type}] Analysis result: {analysis_result}")

            is_sufficient = analysis_result == "true"
            
            if is_sufficient:
                return {"sufficient": True, "comment": "This ticket is clear and ready for development. I will start working on it."}
            else:
                # If not sufficient, generate a clarifying question
                question_prompt = f"The following ticket is not clear enough to start working on it. Please formulate a concise question to the user asking for the specific information that is missing. Ticket description: {description}"
                clarifying_question = self.llm.predict(question_prompt)
                return {"sufficient": False, "comment": clarifying_question}

        except Exception as e:
            print(f"[{self.agent_type}] Error analyzing ticket {ticket.get('identifier')}: {e}")
            # Fallback comment if analysis fails
            return {"sufficient": False, "comment": "I encountered an error while analyzing this ticket. Could you please check if the description is clear and formatted correctly?"}

    @abstractmethod
    def _generate_code_and_create_pr(self, ticket: dict):
        """
        Abstract method for agent-specific logic to generate code and create a PR.
        This must be implemented by subclasses.
        """
        pass

    def process_ticket(self, ticket: dict):
        """
        Main entry point to process a single ticket. It analyzes the ticket,
        and either posts a comment asking for clarification or proceeds
        to generate code and create a pull request.
        """
        analysis = self._analyze_ticket_sufficiency(ticket)

        if not analysis.get("sufficient"):
            comment = analysis.get("comment", "This ticket requires more information.")
            print(f"[{self.agent_type}] Posting clarifying comment on {ticket.get('identifier')}")
            self.linear_api.add_comment(ticket['id'], comment)
            return {"status": "commented", "ticket": ticket.get('identifier'), "comment": comment}
        
        # If the ticket is sufficient, generate code and create a PR
        return self._generate_code_and_create_pr(ticket) 