from ..utils.prompts import ORCHESTRATOR_AGENT_PROMPT, IDEA_TO_TICKETS_PROMPT
from ..utils.langchain_helpers import get_llm
import json
from ..utils.linear_api import LinearAPI
from .frontend_agent import FrontendAgent
from .backend_agent import BackendAgent

class OrchestratorAgent:
    prompt = ORCHESTRATOR_AGENT_PROMPT

    def __init__(self):
        pass

    def _extract_json(self, text):
        """Extract the first JSON object/array from the text."""
        import re
        # Allow both array and object
        match = re.search(r'(\[.*?\]|\{.*?\})', text, re.DOTALL)
        if match:
            json_str = match.group(1)
            return json_str
        return None

    def try_json_loads(self, text, max_attempts=2):
        """Try to extract and parse JSON, fallback to extract_json if fails."""
        for i in range(max_attempts):
            try:
                return json.loads(text)
            except Exception:
                extracted = self._extract_json(text)
                if extracted:
                    try:
                        return json.loads(extracted)
                    except Exception:
                        pass
        return None

    def generate_tickets_from_idea(self, idea: str, max_attempts=3):
        llm = get_llm()
        prompt = IDEA_TO_TICKETS_PROMPT.strip() + f"\n\nIDEA:\n{idea.strip()}"
        for attempt in range(max_attempts):
            response_message = llm.invoke(prompt)
            # The response from llm.invoke is an AIMessage object. We need its string content.
            response_content = response_message.content if hasattr(response_message, 'content') else str(response_message)
            
            tickets = self.try_json_loads(response_content)
            if tickets and isinstance(tickets, list):
                # Validate ticket objects
                valid = all(isinstance(t, dict) and {"titulo", "descripcion", "label"} <= set(t.keys()) for t in tickets)
                if valid:
                    return tickets
            # else, try again
        raise ValueError("No valid JSON array of tickets could be parsed from the LLM's response.")

    def run(self, ticket_data: dict) -> dict:
        ticket_id = ticket_data.get("id")
        linear_api = LinearAPI()
       
        team_key = ticket_data.get("team_key")
        team = linear_api.get_team_id_by_key(team_key) if team_key else None
        team_id = team["id"] if team else None

        assignee_email = ticket_data.get("assignee_email")
        assignee = linear_api.get_user_id_by_email(assignee_email) if assignee_email else None
        assignee_id = assignee["id"] if assignee else None

        label_ids = ticket_data.get("labelIds") or ticket_data.get("label_ids")
        # Ensure label_ids is a list of strings or None
        if label_ids:
            if isinstance(label_ids, str):
                label_ids = [label_ids]
            elif isinstance(label_ids, list):
                label_ids = [str(lid) for lid in label_ids if lid]
            else:
                label_ids = None
        print(f"[OrchestratorAgent] Received label_ids: {label_ids}")

        # Always pass label_ids, even if empty
        linear_ticket = None
        if team_id:
            print(f"[OrchestratorAgent.run] Team ID '{team_id}' found for team_key '{team_key}'. Proceeding to create Linear ticket.")
            linear_ticket = linear_api.create_ticket(
                team_id=team_id,
                title=ticket_data.get("titulo", "Ticket sin título"),
                description=ticket_data.get("descripcion", ""),
                assignee_id=assignee_id,
                label_ids=label_ids if label_ids is not None else []
            )
        else:
            print(f"[OrchestratorAgent.run] SKIPPING Linear ticket creation because no Team ID was found for team_key '{team_key}'.")
        
        return {
            "ticket_id": ticket_id,
            "linear_ticket": linear_ticket,
            "linear_team": team,
            "linear_assignee": assignee,
        }

    def process_project(self, idea: str, team_key: str = None):
        linear_api = LinearAPI()
        # a) Generate tickets
        tickets = self.generate_tickets_from_idea(idea)
        # b) Fetch team and members
        team = None
        members = []
        if team_key:
            team = linear_api.get_team_id_by_key(team_key)
            if team and "id" in team:
                team_id = team["id"]
                # get team members (simulate GraphQL as in main.py)
                team_members = linear_api.get_team_members(team_id)
                if team_members:
                    members = team_members
        assignees = []
        if members:
            n = len(members)
            for i, _ in enumerate(tickets):
                assignees.append(members[i % n])
        else:
            assignees = [None] * len(tickets)

        # c) Get labels from Linear, map label name (case-insensitive) → id
        labels = linear_api.get_labels()
        label_map = {l['name'].lower(): l['id'] for l in labels} if labels else {}

        results = []
        for idx, ticket in enumerate(tickets):
            # Assign round-robin
            assignee = assignees[idx]
            ticket_data = {
                "titulo": ticket["titulo"],
                "descripcion": ticket["descripcion"],
                "team_key": team_key,
                "assignee_email": assignee["email"] if assignee else None,
            }
            # Find label id
            label_name = ticket.get("label", "").lower()
            label_id = label_map.get(label_name)
            if label_id:
                ticket_data["labelIds"] = [label_id]
            # d) Create Linear ticket
            linear_ticket_response = self.run(ticket_data)
            linear_ticket_obj = linear_ticket_response.get("linear_ticket", {}).get("issue")

            # e) Call appropriate agent if ticket creation was successful
            agent_output = None
            if linear_ticket_obj:
                label_name = ticket.get("label", "").lower()
                print(f"[Orchestrator] Handing off ticket {linear_ticket_obj.get('identifier')} to {label_name} agent.")
                if label_name == "frontend":
                    agent_output = FrontendAgent().process_ticket(linear_ticket_obj)
                elif label_name == "backend":
                    agent_output = BackendAgent().process_ticket(linear_ticket_obj)
            
            results.append({
                "local_ticket": {**ticket, "label": label_name},
                "linear_ticket": {k: linear_ticket_obj.get(k) for k in ["id", "identifier", "url"]} if linear_ticket_obj else None,
                "agent_output": agent_output
            })
        return results

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