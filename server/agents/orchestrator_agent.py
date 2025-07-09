from ..utils.prompts import ORCHESTRATOR_AGENT_PROMPT
from ..utils.langchain_helpers import get_llm
import json
from ..utils.linear_api import LinearAPI

class OrchestratorAgent:
    prompt = ORCHESTRATOR_AGENT_PROMPT

    def __init__(self):
        pass

    def run(self, ticket_data: dict) -> dict:
        ticket_id = ticket_data.get("id")
        linear_api = LinearAPI()
       
        team_key = ticket_data.get("team_key")
        team = linear_api.get_team_id_by_key(team_key) if team_key else None
        team_id = team["id"] if team else None

        assignee_email = ticket_data.get("assignee_email")
        assignee = linear_api.get_user_id_by_email(assignee_email) if assignee_email else None
        assignee_id = assignee["id"] if assignee else None

        linear_ticket = None
        if team_id:
            linear_ticket = linear_api.create_ticket(
                team_id=team_id,
                title=ticket_data.get("titulo", "Ticket sin título"),
                description=ticket_data.get("descripcion", ""),
                assignee_id=assignee_id
            )
        return {
            "ticket_id": ticket_id,
            "linear_ticket": linear_ticket,
            "linear_team": team,
            "linear_assignee": assignee,
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