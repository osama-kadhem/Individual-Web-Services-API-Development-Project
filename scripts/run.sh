#!/bin/bash
# High-performance FastAPI runner for IronMind Coach API
echo "🚀 Igniting IronMind Coach API Platform..."
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload