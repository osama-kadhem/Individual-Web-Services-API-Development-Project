from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get(
    "/tools",
    summary="MCP Tool Definitions",
    description="Exposes the API's core analytics as AI-consumable tools (Model Context Protocol).",
    tags=["System"]
)
def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Returns tool definitions in a format consumable by AI agents.
    Demonstrates the API's readiness for the future of agentic computing.
    """
    return [
        {
            "name": "get_athlete_readiness",
            "description": "Calculates readiness score based on ACWR and recovery metrics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "athlete_id": {"type": "integer", "description": "The unique ID of the athlete."},
                    "target_date": {"type": "string", "format": "date", "description": "ISO date for analysis."}
                },
                "required": ["athlete_id"]
            }
        },
        {
            "name": "simulate_future_readiness",
            "description": "Predicts future readiness score based on a proposed training and sleep plan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "athlete_id": {"type": "integer"},
                    "planned_duration": {"type": "number"},
                    "planned_intensity": {"type": "number"},
                    "expected_sleep": {"type": "number"}
                },
                "required": ["athlete_id", "planned_duration", "planned_intensity", "expected_sleep"]
            }
        }
    ]
