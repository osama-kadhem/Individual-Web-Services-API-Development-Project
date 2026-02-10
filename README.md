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

### **Phase 3: Filtering, Pagination & Advanced Queries**

**Goal**: Add query capabilities for data retrieval and analysis

**Will Include**:
- ⏳ Pagination on all list endpoints (skip/limit)
- ⏳ Filter sessions by sport, athlete, date range
- ⏳ Filter sleep logs and check-ins by athlete, date range
- ⏳ Sorting capabilities
- ⏳ Query parameter validation
- ⏳ CORS middleware for web client support

**Enhanced Endpoints**:
- `GET /api/v1/sessions/?athlete_id=1&sport=run&start_date=2026-01-01`
- `GET /api/v1/sleep-logs/?athlete_id=1&start_date=2026-01-01&end_date=2026-01-31`
- `GET /api/v1/checkins/?athlete_id=1&skip=0&limit=10`

---

### **Phase 4: Insights & Analytics**

**Goal**: Provide meaningful insights from collected data

**Will Include**:
- ⏳ Readiness score trends over time
- ⏳ Training load summaries (weekly/monthly)
- ⏳ Sleep quality correlations with performance
- ⏳ Fatigue pattern analysis
- ⏳ Aggregated statistics endpoints
- ⏳ Data visualization support

**New Endpoints**:
- `GET /api/v1/insights/readiness/{athlete_id}` - Readiness trends
- `GET /api/v1/insights/training-load/{athlete_id}` - Training load summary
- `GET /api/v1/insights/sleep-analysis/{athlete_id}` - Sleep patterns

---

### **Phase 5: Production Ready**

**Goal**: Prepare for deployment and production use

**Will Include**:
- ⏳ Database migrations with Alembic
- ⏳ PostgreSQL support for production
- ⏳ Authentication & authorization (JWT)
- ⏳ Rate limiting
- ⏳ Caching layer (Redis)
- ⏳ Docker containerization
- ⏳ CI/CD pipeline
- ⏳ Comprehensive logging
- ⏳ Performance optimization

---

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **SQLite**: Local development database
- **Pytest**: Testing framework
- **Uvicorn**: ASGI server

---

## 📁 Project Structure (Phase 1)

```
project 1/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── api/
│   │   └── endpoints/
│   │       └── athletes.py        # Athletes endpoints
│   ├── core/
│   │   ├── config.py              # Settings
│   │   └── database.py            # Database
│   └── models/
│       ├── models.py              # Athlete model
│       └── schemas.py             # Athlete schemas
├── tests/
│   └── test_api.py                # Basic tests
├── requirements.txt
└── README.md
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
pip install -r requirements.txt
```

### 3. Run the Server
```bash
uvicorn app.main:app --reload
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

**Phase**: 2 of 5  
**Status**: ✅ Phase 2 Complete  
**Tests**: 16/16 passing  
**Endpoints**: 18 working  
**Entities**: 4 (Athletes, Sessions, SleepLogs, Check-ins)

---

## 🔜 Next Steps

To move to **Phase 3**, the following will be added:
- Pagination on all list endpoints (skip/limit)
- Advanced filtering for sessions, sleep, and check-ins
- Sorting capabilities
- Query parameter validation
- CORS middleware

---

## 📖 Additional Documentation

- `PHASE_1_COMPLETE.md` - Detailed Phase 1 summary
- `PHASE_2_COMPLETE.md` - Detailed Phase 2 summary
- API docs available at `/docs` when server is running

---

**Current Phase**: Phase 2 - Complete CRUD & Core Entities ✅
