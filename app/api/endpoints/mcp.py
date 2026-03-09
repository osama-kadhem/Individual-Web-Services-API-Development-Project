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
    Returns tool definitions in a format consumable by AI agents (Model Context Protocol).
    Demonstrates the API's readiness for agentic computing workflows.
    """
    return [
        {
            "name": "get_athlete_readiness",
            "description": (
                "Calculates a readiness score (0–100) for an athlete using the Acute:Chronic "
                "Workload Ratio (ACWR) and sleep/recovery signals. Returns a score, readiness "
                "band (Low/Medium/High), contributing factors, and HATEOAS links."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "athlete_id": {
                        "type": "integer",
                        "description": "The unique ID of the athlete."
                    },
                    "target_date": {
                        "type": "string",
                        "format": "date",
                        "description": "ISO 8601 date for the analysis window (defaults to today)."
                    }
                },
                "required": ["athlete_id"]
            },
            "returns": {
                "readiness_score": "integer (0–100)",
                "readiness_band": "string: 'Low' | 'Medium' | 'High'",
                "signals": "object with acwr, acute_load_7d, chronic_load_28d, sleep_hours, sleep_quality",
                "top_reasons": "array of {reason: string, impact: number}"
            }
        },
        {
            "name": "simulate_future_readiness",
            "description": (
                "Predicts the change in readiness score given a proposed training session and "
                "expected sleep. Returns both the current baseline and the projected score, "
                "plus a natural-language description of the projected change."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "athlete_id": {
                        "type": "integer",
                        "description": "The unique ID of the athlete."
                    },
                    "planned_session_duration": {
                        "type": "number",
                        "description": "Duration of the planned session in minutes (1–600)."
                    },
                    "planned_session_intensity": {
                        "type": "integer",
                        "description": "RPE intensity of the planned session (1–10)."
                    },
                    "expected_sleep_hours": {
                        "type": "number",
                        "description": "Expected sleep duration in hours (0–24)."
                    },
                    "expected_sleep_quality": {
                        "type": "integer",
                        "description": "Expected sleep quality score (1–5)."
                    }
                },
                "required": [
                    "athlete_id",
                    "planned_session_duration",
                    "planned_session_intensity",
                    "expected_sleep_hours",
                    "expected_sleep_quality"
                ]
            },
            "returns": {
                "original_readiness": "ReadinessInsight object (current baseline)",
                "projected_readiness": "ReadinessInsight object (after planned session/sleep)",
                "change_description": "string — natural-language summary of the projected score change"
            }
        },
        {
            "name": "get_training_trends",
            "description": (
                "Retrieves 14-day daily training load history and summary statistics for an athlete. "
                "Useful for identifying overtraining patterns or underloading periods before making "
                "scheduling recommendations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "athlete_id": {
                        "type": "integer",
                        "description": "The unique ID of the athlete."
                    }
                },
                "required": ["athlete_id"]
            },
            "returns": {
                "load_summary": "object with total_14d_load and avg_daily_load",
                "trends": "array of {date: string, load: number} for each of the last 14 days"
            }
        }
    ]
