# IronMind Coach API

> A high-performance REST API for triathlon training management, recovery tracking, and evidence-based readiness analytics — powered by FastAPI and the Acute:Chronic Workload Ratio (ACWR).

---

## 🌐 Live Deployment

| | Link |
|---|---|
| **Live App (Dashboard)** | [https://osamakadhem.pythonanywhere.com](https://osamakadhem.pythonanywhere.com) |
| **Live API Docs (Swagger)** | [https://osamakadhem.pythonanywhere.com/docs](https://osamakadhem.pythonanywhere.com/docs) |
| **Live API Reference (ReDoc)** | [https://osamakadhem.pythonanywhere.com/redoc](https://osamakadhem.pythonanywhere.com/redoc) |
| **Health Check** | [https://osamakadhem.pythonanywhere.com/health](https://osamakadhem.pythonanywhere.com/health) |

**Access Key (API Key):** `ironmind_secret_2026`
- Enter in the Dashboard login screen
- Or pass as HTTP header: `X-API-KEY: ironmind_secret_2026`
- Or click **Authorize** in Swagger and paste the key

---

## 📄 Submitted Materials

| Deliverable | Location |
|---|---|
| **GitHub Repository** | [https://github.com/osama-kadhem/Individual-Web-Services-API-Development-Project](https://github.com/osama-kadhem/Individual-Web-Services-API-Development-Project) |
| **API Documentation (PDF)** | `docs/api_documentation.pdf` |
| **User Manual** | [docs/USER_MANUAL.md](docs/USER_MANUAL.md) |
| **Technical Report** | Submitted via Minerva |
| **Presentation Slides** | Submitted via Minerva |

---

## 🚀 Features

- **Athlete Management** — Full CRUD lifecycle with unique email validation and age bounds (10–120)
- **Training Sessions** — Log sessions across Swim, Bike, Run with RPE (1–10) and duration tracking
- **Recovery Tracking** — Daily sleep logs (0–24h) and wellness check-ins (fatigue, stress, mood, soreness 1–10)
- **Readiness Insights** — Real-time ACWR-based readiness scores (0–100) with impact reasons and HATEOAS links
- **What-If Simulator** — Projects future readiness from planned session + sleep parameters
- **Training Prescription** — Evidence-based weekly plan (Rest / Recover / Maintain / Build) derived from live ACWR
- **Coach Roster** — Squad-level overview sorted by readiness score, with band-level counts
- **Training Trends** — 14-day load history and averages
- **MCP Endpoint** — AI agent-compatible tool definitions (Model Context Protocol)
- **Rate Limiting** — 120 requests/minute per IP via `slowapi`
- **API Key Auth** — Global `X-API-KEY` guard on all `/api/v1/` routes
- **SPA Dashboard** — Login-gated single-page app at `/`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.128 |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Database | SQLite |
| Server | Uvicorn |
| Rate Limiting | slowapi |
| Testing | Pytest (40 integration tests) |
| Hosting | PythonAnywhere |

---

## 📁 Project Structure

```
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── athletes.py          # Athlete CRUD
│   │   │   ├── sessions.py          # Training session CRUD
│   │   │   ├── sleep_logs.py        # Sleep log CRUD
│   │   │   ├── checkins.py          # Check-in CRUD
│   │   │   ├── insights.py          # Readiness, trends, what-if, prescription
│   │   │   ├── coaches.py           # Coach roster
│   │   │   └── mcp.py               # AI tool definitions
│   │   └── v1/api.py                # Central router (auth applied globally)
│   ├── core/
│   │   ├── config.py                # pydantic-settings (.env loader)
│   │   ├── auth.py                  # X-API-KEY dependency
│   │   └── errors.py                # Standardised JSON error envelope
│   ├── crud/                        # Database CRUD operations
│   ├── db/session.py                # Engine, SessionLocal, get_db
│   ├── models/models.py             # 4 SQLAlchemy ORM tables
│   ├── schemas/                     # Pydantic request/response schemas
│   ├── services/insights.py         # ALL business logic (ACWR engine)
│   └── static/                      # SPA dashboard (index.html, app.js, CSS)
├── config/requirements.txt          # Pinned dependencies
├── data/ironmind.db                 # SQLite database
├── docs/
│   ├── USER_MANUAL.md               # Full user manual
│   └── api_documentation.pdf        # API docs PDF
├── scripts/
│   ├── run.sh                       # Launch script
│   └── import_dataset.py            # Kaggle ETL script
└── tests/test_integration.py        # 40 integration tests
```

---

## 🏁 Local Setup

### 1. Clone & Install
```bash
git clone https://github.com/osama-kadhem/Individual-Web-Services-API-Development-Project.git
cd Individual-Web-Services-API-Development-Project
python3 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root:
```
DATABASE_URL=sqlite:///./data/ironmind.db
PROJECT_NAME=IronMind Coach API
VERSION=0.6.0
API_V1_STR=/api/v1
API_KEY=ironmind_secret_2026
```

### 3. Launch
```bash
./venv/bin/uvicorn app.main:app --reload
```

Server available at: **http://localhost:8000**

| URL | Purpose |
|---|---|
| http://localhost:8000/ | SPA Dashboard |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | Health check |

---

## 📊 Data Ingestion (Kaggle Dataset)

The API can be pre-populated with the **Athlete Training & Recovery Tracker** dataset from Kaggle.

```bash
# Download dataset
./venv/bin/python3 -c 'import kagglehub; kagglehub.dataset_download("prince7489/athlete-training-and-recovery-tracker-dataset")'

# Run ETL import
./venv/bin/python3 scripts/import_dataset.py
```

The ETL script:
- Converts `Training_Hours` → minutes (`× 60`)
- Maps `Recovery_Index` (0–100) → Soreness (1–10) inversely
- Derives athlete emails from string IDs (e.g. `A0001` → `athlete_a0001@ironmind.com`)
- Handles duplicate records gracefully
- Populates all 4 tables: Athletes, Sessions, SleepLogs, CheckIns

---

## � Security

| Mechanism | Detail |
|---|---|
| API Key Auth | `X-API-KEY` header required on all `/api/v1/` routes |
| CORS | Enabled for all origins (`allow_origins=["*"]`) |
| Rate Limiting | 120 req/min per IP globally; 30/min on `/health` |
| .env | Secret values in `.env`, excluded from git via `.gitignore` |
| HTTPS | Enforced on PythonAnywhere deployment |

---

## 📊 Core Concepts

### ACWR-Based Readiness Scoring

Readiness (0–100) is computed using the **Acute:Chronic Workload Ratio** method:

| ACWR Range | Zone | Score Effect |
|---|---|---|
| 0.8 – 1.3 | Optimal | +15 pts |
| > 1.5 | Danger (injury risk) | −20 pts |
| < 0.5 | Under-trained | −10 pts |

Sleep ≥ 8h: +10 pts | Sleep < 6.5h: −15 pts | Sleep quality ≥ 4: +5 pts

Score bands: **High** (80–100) · **Medium** (50–79) · **Low** (0–49)

> References: Gabbett (2016), Hulin et al. (2016), Foster et al. (2001)

### Training Prescription Tiers

| Tier | Trigger | Sessions/wk | RPE Cap |
|---|---|---|---|
| Rest | Readiness < 40 | 0 | — |
| Recover | ACWR > 1.5 | 2 | 5 |
| Maintain | ACWR 0.8–1.3 | 4 | 8 |
| Build | ACWR < 0.8 | 5 | 9 |

### Error Envelope

All errors return a consistent JSON structure:
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

## 🧪 Testing

```bash
./venv/bin/pytest tests/ -v
```

**40 tests, 0 failures** — covering CRUD lifecycles, input validation edge cases, ACWR algorithm correctness, security, and all analytics endpoints.

---

## 📖 API Documentation

- **User Manual**: [docs/USER_MANUAL.md](docs/USER_MANUAL.md)
- **Interactive Console**: [https://osamakadhem.pythonanywhere.com/docs](https://osamakadhem.pythonanywhere.com/docs)
- **Reference Manual**: [https://osamakadhem.pythonanywhere.com/redoc](https://osamakadhem.pythonanywhere.com/redoc)
- **PDF Documentation**: `docs/api_documentation.pdf`
