from __future__ import annotations
import pytest

from server.utils import clarity_checker

def test_clear_ticket():
    ticket = {
        "title": "Nueva API para login de usuarios",
        "description": "Implementar endpoint RESTful para permitir login usando JWT. AC: Usuario puede iniciar sesión con email y contraseña y recibe un token válido.",
        "labels": {"nodes": [{"id": "lbl1", "name": "backend"}]},
    }
    is_clear, missing = clarity_checker.analyze(ticket)
    assert is_clear
    assert missing == []

def test_missing_title():
    ticket = {
        "title": "",
        "description": "La descripción es suficientemente larga. AC: Criterio presente.",
        "labels": {"nodes": [{"id": "lbl1", "name": "backend"}]},
    }
    is_clear, missing = clarity_checker.analyze(ticket)
    assert not is_clear
    assert "Falta el título." in missing

def test_short_description():
    ticket = {
        "title": "Algo",
        "description": "Muy corta.",
        "labels": {"nodes": [{"id": "lbl1", "name": "backend"}]},
    }
    is_clear, missing = clarity_checker.analyze(ticket)
    assert not is_clear
    assert any("demasiado corta" in m for m in missing)

def test_missing_label_and_backend():
    ticket = {
        "title": "Backend stuff",
        "description": "Descripción suficientemente larga. AC: presente.",
        "labels": {"nodes": []},
    }
    is_clear, missing = clarity_checker.analyze(ticket)
    assert not is_clear
    assert any("etiqueta" in m for m in missing)

    # Without backend keyword
    ticket2 = {
        "title": "Backend stuff",
        "description": "Descripción suficientemente larga. AC: presente.",
        "labels": {"nodes": [{"id": "1", "name": "infra"}]},
    }
    is_clear2, missing2 = clarity_checker.analyze(ticket2)
    assert not is_clear2
    assert any("backend" in m.lower() for m in missing2)

def test_missing_acceptance_criteria():
    ticket = {
        "title": "API",
        "description": "Descripción suficientemente larga pero no contiene criterio.",
        "labels": {"nodes": [{"id": "lbl1", "name": "backend"}]},
    }
    is_clear, missing = clarity_checker.analyze(ticket)
    assert not is_clear
    assert any("criterio de aceptación" in m.lower() for m in missing)