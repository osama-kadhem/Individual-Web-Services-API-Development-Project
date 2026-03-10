# IronMind Coach API — User Manual

**Version:** 0.6.0  
**Framework:** FastAPI · **Database:** SQLite · **Auth:** API Key (`X-API-KEY`)

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Authentication](#2-authentication)
3. [Dashboard (SPA)](#3-dashboard-spa)
4. [Athlete Management](#4-athlete-management)
5. [Training Sessions](#5-training-sessions)
6. [Sleep Logs](#6-sleep-logs)
7. [Wellness Check-ins](#7-wellness-check-ins)
8. [Readiness Insights](#8-readiness-insights)
9. [What-If Simulator](#9-what-if-simulator)
10. [Training Prescription](#10-training-prescription)
11. [Coach Roster](#11-coach-roster)
12. [Training Trends](#12-training-trends)
13. [MCP Tool Definitions](#13-mcp-tool-definitions)
14. [Error Reference](#14-error-reference)
15. [Running Tests](#15-running-tests)

---

## 1. Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/ironmind-coach-api.git
cd ironmind-coach-api

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r config/requirements.txt

# 4. Start the server
./scripts/run.sh
```

The API will be available at: **http://localhost:8000**

| URL | Purpose |
|---|---|
| `http://localhost:8000/` | SPA Dashboard |
| `http://localhost:8000/docs` | Swagger UI (interactive) |
| `http://localhost:8000/redoc` | ReDoc (reference docs) |
| `http://localhost:8000/health` | Health check |

### Populate with Real Data (Optional)

```bash
# Download the Kaggle dataset
./venv/bin/python3 -c 'import kagglehub; kagglehub.dataset_download("prince7489/athlete-training-and-recovery-tracker-dataset")'

# Run the ETL import script
./venv/bin/python3 scripts/import_dataset.py
```

---

## 2. Authentication

All `/api/v1/` endpoints require an **API key** passed as an HTTP header.

| Header | Value |
|---|---|
| `X-API-KEY` | `ironmind_secret_2026` |

**Missing or wrong key → HTTP 403 Forbidden:**
```json
{
  "error": {
    "status_code": 403,
    "type": "unauthorized",
    "message": "Invalid or missing API Key. Please provide X-API-KEY header."
  }
}
```

**Example using curl:**
```bash
curl -H "X-API-KEY: ironmind_secret_2026" http://localhost:8000/api/v1/athletes/
```

**Public endpoints (no key required):**  
`GET /` · `GET /docs` · `GET /redoc` · `GET /health`

---

## 3. Dashboard (SPA)

Open `http://localhost:8000/` in your browser.

### Login
Enter the API key `ironmind_secret_2026` in the Access Key field and click **Login**. The key is stored in `sessionStorage` for the duration of your browser session.

### Navigation
The sidebar contains 7 sections:

| Section | What it shows |
|---|---|
| Dashboard | Summary stats + recent athletes |
| Athletes | Full athlete table with add/edit/delete |
| Sessions | Training session log |
| Sleep Logs | Daily sleep records |
| Check-ins | Wellness check-in records |
| Insights | Live readiness report + What-If simulator |
| API Console | Embedded Swagger UI |

---

## 4. Athlete Management

Base path: `/api/v1/athletes/`

### Create an Athlete
`POST /api/v1/athletes/`

```json
{
  "name": "Jane Doe",
  "email": "jane@ironmind.com",
  "age": 28
}
```

**Validation rules:**
- `name` — required, 1–120 characters, cannot be blank/whitespace
- `email` — required, must be a valid email address, must be unique
- `age` — optional, integer between **10 and 120**

**Returns:** `201 Created`
```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@ironmind.com",
  "age": 28,
  "created_at": "2026-03-10T22:00:00"
}
```

### List All Athletes
`GET /api/v1/athletes/?skip=0&limit=100`

### Get Single Athlete
`GET /api/v1/athletes/{id}`

### Update an Athlete (Partial)
`PUT /api/v1/athletes/{id}`
```json
{ "name": "Jane Smith" }
```
All fields are optional — only supplied fields are updated.

### Delete an Athlete
`DELETE /api/v1/athletes/{id}` → `204 No Content`

> ⚠️ Deleting an athlete **cascade-deletes** all their sessions, sleep logs, and check-ins.

---

## 5. Training Sessions

Base path: `/api/v1/sessions/`

### Create a Session
`POST /api/v1/sessions/`

```json
{
  "athlete_id": 1,
  "sport": "Running",
  "duration": 60.0,
  "intensity": 7,
  "distance": 12.5,
  "date": "2026-03-10T08:00:00"
}
```

**Validation rules:**
- `sport` — required, 1–60 characters, cannot be blank
- `duration` — required, **> 0** and **≤ 600** minutes
- `intensity` — optional, integer **1–10** (RPE scale)
- `distance` — optional, **0–500** km
- `athlete_id` — must reference an existing athlete (404 if not)

### List Sessions
`GET /api/v1/sessions/?athlete_id=1&sport=Running&skip=0&limit=100`

### Get / Update / Delete
```
GET    /api/v1/sessions/{id}
PUT    /api/v1/sessions/{id}   ← partial update, all fields optional
DELETE /api/v1/sessions/{id}   → 204
```

---

## 6. Sleep Logs

Base path: `/api/v1/sleep-logs/`

### Create a Sleep Log
`POST /api/v1/sleep-logs/`

```json
{
  "athlete_id": 1,
  "sleep_hours": 8.0,
  "sleep_quality": 4,
  "date": "2026-03-10"
}
```

**Validation rules:**
- `sleep_hours` — required, **0–24**
- `sleep_quality` — optional, integer **1–5** (1 = poor, 5 = excellent)
- Only **one log per athlete per date** — duplicate returns **409 Conflict**

### List / Get / Update / Delete
```
GET    /api/v1/sleep-logs/?athlete_id=1
GET    /api/v1/sleep-logs/{id}
PUT    /api/v1/sleep-logs/{id}
DELETE /api/v1/sleep-logs/{id}  → 204
```

---

## 7. Wellness Check-ins

Base path: `/api/v1/checkins/`

### Create a Check-in
`POST /api/v1/checkins/`

```json
{
  "athlete_id": 1,
  "fatigue": 4,
  "stress": 3,
  "mood": 8,
  "soreness": 2,
  "date": "2026-03-10"
}
```

**Validation rules:**
- `fatigue`, `stress`, `mood`, `soreness` — all required, integers **1–10**
- Only **one check-in per athlete per date** — duplicate returns **409 Conflict**

### List / Get / Update / Delete
```
GET    /api/v1/checkins/?athlete_id=1
GET    /api/v1/checkins/{id}
PUT    /api/v1/checkins/{id}
DELETE /api/v1/checkins/{id}  → 204
```

---

## 8. Readiness Insights

`GET /api/v1/athletes/{id}/insights/readiness`

Optional query param: `?target_date=2026-03-10` (defaults to today)

**Response (200 OK):**
```json
{
  "athlete_id": 1,
  "date": "2026-03-10",
  "readiness_score": 87,
  "readiness_band": "High",
  "signals": {
    "acute_load_7d": 2520.0,
    "chronic_load_28d": 2310.0,
    "acwr": 1.1,
    "sleep_hours": 8.5,
    "sleep_quality": 4
  },
  "top_reasons": [
    { "reason": "Optimal training load balance (ACWR 0.8-1.3)", "impact": 15 },
    { "reason": "Excellent sleep duration (>=8h)", "impact": 10 },
    { "reason": "High sleep quality", "impact": 5 }
  ],
  "links": {
    "self": "/api/v1/athletes/1/insights/readiness",
    "sessions": "/api/v1/sessions/?athlete_id=1"
  }
}
```

**Score bands:**
| Band | Score Range | Meaning |
|---|---|---|
| High | 80–100 | Ready for high-intensity training |
| Medium | 50–79 | Train with moderate intensity |
| Low | 0–49 | Rest or very light activity only |

**ACWR thresholds:**

| ACWR | Zone | Score Effect |
|---|---|---|
| 0.8–1.3 | Optimal | +15 pts |
| > 1.5 | Danger | −20 pts |
| < 0.5 | Under-trained | −10 pts |

---

## 9. What-If Simulator

`POST /api/v1/athletes/{id}/whatif/readiness`

**Request body:**
```json
{
  "planned_session_duration": 90,
  "planned_session_intensity": 8,
  "expected_sleep_hours": 9,
  "expected_sleep_quality": 5
}
```

**Response:** Returns both the current baseline and the projected readiness after the planned session and sleep, plus a plain-English change description.

```json
{
  "original_readiness": { "readiness_score": 85, "readiness_band": "High", "..." : "..." },
  "projected_readiness": { "readiness_score": 90, "readiness_band": "High", "...": "..." },
  "change_description": "This plan is projected to improve your readiness score by 5 points compared to your current baseline."
}
```

---

## 10. Training Prescription

`GET /api/v1/athletes/{id}/training-prescription`

Returns a structured weekly training plan based on live ACWR and readiness:

| Tier | Trigger | Sessions/wk | RPE Cap | Load Change |
|---|---|---|---|---|
| **Rest** | Readiness < 40 | 0 | — | −100% |
| **Recover** | ACWR > 1.5 | 2 | 5 | −20% |
| **Maintain** | ACWR 0.8–1.3 | 4 | 8 | 0% |
| **Build** | ACWR < 0.8 | 5 | 9 | +10% |

**Response:**
```json
{
  "athlete_id": 1,
  "date": "2026-03-10",
  "acwr": 1.1,
  "readiness_score": 87,
  "prescription": "Maintain",
  "target_weekly_sessions": 4,
  "max_session_intensity": 8,
  "target_load_change_pct": 0.0,
  "rationale": "ACWR of 1.1 sits in the optimal 0.8–1.3 window. Maintain current training volume. High-intensity sessions permitted up to RPE 8.",
  "links": {
    "self": "/api/v1/athletes/1/training-prescription",
    "readiness": "/api/v1/athletes/1/insights/readiness",
    "trends": "/api/v1/athletes/1/analytics/trends"
  }
}
```

---

## 11. Coach Roster

`GET /api/v1/coaches/roster`

Returns all athletes sorted by readiness score **ascending** (most at-risk first), with squad-level band counts.

```json
{
  "total_athletes": 3,
  "high_readiness": 1,
  "medium_readiness": 1,
  "low_readiness": 1,
  "roster": [
    { "athlete_id": 2, "name": "Tom", "readiness_score": 45, "readiness_band": "Low",    "acwr": 1.8, "prescription": "Recover" },
    { "athlete_id": 3, "name": "Amy", "readiness_score": 72, "readiness_band": "Medium", "acwr": 1.1, "prescription": "Maintain" },
    { "athlete_id": 1, "name": "Jane","readiness_score": 87, "readiness_band": "High",   "acwr": 0.9, "prescription": "Maintain" }
  ],
  "links": { "self": "/api/v1/coaches/roster" }
}
```

---

## 12. Training Trends

`GET /api/v1/athletes/{id}/analytics/trends`

Returns 15 days of daily training load history (0–14 days ago) and summary statistics.

```json
{
  "athlete_id": 1,
  "load_summary": {
    "total_14d_load": 8400.0,
    "avg_daily_load": 600.0
  },
  "trends": [
    { "date": "2026-02-24", "load": 420.0 },
    { "date": "2026-02-25", "load": 600.0 },
    "..."
  ],
  "links": {
    "self": "/api/v1/athletes/1/analytics/trends",
    "readiness": "/api/v1/athletes/1/insights/readiness"
  }
}
```

> **Load formula:** `load = duration (minutes) × RPE (1–10)` per session, summed daily.

---

## 13. MCP Tool Definitions

`GET /api/v1/mcp/tools`

Returns AI-consumable tool definitions (Model Context Protocol format) for the three core analytics functions: `get_athlete_readiness`, `simulate_future_readiness`, and `get_training_trends`. Use this endpoint to integrate IronMind Coach into LLM agent workflows.

---

## 14. Error Reference

All errors use a consistent JSON envelope:

```json
{
  "error": {
    "status_code": 422,
    "type": "validation_error",
    "message": "Input validation failed",
    "details": [
      { "field": "age", "message": "Input should be less than or equal to 120" }
    ]
  }
}
```

| Status | Type | Cause |
|---|---|---|
| 400 | `bad_request` | Duplicate email on athlete create |
| 403 | `unauthorized` | Missing or wrong `X-API-KEY` |
| 404 | `not_found` | Resource ID does not exist |
| 409 | `conflict` | Duplicate sleep log or check-in for same date |
| 422 | `validation_error` | Invalid field value (out of range, wrong type, blank) |
| 429 | `too_many_requests` | Rate limit exceeded (120/min per IP) |
| 500 | `internal_error` | Unexpected server error |

---

## 15. Running Tests

```bash
# Run the full test suite
./venv/bin/pytest tests/ -v
```

Expected output: **40 passed, 0 failed** in ~1 second.

The test suite covers:
- Error envelope format (404, 422, 400)
- Full CRUD lifecycle for all 4 entities
- Input validation edge cases (age bounds, blank fields, out-of-range values)
- Duplicate date 409 enforcement
- ACWR readiness algorithm correctness
- HATEOAS link presence
- What-If simulator structure
- Training prescription tier logic
- Coach roster sorting and band counts
- MCP endpoint structure
