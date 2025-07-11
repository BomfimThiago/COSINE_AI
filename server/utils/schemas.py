from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel, ValidationError
import json

class FrontendAgentOutput(BaseModel):
    archivo: Optional[str] = None
    codigo: str  # JSX / TSX snippet
    comentario: str  # brief explanation in Spanish
    dependencias: Optional[List[str]] = None
    test: Optional[str] = None
    css: Optional[str] = None

    @classmethod
    def validate_output(cls, raw: Any) -> "FrontendAgentOutput":
        """
        Validates and parses raw output into FrontendAgentOutput.
        Accepts a dict or JSON-serialisable str. Raises ValueError if invalid.
        """
        # Accept dict or JSON-serializable string
        if isinstance(raw, str):
            try:
                data = json.loads(raw)
            except Exception as e:
                raise ValueError(f"Invalid JSON: {e}")
        elif isinstance(raw, dict):
            data = raw
        else:
            raise ValueError("Input must be a dict or JSON string.")

        # Ensure required keys
        required = ["codigo", "comentario"]
        if not all(k in data and isinstance(data[k], str) and data[k].strip() for k in required):
            raise ValueError("Missing required fields: 'codigo' and/or 'comentario'.")

        try:
            return cls(**data)
        except ValidationError as ve:
            raise ValueError(f"Validation error: {ve}")