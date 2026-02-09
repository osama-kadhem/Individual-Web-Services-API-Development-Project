#!/bin/bash

# IronMind Coach API - Quick Start Script

echo "🏃 Starting IronMind Coach API..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Start the server
echo "🚀 Server starting at http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "📖 ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

uvicorn app.main:app --reload
