#!/bin/bash
# Update Live GUI with Enhanced AgentCore Integration
# Production Analytics Agent v4.1

set -e

echo "🚀 Updating Live GUI with Enhanced AgentCore Integration..."

# Configuration
REGION="us-west-2"
CLUSTER_NAME="production-analytics-agent-cluster"
SERVICE_NAME="production-analytics-agent-gui-service"
ECR_REPO_NAME="production-analytics-agent-gui"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    fi
    
    # Check if GUI files exist
    if [[ ! -f "gui/app.py" ]] || [[ ! -f "gui/agentcore_client.py" ]]; then
        print_error "GUI files not found. Please run from project root."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Build and push new GUI image
build_and_push_image() {
    print_info "Building enhanced GUI Docker image..."
    
    # Change to GUI directory
    cd gui
    
    # Create Dockerfile if it doesn't exist
    if [[ ! -f "Dockerfile" ]]; then
        print_info "Creating Dockerfile for GUI..."
        cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
EOF
    fi
    
    # Create requirements.txt for GUI
    if [[ ! -f "requirements.txt" ]]; then
        print_info "Creating requirements.txt for GUI..."
        cat > requirements.txt << 'EOF'
streamlit>=1.28.0
boto3>=1.35.0
pandas>=2.0.0
plotly>=5.15.0
requests>=2.31.0
pillow>=10.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
EOF
    fi
    
    # Build Docker image
    print_info "Building Docker image..."
    docker build -t ${ECR_REPO_NAME}:latest .
    
    # Tag for ECR
    docker tag ${ECR_REPO_NAME}:latest ${ECR_URI}:latest
    docker tag ${ECR_REPO_NAME}:latest ${ECR_URI}:v4.1-enhanced
    
    print_success "Docker image built successfully"
    
    # Login to ECR
    print_info "Logging in to ECR..."
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}
    
    # Push to ECR
    print_info "Pushing image to ECR..."
    docker push ${ECR_URI}:latest
    docker push ${ECR_URI}:v4.1-enhanced
    
    print_success "Image pushed to ECR successfully"
    
    # Return to project root
    cd ..
}

# Update ECS service
update_ecs_service() {
    print_info "Updating ECS service with new image..."
    
    # Get current task definition
    TASK_DEF_ARN=$(aws ecs describe-services \
        --cluster ${CLUSTER_NAME} \
        --services ${SERVICE_NAME} \
        --region ${REGION} \
        --query 'services[0].taskDefinition' \
        --output text)
    
    print_info "Current task definition: ${TASK_DEF_ARN}"
    
    # Get task definition details
    TASK_DEF_JSON=$(aws ecs describe-task-definition \
        --task-definition ${TASK_DEF_ARN} \
        --region ${REGION} \
        --query 'taskDefinition')
    
    # Create new task definition with updated image
    NEW_TASK_DEF=$(echo ${TASK_DEF_JSON} | jq --arg IMAGE "${ECR_URI}:latest" '
        .containerDefinitions[0].image = $IMAGE |
        del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .placementConstraints, .compatibilities, .registeredAt, .registeredBy)
    ')
    
    # Register new task definition
    print_info "Registering new task definition..."
    NEW_TASK_DEF_ARN=$(echo ${NEW_TASK_DEF} | aws ecs register-task-definition \
        --region ${REGION} \
        --cli-input-json file:///dev/stdin \
        --query 'taskDefinition.taskDefinitionArn' \
        --output text)
    
    print_success "New task definition registered: ${NEW_TASK_DEF_ARN}"
    
    # Update service
    print_info "Updating ECS service..."
    aws ecs update-service \
        --cluster ${CLUSTER_NAME} \
        --service ${SERVICE_NAME} \
        --task-definition ${NEW_TASK_DEF_ARN} \
        --region ${REGION} > /dev/null
    
    print_success "ECS service update initiated"
}

# Wait for deployment to complete
wait_for_deployment() {
    print_info "Waiting for deployment to complete..."
    
    # Wait for service to stabilize
    aws ecs wait services-stable \
        --cluster ${CLUSTER_NAME} \
        --services ${SERVICE_NAME} \
        --region ${REGION}
    
    print_success "Deployment completed successfully"
}

# Test updated GUI
test_updated_gui() {
    print_info "Testing updated GUI..."
    
    GUI_URL="http://analytics-gui-alb-1184070249.us-west-2.elb.amazonaws.com"
    
    # Wait a moment for the service to be ready
    sleep 30
    
    # Test GUI health
    if curl -s -f "${GUI_URL}/healthz" > /dev/null; then
        print_success "GUI health check passed"
    else
        print_warning "GUI health check failed (may still be starting)"
    fi
    
    # Test main page
    if curl -s -f "${GUI_URL}" > /dev/null; then
        print_success "GUI main page accessible"
        print_info "GUI URL: ${GUI_URL}"
    else
        print_error "GUI main page not accessible"
        return 1
    fi
    
    # Run comprehensive test
    if [[ -f "scripts/test-live-gui.py" ]]; then
        print_info "Running comprehensive GUI test..."
        python3 scripts/test-live-gui.py
    fi
}

# Main deployment flow
main() {
    echo "🔧 Enhanced GUI Deployment to Live Environment"
    echo "=============================================="
    echo "Cluster: ${CLUSTER_NAME}"
    echo "Service: ${SERVICE_NAME}"
    echo "ECR Repository: ${ECR_URI}"
    echo "Region: ${REGION}"
    echo ""
    
    check_prerequisites
    build_and_push_image
    update_ecs_service
    wait_for_deployment
    test_updated_gui
    
    echo ""
    print_success "Enhanced GUI deployment completed successfully!"
    echo ""
    echo "📋 Deployment Summary:"
    echo "- Enhanced GUI with AgentCore integration deployed"
    echo "- Real-time query processing enabled"
    echo "- Progress indicators and connection management added"
    echo "- Advanced visualization support included"
    echo ""
    echo "🌐 Access your enhanced GUI at:"
    echo "   http://analytics-gui-alb-1184070249.us-west-2.elb.amazonaws.com/"
    echo ""
    echo "🎯 New Features Available:"
    echo "- AgentCore Runtime connection"
    echo "- Real-time progress indicators"
    echo "- Advanced chart generation"
    echo "- Session management"
    echo "- Connection status monitoring"
}

# Run main function
main "$@"