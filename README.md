# IronMind Coach API

A specialized REST API for high-performance triathlon training, recovery tracking, and readiness analytics. Built using FastAPI and SQLAlchemy, this platform leverages sports science metrics (like ACWR) to help athletes optimize their training load and recovery cycles.

---

## 🚀 Features

- **Athlete Management**: Full profile lifecycle with unique email validation.
- **Training Logs**: Record sessions across multiple sports (Swim, Bike, Run) with RPE (Rate of Perceived Exertion) and duration tracking.
- **Recovery Tracking**: Log daily sleep duration and quality, plus subjective wellness check-ins (fatigue, stress, mood, soreness).
- **Readiness Insights**: Real-time analysis using Acute:Chronic Workload Ratio (ACWR) to project injury risk and performance readiness.
- **Predictive Simulator**: "What-If" simulator to project how planned training and sleep will affect future readiness scores.
- **Training Prescription**: Evidence-based weekly training plan (Rest / Recover / Maintain / Build) derived from live ACWR.
- **Coach Roster**: Squad-level overview with every athlete's live readiness score, sorted worst-first.
- **Training Analytics**: 14-day load distribution and trend summaries.
- **MCP Endpoint**: AI agent-compatible tool definitions (Model Context Protocol).
- **Rate Limiting**: 120 requests/minute per IP via slowapi.
- **Professional Docs**: Interactive API consoles via customized Swagger UI and ReDoc.

---

## 🛠️ Tech Stack

- **FastAPI**: Performance-focused modern web framework.
- **SQLAlchemy**: Robust ORM for database management.
- **Pydantic v2**: Data validation and schema definition.
- **SQLite**: Relational database storage.
- **slowapi**: Rate limiting middleware.
- **Pytest**: Comprehensive test suite (40 tests).
- **Uvicorn**: High-performance ASGI server.

---

## 📁 Project Structure

```
├── app/                           # Application core logic
│   ├── api/                       # API routes and endpoints
│   ├── core/                      # Configuration and error handling
│   ├── crud/                      # Database CRUD operations
│   ├── db/                        # Database session & base model
│   ├── models/                    # SQLAlchemy models
│   ├── schemas/                   # Pydantic data schemas
│   ├── services/                  # Business logic & analytics
│   └── static/                    # Dashboard SPA and documentation themes
├── scripts/                       # Deployment and utility scripts
├── tests/                         # Full automated test suite
├── .env                           # Environment configuration
└── README.md                      # Product documentation
```

---

## 🏁 Getting Started

### 1. Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

### 2. Launch the Platform
```bash
./scripts/run.sh
```
The server will be available at: **http://localhost:8000**

---

## � Data Ingestion (Kaggle Dataset)

To ensure real-world complexity, the API is pre-populated using the **Athlete Training & Recovery Tracker** dataset.

**Download & Import Process:**
```bash
# 1. Download from Kaggle via kagglehub
./venv/bin/python3 -c 'import kagglehub; kagglehub.dataset_download("prince7489/athlete-training-and-recovery-tracker-dataset")'

# 2. Run the ETL script to clean and map data to SQLite
./venv/bin/python3 scripts/import_dataset.py
```
*Note: The ETL script standardizes metrics, converts units (hours to minutes), and maps recovery indices to centralized wellness models.*

---

## �📖 API Documentation

The platform provides two interactive documentation interfaces:

- **Interactive Console (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Reference Manual (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **User Manual**: [docs/USER_MANUAL.md](docs/USER_MANUAL.md)

---

## 📊 Core Concepts

### Readiness Scoring
Readiness is calculated using a proprietary weighted algorithm that considers:
- **ACWR (Acute:Chronic Workload Ratio)**: A 7-day vs 28-day training load comparison. Optimal range is 0.8–1.3.
- **Sleep Metrics**: Duration and quality trends.
- **Subjective Wellness**: Daily check-ins for fatigue, stress, and mood.

### Error Handling
The API returns standardized JSON error envelopes:
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

## 🧪 Quality Assurance

We maintain a comprehensive test suite with **40 integration tests** covering all core logic, validation rules, and analytics.

```bash
./venv/bin/pytest tests/ -v
```
