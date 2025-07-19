#!/bin/bash

# Test Agent Locally
# Usage: ./scripts/test-agent.sh

set -e

echo "🧪 Testing Analytics Agent locally..."

# Test the agent Python code
echo "Testing agent main.py..."
cd agent
python main.py
cd ..

# Test building the Docker image
echo "🐳 Testing Docker build..."
cd agent
docker build -t analytics-agent-test:latest .
echo "✅ Agent Docker build successful"
cd ..

# Test GUI locally
echo "🖥️  Testing GUI locally..."
echo "Starting Streamlit on http://localhost:8501"
echo "Press Ctrl+C to stop"
cd gui
streamlit run app.py --server.port=8501