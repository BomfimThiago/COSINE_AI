from __future__ import annotations
from typing import Any
from .linear_api import LinearAPI

class TicketLoader:
    @staticmethod
    def load(ticket_id: str) -> dict | None:
        """
        Loads a ticket by id using LinearAPI.
        """
        api = LinearAPI()
        return api.get_ticket(ticket_id)