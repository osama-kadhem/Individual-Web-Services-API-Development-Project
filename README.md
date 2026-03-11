# 🏊‍♂️ IronMind: Advanced Performance & Readiness Analytics API for High-Performance Coaching

[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![PythonAnywhere](https://img.shields.io/badge/Deployed-PythonAnywhere-blueviolet?style=for-the-badge&logo=pythonanywhere&logoColor=white)](https://osamakadhem.pythonanywhere.com)

> **IronMind Coach** is an enterprise-grade RESTful API designed for elite triathlon coaches and athletes. It transforms disparate training data into actionable "Readiness Insights" by leveraging the **Acute:Chronic Workload Ratio (ACWR)** and real-time environmental stress factors.

---

## 🌐 Infrastructure & Access

### 🚀 Production (Live Deployment)
| Service | Endpoint |
| :--- | :--- |
| **Dashboard** | [https://osamakadhem.pythonanywhere.com](https://osamakadhem.pythonanywhere.com) |
| **Swagger UI** | [https://osamakadhem.pythonanywhere.com/docs](https://osamakadhem.pythonanywhere.com/docs) |
| **ReDoc Reference** | [https://osamakadhem.pythonanywhere.com/redoc](https://osamakadhem.pythonanywhere.com/redoc) |
| **Health Metrics** | [https://osamakadhem.pythonanywhere.com/health](https://osamakadhem.pythonanywhere.com/health) |

### 🛠️ Local Development (Mac/PC)
Once running locally (see Setup below), access these endpoints:
*   **Dashboard**: [http://localhost:8000](http://localhost:8000)
*   **Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Reference Manual**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

**Credentials:**
*   **Master Access Key:** `ironmind_secret_2026` (Use for Dashboard/Swagger `X-API-KEY` header).
*   **Modern Auth:** Use the `/api/v1/auth/login` endpoint to receive a stateless **JWT Bearer Token**.

---

## 🏆 Beyond the Brief: Research-Led Innovations
This project extends the initial requirements with high-tier features designed to meet "Advanced Data Integration" and "Professional Implementation" rubrics.

### 🌡️ 1. Environment-Aware Readiness (External API Integration)
The API dynamically queries the **OpenWeatherMap API** for an athlete's city. It applies "Environmental Stress Penalties" to the Readiness Score:
*   **Heat Stress**: Penalizes scores in temperatures **>30°C** (-20 pts).
*   **Humidity Stress**: Adjusts for extra cardiovascular strain in high-humidity zones (-10 pts).

### 📈 2. Interactive Load-Trends (Visual Analytics)
The dashboard integrates **Chart.js** to visualize the **14-day training load distribution**. This provides visual evidence for identifies "spikes" in training intensity.

### 🔐 3. Security Hardening (JWT + RBAC)
*   **Encryption**: Passwords secured using **Bcrypt** hashing.
*   **RBAC**: Implements **Role-Based Access Control**. `Coach` roles see squad-level rosters, while `Athlete` roles are restricted to personal metrics.

### 📥 4. Automated ETL & Portability
*   **Kaggle Integration**: A custom ETL script standardizes and imports the "Athlete Training Tracker" dataset.
*   **Data Portability**: A dedicated `GET /export` endpoint generates real-time **CSV downloads** of training history.

---

## 🏗️ System Architecture

```text
├── app/
│   ├── api/
│   │   ├── endpoints/       # Athlete, Sessions, Sleep, Checkins, Insights, Coaches
│   │   └── v1/api.py        # Central Router with Dependency Injection
│   ├── core/                # JWT Auth, Bcrypt Hashing, pydantic-settings
│   ├── crud/                # Encapsulated database access patterns
│   ├── models/              # SQLAlchemy ORM definitions
│   ├── schemas/             # Strict Pydantic v2 request/response schemas
│   ├── services/            # ACWR Engine & Weather Analytics Logic
│   └── static/              # SPA Frontend (HTML5 / Vanilla JS / Chart.js)
├── scripts/                 # ETL Importers (Kaggle) & DB Initializers
├── data/                    # Local SQLite storage and raw Kaggle CSVs
├── docs/                    # User Manual and Automated API Documentation
└── tests/                   # 40+ Integration/Critical Path tests (Pytest)
```

---

## 📊 Core Science Concepts

### 1. Acute:Chronic Workload Ratio (ACWR)
IronMind calculates training risk by comparing the last **7 days** of load (Acute) against the average of the last **28 days** (Chronic).
*   **The "Sweet Spot" (0.8 - 1.3)**: Optimal fitness building.
*   **The "Danger Zone" (> 1.5)**: High injury risk detected.

### 2. Evidence-Based Prescription
Based on **Gabbett (2016)**, the API automatically generates training recommendations:
*   **Rest / Recover / Maintain / Build** tiers derived from live readiness.

---

## 🏁 Developer Quickstart

### 1. Setup
```bash
git clone https://github.com/osama-kadhem/Individual-Web-Services-API-Development-Project.git
cd Individual-Web-Services-API-Development-Project
python3 -m venv venv && source venv/bin/activate
pip install -r config/requirements.txt
```

### 2. Run Locally
```bash
# Initialize database tables
PYTHONPATH=. python scripts/init_db.py

# Import 1,000 Kaggle records into SQLite
PYTHONPATH=. python scripts/import_dataset.py

# Launch the FastAPI server
./venv/bin/uvicorn app.main:app --reload
```

---

## 🔬 Academic References
Integrated logic is supported by the following sports science consensus and datasets:

1.  **Gabbett, T.J. (2016)** 'The training—injury prevention paradox: should athletes be training smarter and harder?', *British Journal of Sports Medicine*.
2.  **Racinais, S., et al. (2015)** 'Consensus recommendations on training and competing in the heat', *BJSM*.
3.  **Kaggle Dataset (2024)** 'Athlete Training and Recovery Tracker Dataset'. Available at: [Kaggle](https://www.kaggle.com/datasets/prince7489/athlete-training-and-recovery-tracker-dataset).
4.  **OpenWeather (2026)** *Current weather data API*. Available at: https://openweathermap.org/api.

---

## 📖 Component Documentation
*   📘 **[User Manual](docs/USER_MANUAL.md)**: Feature walkthrough and API guide.
*   📕 **[API Reference](https://osamakadhem.pythonanywhere.com/redoc)**: Technical endpoint definitions.
*   🧪 **[Test Suite](tests/test_integration.py)**: Evidence of 40 passing integration tests.

---
*© 2026 IronMind High-Performance Systems · Designed for COM3011 Web Services*
