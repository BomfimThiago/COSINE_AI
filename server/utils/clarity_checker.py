from __future__ import annotations
from typing import Any

def analyze(ticket: dict) -> tuple[bool, list[str]]:
    """
    Analiza la claridad del ticket según reglas predefinidas.
    Devuelve (es_claro: bool, faltantes: list[str])
    """
    missing: list[str] = []

    # 1. Título no vacío
    title = ticket.get("title") or ticket.get("titulo") or ""
    if not isinstance(title, str) or not title.strip():
        missing.append("Falta el título.")

    # 2. Descripción ≥ 30 caracteres
    description = (
        ticket.get("description")
        or ticket.get("descripcion")
        or ticket.get("body")
        or ""
    )
    if not isinstance(description, str) or len(description.strip()) < 30:
        missing.append("La descripción es demasiado corta (mínimo 30 caracteres).")

    # 3. Al menos una etiqueta y debe incluir 'backend'
    labels = []
    if "labels" in ticket and isinstance(ticket["labels"], dict) and "nodes" in ticket["labels"]:
        labels = [lbl.get("name", "") for lbl in ticket["labels"]["nodes"]]
    elif "labels" in ticket and isinstance(ticket["labels"], list):
        labels = ticket["labels"]
    elif "etiquetas" in ticket:
        labels = ticket["etiquetas"]
    labels = [str(lbl).lower() for lbl in labels if lbl]

    if not labels:
        missing.append("Debe tener al menos una etiqueta (label).")
    elif not any("backend" in lbl for lbl in labels):
        missing.append("Debe tener una etiqueta que contenga la palabra 'backend'.")

    # 4. Criterio de aceptación: descripción debe contener "AC:"
    if not ("ac:" in description.lower()):
        missing.append("Falta el criterio de aceptación (AC).")

    is_clear = len(missing) == 0
    return is_clear, missing