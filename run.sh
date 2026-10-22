#!/usr/bin/env bash
# CineMatch AI - Launch Script
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🎬 Launching CineMatch AI - Movie Recommender (TF-IDF)"
echo "=========================================================="

# Check if .venv exists, otherwise create it
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Ensuring dependencies are installed..."
pip install -q -r requirements.txt

# Generate dataset if missing
if [ ! -f "data/movies.csv" ]; then
    echo "Generating curated movie dataset with authentic posters..."
    python3 data/build_expanded_dataset.py
fi

echo ""
echo "✨ Starting Flask Web Server on http://127.0.0.1:5001"
echo "Press Ctrl+C to stop."
echo "=========================================================="
echo ""

python3 app.py
