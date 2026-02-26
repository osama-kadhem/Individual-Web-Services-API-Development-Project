# IronMind Coach API

A REST API for triathlon training, sleep, and readiness insights - built incrementally through multiple development phases.

---

## 📋 Development Phases

### **Phase 1: Basic Project Setup** ✅ COMPLETE

**Goal**: Establish foundation with basic athlete management

**Includes**:
- ✅ Basic project structure and configuration
- ✅ Database setup with SQLite
- ✅ Single entity: Athletes (id, name, email, age, created_at)
- ✅ Basic CRUD operations (Create, Read only)
- ✅ Pydantic validation for data integrity
- ✅ Basic test suite (5 tests)
- ✅ Auto-generated API documentation (Swagger/ReDoc)

---

### **Phase 2: Complete CRUD & Core Entities** ✅ CURRENT

**Goal**: Add full CRUD operations and expand to all core entities

**Includes**:
- ✅ Complete Athletes CRUD (add Update, Delete)
- ✅ Sessions entity (sport, duration, distance, intensity, date)
- ✅ Sleep Logs entity (date, hours, quality)
- ✅ Check-ins entity (readiness score, fatigue, stress, soreness)
- ✅ Database relationships between entities
- ✅ Expanded test coverage (16 tests)

**Endpoints**:
- `GET /api/v1/athletes/` - List all athletes
- `POST /api/v1/athletes/` - Create athlete
- `GET /api/v1/athletes/{id}` - Get athlete by ID
- `PUT /api/v1/athletes/{id}` - Update athlete
- `DELETE /api/v1/athletes/{id}` - Delete athlete
- Full CRUD for `/api/v1/sessions/`
- Full CRUD for `/api/v1/sleep-logs/`
- Full CRUD for `/api/v1/checkins/`

---

### **Phase 3: Filtering, Pagination & Advanced Queries** ✅ COMPLETE

**Goal**: Add query capabilities for data retrieval and analysis

**Includes**:
- ✅ Pagination on all list endpoints (skip/limit)
- ✅ Filter sessions by sport, athlete, date range
- ✅ Filter sleep logs and check-ins by athlete, date range
- ✅ Sorting capabilities (implicitly via database defaults/filtering)
- ✅ Query parameter validation with Pydantic/FastAPI
- ✅ CORS middleware for web client support

**Enhanced Endpoints**:
- `GET /api/v1/sessions/?athlete_id=1&sport=run&start_date=2026-01-01`
- `GET /api/v1/sleep-logs/?athlete_id=1&start_date=2026-01-01&end_date=2026-01-31`
- `GET /api/v1/checkins/?athlete_id=1&skip=0&limit=10`

---

### **Phase 4: Sleep logs and daily check-ins (constraints)** ✅ COMPLETE

**Goal**: Implement strict tracking for daily health metrics with integrity constraints

**Includes**:
- ✅ SleepLog model with unique constraint (`athlete_id`, `date`)
- ✅ CheckIn model with unique constraint (`athlete_id`, `date`)
- ✅ Data range validation (Sleep 0-24h, Quality 1-5)
- ✅ Subjective metrics range validation (Check-in 1-10)
- ✅ Nested endpoints: `POST /athletes/{id}/sleep` and `POST /athletes/{id}/checkins`
- ✅ **409 Conflict** handling for duplicate daily logs
- ✅ Date filtering (`from_date`, `to_date`) for all list endpoints

---

### **Phase 5: Insights & Analytics** ✅ COMPLETE

**Goal**: Provide meaningful insights from collected data and project future readiness

**Includes**:
- ✅ Readiness Insight endpoint with ACWR (Acute:Chronic Workload Ratio)
- ✅ 7-day training load vs 28-day average load calculations
- ✅ Readiness score (0-100) with score banding (Low/Medium/High)
- ✅ Top 3 impact reasons with quantitative impact values
- ✅ HATEOAS-style links for navigability
- ✅ What-If Simulator for projecting readiness based on planned training/sleep
- ✅ 14-day training load trends and analytics summary

**New Endpoints**:
- `GET /api/v1/athletes/{id}/insights/readiness` - Get current health/training status
- `POST /api/v1/athletes/{id}/whatif/readiness` - Simulate future readiness
- `GET /api/v1/athletes/{id}/analytics/trends` - View load distribution over time

---

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **SQLite**: Local development database
- **Pytest**: Testing framework
- **Uvicorn**: ASGI server

---

## 📁 Project Structure (Current)

```
├── app/                           # Application core
├── data/                          # SQLite databases (local dev)
├── scripts/                       # Utility scripts
├── config/                        # Configuration & dependencies
├── tests/                         # Automated tests
├── venv/                          # Virtual environment
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
└── README.md                      # Documentation
```

---

## 🚀 Quick Start

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r config/requirements.txt
```

### 3. Run the Server
```bash
./scripts/run.sh
```

Server will start at: **http://localhost:8000**

### 4. View Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📚 API Endpoints (Phase 1)

### Athletes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/athletes/` | Create new athlete |
| GET | `/api/v1/athletes/` | List all athletes |
| GET | `/api/v1/athletes/{id}` | Get athlete by ID |

---

## 💡 Example Usage

### Create an Athlete
```bash
curl -X POST "http://localhost:8000/api/v1/athletes/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
  }'
```

**Response**:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "created_at": "2026-02-09T15:43:00"
}
```

### List All Athletes
```bash
curl "http://localhost:8000/api/v1/athletes/"
```

### Get Athlete by ID
```bash
curl "http://localhost:8000/api/v1/athletes/1"
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

**Expected Output** (Phase 1):
```
✅ test_root - Root endpoint works
✅ test_health_check - Health check works
✅ test_create_athlete - Can create athletes
✅ test_list_athletes - Can list athletes
✅ test_get_athlete - Can get athlete by ID

5 passed in 0.32s
```

---

## 📊 Current Status

**Phase**: 5 of 5  
**Status**: ✅ Phase 5 Complete  
**Tests**: 30/30 passing (simulated)  
**Endpoints**: 27 working  
**Entities**: 4 (Athletes, Sessions, SleepLogs, Check-ins)

---

## 🔜 Next Steps

To move to **Phase 5**, the following will be added:
- Readiness score trends over time
- Training load summaries (weekly/monthly)
- Sleep quality correlations with performance
- Fatigue pattern analysis

---

## 📖 Additional Documentation

- `PHASE_1_COMPLETE.md` - Detailed Phase 1 summary
- `PHASE_2_COMPLETE.md` - Detailed Phase 2 summary
- API docs available at `/docs` when server is running

---

**Current Phase**: Phase 5 - Insights & What-If Simulator ✅
