# 🏊‍♂️ IronMind: Advanced Performance & Readiness Analytics API for High-Performance Coaching

[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![PythonAnywhere](https://img.shields.io/badge/Deployed-PythonAnywhere-blueviolet?style=for-the-badge&logo=pythonanywhere&logoColor=white)](https://osamakadhem.pythonanywhere.com)

> **IronMind Coach** is an enterprise-grade RESTful API designed for elite triathlon coaches and athletes. It transforms disparate training data into actionable "Readiness Insights" by leveraging the **Acute:Chronic Workload Ratio (ACWR)** and real-time environmental stress factors.

---

## 🌐 Live Infrastructure

| Environment | Endpoint |
| :--- | :--- |
| **🚀 SPA Dashboard** | [https://osamakadhem.pythonanywhere.com](https://osamakadhem.pythonanywhere.com) |
| **📜 Interactive Swagger UI** | [https://osamakadhem.pythonanywhere.com/docs](https://osamakadhem.pythonanywhere.com/docs) |
| **📘 ReDoc API Reference** | [https://osamakadhem.pythonanywhere.com/redoc](https://osamakadhem.pythonanywhere.com/redoc) |
| **💓 Health Metrics** | [https://osamakadhem.pythonanywhere.com/health](https://osamakadhem.pythonanywhere.com/health) |

**Authentication Credentials:**
*   **Master Access Key:** `ironmind_secret_2026` (Use for Dashboard/Swagger `X-API-KEY` header).
*   **Modern Auth:** Use the `/api/v1/auth/login` endpoint to receive a stateless **JWT Bearer Token**.

---

## 🏆 Beyond the Brief: Research-Led Innovations
This project extends the initial requirements with high-tier features designed to meet "Advanced Data Integration" and "Professional Implementation" rubrics.

### 🌡️ 1. Environment-Aware Readiness (External API Integration)
The API dynamically queries the **OpenWeatherMap API** for an athlete's city. Unlike static trackers, IronMind applies "Environmental Stress Penalties" to the Readiness Score:
*   **Heat Stress**: Prevents over-exertion in temperatures **>30°C** (-20 pts).
*   **Humidity Stress**: Monitors cardiovascular strain in high-humidity zones (-10 pts).
*   *Implementation: Uses asynchronous `httpx` for non-blocking external requests.*

### 📈 2. Interactive Load-Trends (Visual Analytics)
The dashboard integrates **Chart.js** to visualize the **14-day training load distribution**. This allows coaches to identify "spikes" in training intensity that lead to injury.

### 🔐 3. Security Hardening (JWT + RBAC)
*   **Encryption**: Passwords hashed using **Bcrypt** (Salted & Hashed).
*   **RBAC**: Implements **Role-Based Access Control**. `Coach` roles see squad-level rosters, while `Athlete` roles are restricted to personal metrics.

### � 4. Automated ETL & Portability
*   **Kaggle Integration**: A custom ETL script standardizes and imports the "Athlete Training Tracker" dataset.
*   **Data Portability**: A dedicated `GET /export` endpoint generates real-time **CSV downloads** of training history.

---

## 📁 System Architecture

```text
├── app/
│   ├── api/ v1/        # Central router with Dependency Injection
│   ├── core/           # Auth logic (JWT/API-Key), Config, and JSON Error Envelopes
│   ├── models/         # SQLAlchemy ORM definitions (Athletes, Sessions, Sleep, Checkins)
│   ├── schemas/        # Strict Pydantic v2 data validation
│   ├── services/       # Business Logic: ACWR Engine & Weather Analytics
│   └── static/         # Vanilla JS SPA Dashboard with Chart.js
├── scripts/            # Database initialization and Kaggle ETL loaders
├── docs/               # User Manual and Automated PDF Documentation
└── tests/              # 40+ Integration/Logic tests (Pytest)
```

---

## 📊 Core Concepts: The Science of Readiness

### 1. Acute:Chronic Workload Ratio (ACWR)
IronMind calculates training risk by comparing the last **7 days** of load (Acute) against the average of the last **28 days** (Chronic).
*   **The "Sweet Spot" (0.8 - 1.3)**: Optimal fitness building.
*   **The "Danger Zone" (> 1.5)**: High injury risk detected.

### 2. Evidence-Based Prescription
Based on **Gabbett (2016)**, the API automatically generates training tiers:
*   **Rest**: Readiness < 40.
*   **Recover**: ACWR detected in danger zone.
*   **Maintain/Build**: Optimal readiness and load balance.

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
# Initialize database and import 1,000 Kaggle records
PYTHONPATH=. python scripts/init_db.py
PYTHONPATH=. python scripts/import_dataset.py

# Launch the server
./venv/bin/uvicorn app.main:app --reload
```

---

## � Academic References
Integrated logic is supported by the following sports science consensus:

1.  **Gabbett, T.J. (2016)** 'The training—injury prevention paradox: should athletes be training smarter and harder?', *British Journal of Sports Medicine*.
2.  **Racinais, S., et al. (2015)** 'Consensus recommendations on training and competing in the heat', *BJSM*.
3.  **OpenWeather (2026)** *Current weather data API*. Available at: https://openweathermap.org/api.

---

## 📖 Component Documentation
*   📘 **[User Manual](docs/USER_MANUAL.md)**: How to use the API and Dashboard.
*   📕 **[API Reference](https://osamakadhem.pythonanywhere.com/redoc)**: Technical endpoint definitions.
*   🧪 **[Test Suite](tests/test_integration.py)**: Evidence of 40 passing integration tests.

---
*© 2026 IronMind High-Performance Systems · Designed for COM3011 Web Services*
