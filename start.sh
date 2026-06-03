#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 GPTFlow — Starting..."

# Kill existing process on port 8010
PID=$(lsof -ti :8010 2>/dev/null || true)
if [ -n "$PID" ]; then
    echo "⚠️  Port 8010 in use (PID $PID), killing..."
    kill $PID 2>/dev/null || true
    sleep 1
fi

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

echo "✅ Server running at http://localhost:8010"
echo "   Press Ctrl+C to stop"
echo ""

(sleep 2 && xdg-open http://localhost:8010) &

uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
