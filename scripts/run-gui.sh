#!/bin/bash
# Run the Enhanced Analytics GUI
# Production Analytics Agent v4.1

set -e

echo "🚀 Starting Enhanced Analytics GUI..."

# Configuration
GUI_PORT="${GUI_PORT:-8501}"
AGENT_ENDPOINT="${AGENT_ENDPOINT:-http://localhost:8080}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if agent is running
print_info "Checking if agent is running..."
if curl -s "$AGENT_ENDPOINT/health" > /dev/null 2>&1; then
    print_success "Agent is running at $AGENT_ENDPOINT"
else
    print_warning "Agent not detected at $AGENT_ENDPOINT"
    print_info "GUI will use fallback mode"
fi

# Check dependencies
print_info "Checking GUI dependencies..."
python3 -c "import streamlit, plotly, pandas, boto3" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "All GUI dependencies available"
else
    print_warning "Some dependencies missing. Installing..."
    pip install streamlit plotly pandas boto3 pillow
fi

# Set environment variables
export AGENT_ENDPOINT="$AGENT_ENDPOINT"
export STREAMLIT_SERVER_PORT="$GUI_PORT"
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"

print_info "Starting Streamlit GUI on port $GUI_PORT..."
print_info "Agent endpoint: $AGENT_ENDPOINT"

# Change to GUI directory
cd "$(dirname "$0")/../gui"

# Start Streamlit
streamlit run app.py \
    --server.port=$GUI_PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --theme.base=light

print_success "GUI started successfully!"
print_info "Access the GUI at: http://localhost:$GUI_PORT"