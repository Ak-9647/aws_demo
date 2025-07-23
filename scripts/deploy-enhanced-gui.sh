#!/bin/bash
# Deploy Enhanced GUI - Simplified Version
# Production Analytics Agent v4.1

set -e

echo "🚀 Deploying Enhanced GUI to Live Environment..."

# Configuration
REGION="us-west-2"
CLUSTER_NAME="production-analytics-agent-cluster"
SERVICE_NAME="production-analytics-agent-gui-service"
ACCOUNT_ID="280383026847"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/production-analytics-agent-gui"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

# Force update ECS service to pull new image
force_update_service() {
    print_info "Forcing ECS service update..."
    
    aws ecs update-service \
        --cluster ${CLUSTER_NAME} \
        --service ${SERVICE_NAME} \
        --force-new-deployment \
        --region ${REGION} > /dev/null
    
    print_success "Service update initiated"
}

# Wait for deployment
wait_for_deployment() {
    print_info "Waiting for deployment to complete..."
    
    # Wait for service to stabilize
    aws ecs wait services-stable \
        --cluster ${CLUSTER_NAME} \
        --services ${SERVICE_NAME} \
        --region ${REGION}
    
    print_success "Deployment completed"
}

# Test the deployment
test_deployment() {
    print_info "Testing deployed GUI..."
    
    GUI_URL="http://analytics-gui-alb-1184070249.us-west-2.elb.amazonaws.com"
    
    # Wait for service to be ready
    sleep 30
    
    # Test health
    for i in {1..5}; do
        if curl -s -f "${GUI_URL}/healthz" > /dev/null 2>&1; then
            print_success "GUI health check passed"
            break
        elif curl -s -f "${GUI_URL}" > /dev/null 2>&1; then
            print_success "GUI main page accessible"
            break
        else
            print_warning "Attempt $i: GUI not ready yet, waiting..."
            sleep 10
        fi
    done
    
    print_info "GUI URL: ${GUI_URL}"
}

# Main execution
main() {
    echo "🔧 Enhanced GUI Deployment"
    echo "=========================="
    echo "Cluster: ${CLUSTER_NAME}"
    echo "Service: ${SERVICE_NAME}"
    echo "Image: ${ECR_URI}:latest"
    echo ""
    
    # The image was already pushed successfully, so just update the service
    force_update_service
    wait_for_deployment
    test_deployment
    
    echo ""
    print_success "Enhanced GUI deployment completed!"
    echo ""
    echo "🌐 Access your enhanced GUI at:"
    echo "   http://analytics-gui-alb-1184070249.us-west-2.elb.amazonaws.com/"
    echo ""
    echo "🎯 New Features Available:"
    echo "- Real-time AgentCore Runtime connection"
    echo "- Progress indicators during processing"
    echo "- Advanced connection management"
    echo "- Enhanced visualizations"
    echo "- Session persistence"
}

main "$@"