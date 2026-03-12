# IronMind Coach API — User Manual

**Version:** 0.6.0  
**Framework:** FastAPI · **Database:** SQLite · **Auth:** Hybrid (JWT + API Key)

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
git clone https://github.com/osama-kadhem/Individual-Web-Services-API-Development-Project.git
cd Individual-Web-Services-API-Development-Project

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r config/requirements.txt

# 4. Start the server
PYTHONPATH=. python scripts/init_db.py
PYTHONPATH=. python scripts/import_dataset.py
./venv/bin/uvicorn app.main:app --reload
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

The API utilizes a dual-layered authentication system.

### Option A: Master Access Key
Pass the following header for admin or script-based access:
- **Header**: `X-API-KEY`
- **Value**: `ironmind_secret_2026`

### Option B: Professional JWT (Stateless Bearer)
Full OAuth2 flow supported for production environments.
1. **Login**: `POST /api/v1/auth/login`
2. **Usage**: Pass the token in the `Authorization: Bearer <token>` header.

**Public endpoints (no key required):**  
`POST /api/v1/athletes/` (Registration) · `GET /docs` · `GET /redoc` · `GET /health`

---

## 3. Dashboard (SPA)

Open `http://localhost:8000/` in your browser.

### Login
Enter the API key `ironmind_secret_2026` in the Access Key field to enter the dashboard.

---

## 4. Athlete Management

Base path: `/api/v1/athletes/`

### Create an Athlete
`POST /api/v1/athletes/`

**Validation rules:**
- `age`: Optional, integer between **10 and 120**.
- `email`: Required, must be a valid and unique email address.

---

## 5. Training Sessions

Base path: `/api/v1/sessions/`

### Create a Session
`POST /api/v1/sessions/`

**Validation rules:**
- `duration`: Required, between **1.0 and 600.0** minutes.
- `intensity`: Optional, RPE scale **1–10**.

---

## 6. Sleep Logs

Base path: `/api/v1/sleep-logs/`

**Validation rules:**
- `sleep_hours`: Required, between **0.0 and 24.0**.
- Only **one log per athlete per date** (409 Conflict on duplication).

---

## 7. Wellness Check-ins

Base path: `/api/v1/checkins/`

**Validation rules:**
- `fatigue`, `stress`, `mood`, `soreness`: Required, integers **1–10**.

---

## 8. Readiness Insights

`GET /api/v1/athletes/{id}/insights/readiness`

Calculates a 0–100 score using the **Acute:Chronic Workload Ratio (ACWR)** and **Live Weather**.

### Science Factors:
| Factor | Trigger | Impact |
|---|---|---|
| **ACWR** | 0.8–1.3 (Optimal) | +15 pts |
| **ACWR** | > 1.5 (Danger) | -20 pts |
| **Temperature** | > 30°C | -20 pts (Heat Penalty) |
| **Humidity** | > 80% | -10 pts |

---

## 9. What-If Simulator

`POST /api/v1/athletes/{id}/whatif/readiness`

Allows athletes to project their readiness score by inputting a planned duration, intensity, and expected sleep duration. Returns a `projected_readiness` score.

---

## 10. Training Prescription

`GET /api/v1/athletes/{id}/training-prescription`

Automatically generates a weekly goal (**Rest / Recover / Maintain / Build**) based on the live ACWR zone.

---

## 11. Coach Roster

`GET /api/v1/coaches/roster`

**Squad Overview**: Returns all athletes sorted by readiness score ascending (most at-risk first).

---

## 12. Training Trends

`GET /api/v1/athletes/{id}/analytics/trends`

Returns a 14-day training load history. Used to render the **Interactive Performance Charts**.

---

## 13. MCP Tool Definitions

`GET /api/v1/mcp/tools`

Returns Model Context Protocol (MCP) definitions, allowing AI agents to interact with the API analytics endpoints autonomously.

---

## 14. Error Reference

Standard JSON Structure:
```json
{
  "error": {
    "status_code": 404,
    "type": "not_found",
    "message": "Athlete not found"
  }
}
```

---

## 15. Running Tests

```bash
./venv/bin/pytest tests/ -v
```
Expect **40 passing tests** covering security, logic, and CRUD operations.
