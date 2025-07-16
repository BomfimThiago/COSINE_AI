from __future__ import annotations

import json
from .base_agent import BaseAgent
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

BACKEND_CODE_GEN_PROMPT = """
You are a senior backend developer specializing in Python and FastAPI.
Based on the following ticket, generate a single file's content to solve the task.
The output must be a JSON object with two keys:
1. "file_path": A string with the full proposed file path (e.g., "server/api/auth.py").
2. "file_content": A string containing the complete, well-formatted code for the file.

Ticket Description:
---
{description}
---
"""

class BackendAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_type="BackendAgent")

        # LLM Chain for generating backend code
        self.code_gen_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(BACKEND_CODE_GEN_PROMPT)
        )

    def _generate_code_and_create_pr(self, ticket: dict):
        print(f"[{self.agent_type}] Generating code for ticket: {ticket.get('identifier')}")
        description = ticket.get("description", "")

        try:
            # Generate code and file path
            generation_str = self.code_gen_chain.run(description=description)
            # The model might return a string that is not perfect JSON, so we clean it
            clean_json_str = generation_str[generation_str.find('{'):generation_str.rfind('}')+1]
            generation = json.loads(clean_json_str)
            
            file_path = generation.get("file_path")
            file_content = generation.get("file_content")

            if not file_path or not file_content:
                raise ValueError("LLM failed to provide a valid file_path or file_content.")

            print(f"[{self.agent_type}] Generated code for file: {file_path}")

            # Create the Pull Request
            pr_result = self.github_api.create_pr(
                ticket_id=ticket.get("identifier"),
                ticket_title=ticket.get("title"),
                file_path=file_path,
                file_content=file_content
            )

            # If PR creation is successful, post a comment on the Linear ticket
            if pr_result.get("success"):
                comment_body = f"I've opened a pull request to address this ticket: {pr_result.get('pr_url')}"
                self.linear_api.add_comment(ticket['id'], comment_body)
                return {"status": "pr_created", "ticket": ticket.get('identifier'), "pr_url": pr_result.get('pr_url')}
            else:
                raise Exception(f"Failed to create PR: {pr_result.get('error')}")

        except Exception as e:
            error_message = f"An error occurred during code generation or PR creation for {ticket.get('identifier')}: {e}"
            print(f"[{self.agent_type}] {error_message}")
            # Post a comment on Linear that something went wrong
            self.linear_api.add_comment(ticket['id'], f"I tried to work on this ticket but encountered an error and could not create a pull request. Please review the details.\n\nError: {e}")
            return {"status": "error", "ticket": ticket.get('identifier'), "error": str(e)}