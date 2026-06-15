#!/bin/bash

# Dark Pattern Detector - Local Runner (without Docker)
# Run this script to start everything locally

echo "🔍 Dark Pattern Detector — Local Setup"
echo "======================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found locally."
    echo "   Option 1: Install PostgreSQL"
    echo "   Option 2: Use Docker: docker-compose up postgres -d"
    echo ""
fi

# Check .env file
if [ ! -f .env ]; then
    echo "📋 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
    echo "   Get free key at: https://aistudio.google.com/app/apikey"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create PostgreSQL database (if psql available)
if command -v psql &> /dev/null; then
    echo ""
    echo "🗄️  Setting up database..."
    psql -U postgres -c "CREATE DATABASE darkpattern_db;" 2>/dev/null || true
    psql -U postgres -c "CREATE USER darkpattern_user WITH PASSWORD 'darkpattern_pass';" 2>/dev/null || true
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE darkpattern_db TO darkpattern_user;" 2>/dev/null || true
    echo "✅ Database ready"
fi

echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

echo "🎨 Starting Streamlit frontend on http://localhost:8501"
streamlit run frontend/app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "✅ Both services running!"
echo "   Frontend: http://localhost:8501"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'; exit 0" INT
wait
