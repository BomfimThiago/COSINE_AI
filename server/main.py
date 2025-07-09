from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from .agents.orchestrator_agent import OrchestratorAgent
from .utils.linear_api import LinearAPI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TicketRequest(BaseModel):
    descripcion: str
    team_key: Optional[str] = None
    assignee_email: Optional[str] = None
    titulo: Optional[str] = None
    id: Optional[str] = None
    labelIds: Optional[List[str]] = None

@app.post("/create_ticket")
def create_ticket(ticket: TicketRequest):
    try:
        print(f"[main.py] Received ticket data: {ticket.dict()}")
        agent = OrchestratorAgent()
        result = agent.run(ticket.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/linear/teams")
def get_linear_teams():
    api = LinearAPI()
    # Fetch all teams
    query = """
    query {
      teams {
        nodes {
          id
          name
          key
        }
      }
    }
    """
    response = api._LinearAPI__raw_query(query)
    return response.get("data", {}).get("teams", {}).get("nodes", [])

@app.get("/linear/team_members")
def get_linear_team_members(team_key: str = Query(...)):
    api = LinearAPI()
    # Fetch all teams and find the one with the matching key
    query_teams = """
    query {
      teams {
        nodes {
          id
          name
          key
        }
      }
    }
    """
    teams_response = api._LinearAPI__raw_query(query_teams)
    teams = teams_response.get("data", {}).get("teams", {}).get("nodes", [])
    team = next((t for t in teams if t["key"] == team_key), None)
    if not team:
        return []
    # Fetch members of the team
    query_members = f"""
    query {{
      team(id: \"{team['id']}\") {{
        members {{
          nodes {{
            id
            name
            email
          }}
        }}
      }}
    }}
    """
    members_response = api._LinearAPI__raw_query(query_members)
    return members_response.get("data", {}).get("team", {}).get("members", {}).get("nodes", [])

@app.get("/linear/labels")
def get_linear_labels():
    api = LinearAPI()
    return api.get_labels()
