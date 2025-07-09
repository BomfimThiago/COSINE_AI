from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .agents.orchestrator_agent import OrchestratorAgent

app = FastAPI()

class TicketRequest(BaseModel):
    descripcion: str
    team_key: Optional[str] = None
    assignee_email: Optional[str] = None
    titulo: Optional[str] = None
    id: Optional[str] = None

@app.post("/create_ticket")
def create_ticket(ticket: TicketRequest):
    try:
        agent = OrchestratorAgent()
        result = agent.run(ticket.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
