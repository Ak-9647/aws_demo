#!/bin/bash
# Deploy Latest Agent to AgentCore Runtime
# Production Analytics Agent v4.1 - Enhanced Version

set -e

echo "🚀 Deploying Latest Agent to AgentCore Runtime..."

# Configuration
REGION="us-west-2"
ACCOUNT_ID="280383026847"
ECR_REPO_NAME="production-analytics-agent-agent"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}"
AGENT_VERSION="v4.1-enhanced"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check required files
    if [[ ! -f "agent/main.py" ]]; then
        print_error "Agent main.py not found. Please run from project root."
        exit 1
    fi
    
    if [[ ! -f "agent/requirements.txt" ]]; then
        print_error "Agent requirements.txt not found."
        exit 1
    fi
    
    # Check AWS CLI and Docker
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create optimized Dockerfile for agent
create_agent_dockerfile() {
    print_info "Creating optimized Dockerfile for agent..."
    
    cat > agent/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the agent
CMD ["python", "main.py"]
EOF
    
    print_success "Dockerfile created"
}

# Build and push agent image
build_and_push_agent() {
    print_info "Building enhanced agent Docker image..."
    
    # Change to agent directory
    cd agent
    
    # Build Docker image
    print_info "Building Docker image with latest features..."
    docker build -t ${ECR_REPO_NAME}:${AGENT_VERSION} .
    
    # Tag for ECR
    docker tag ${ECR_REPO_NAME}:${AGENT_VERSION} ${ECR_URI}:${AGENT_VERSION}
    docker tag ${ECR_REPO_NAME}:${AGENT_VERSION} ${ECR_URI}:latest
    
    print_success "Docker image built successfully"
    
    # Login to ECR
    print_info "Logging in to ECR..."
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}
    
    # Push to ECR
    print_info "Pushing enhanced agent image to ECR..."
    docker push ${ECR_URI}:${AGENT_VERSION}
    docker push ${ECR_URI}:latest
    
    print_success "Enhanced agent image pushed to ECR"
    
    # Return to project root
    cd ..
}

# Test agent locally before deployment
test_agent_locally() {
    print_info "Testing agent locally..."
    
    # Start agent container for testing
    print_info "Starting agent container for local testing..."
    
    CONTAINER_ID=$(docker run -d -p 8080:8080 ${ECR_REPO_NAME}:${AGENT_VERSION})
    
    # Wait for container to start
    sleep 10
    
    # Test health endpoint
    if curl -s -f http://localhost:8080/health > /dev/null; then
        print_success "Agent health check passed"
        
        # Test query processing
        print_info "Testing query processing..."
        RESPONSE=$(curl -s -X POST http://localhost:8080 \
            -H "Content-Type: application/json" \
            -d '{"query": "Test query for deployment validation"}')
        
        if [[ -n "$RESPONSE" ]]; then
            print_success "Agent query processing working"
            echo "   Response length: ${#RESPONSE} characters"
        else
            print_warning "Agent query processing may have issues"
        fi
    else
        print_error "Agent health check failed"
        docker logs $CONTAINER_ID
        docker stop $CONTAINER_ID
        exit 1
    fi
    
    # Stop test container
    docker stop $CONTAINER_ID > /dev/null
    print_success "Local testing completed"
}

# Display deployment instructions
show_deployment_instructions() {
    print_info "AgentCore Runtime Deployment Instructions..."
    
    echo ""
    echo "🔧 Manual AgentCore Runtime Update Required"
    echo "==========================================="
    echo ""
    echo "The enhanced agent image has been built and pushed to ECR:"
    echo "📦 Image URI: ${ECR_URI}:${AGENT_VERSION}"
    echo "📦 Latest URI: ${ECR_URI}:latest"
    echo ""
    echo "To update your AgentCore Runtime:"
    echo ""
    echo "1. 🌐 Open AWS Console → Amazon Bedrock → AgentCore"
    echo "2. 📋 Navigate to your Agent Runtime"
    echo "3. ⚙️  Click 'Update Runtime Configuration'"
    echo "4. 🖼️  Update Container Image to: ${ECR_URI}:${AGENT_VERSION}"
    echo "5. 💾 Save and Deploy"
    echo ""
    echo "🎯 Enhanced Features in v4.1:"
    echo "- ✅ LangGraph workflow orchestration"
    echo "- ✅ Database integration with natural language to SQL"
    echo "- ✅ Context engineering and memory management"
    echo "- ✅ MCP tools integration"
    echo "- ✅ AgentCore Gateway support"
    echo "- ✅ Advanced analytics and visualization"
    echo "- ✅ Comprehensive error handling"
    echo ""
    echo "🔗 After deployment, your GUI will connect to the enhanced runtime!"
}

# Create agent test script
create_test_script() {
    print_info "Creating agent test script..."
    
    cat > scripts/test-deployed-agent.py << 'EOF'
#!/usr/bin/env python3
"""
Test Deployed Agent
Tests the AgentCore runtime after deployment
"""

import boto3
import json
import time
from datetime import datetime

def test_agentcore_runtime():
    """Test the deployed AgentCore runtime."""
    print("🧪 Testing Deployed AgentCore Runtime")
    print("=" * 60)
    
    try:
        client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        # Test queries
        test_queries = [
            "Hello, test the enhanced agent",
            "Show me sales performance analysis",
            "What analytics capabilities do you have?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing query: '{query}'")
            
            try:
                start_time = time.time()
                
                response = client.invoke_agent(
                    agentId='your-agent-id',  # Update with actual agent ID
                    agentAliasId='TSTALIASID',
                    sessionId=f'test-session-{i}',
                    inputText=query
                )
                
                # Process streaming response
                response_text = ""
                for event in response['completion']:
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'bytes' in chunk:
                            response_text += chunk['bytes'].decode('utf-8')
                
                response_time = time.time() - start_time
                
                print(f"   ✅ Response received in {response_time:.2f}s")
                print(f"   📝 Response length: {len(response_text)} characters")
                
                if "error" not in response_text.lower():
                    print(f"   🎉 Query processed successfully")
                else:
                    print(f"   ⚠️  Response may contain errors")
                
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
        
        print("\n🎉 AgentCore runtime testing completed!")
        
    except Exception as e:
        print(f"❌ Failed to test AgentCore runtime: {e}")
        print("💡 Make sure to update the agent ID in the test script")

if __name__ == "__main__":
    test_agentcore_runtime()
EOF
    
    chmod +x scripts/test-deployed-agent.py
    print_success "Test script created: scripts/test-deployed-agent.py"
}

# Main deployment flow
main() {
    echo "🔧 Latest Agent Deployment to AgentCore Runtime"
    echo "==============================================="
    echo "Account: ${ACCOUNT_ID}"
    echo "Region: ${REGION}"
    echo "ECR Repository: ${ECR_URI}"
    echo "Agent Version: ${AGENT_VERSION}"
    echo ""
    
    check_prerequisites
    create_agent_dockerfile
    build_and_push_agent
    test_agent_locally
    create_test_script
    show_deployment_instructions
    
    echo ""
    print_success "Latest agent deployment preparation completed!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Update AgentCore Runtime with new image URI (see instructions above)"
    echo "2. Test the deployment with: python3 scripts/test-deployed-agent.py"
    echo "3. Verify GUI connection to enhanced runtime"
    echo ""
    echo "🎯 Your enhanced agent is ready for AgentCore Runtime deployment!"
}

# Run main function
main "$@"