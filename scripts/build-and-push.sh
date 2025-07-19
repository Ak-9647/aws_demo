#!/bin/bash

# Build and Push Script for Analytics Agent
# Usage: ./scripts/build-and-push.sh [AWS_ACCOUNT_ID] [AWS_REGION]

set -e

# Default values
AWS_REGION=${2:-us-west-2}
AWS_ACCOUNT_ID=${1}

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Usage: $0 <AWS_ACCOUNT_ID> [AWS_REGION]"
    echo "Example: $0 123456789012 us-west-2"
    exit 1
fi

echo "🚀 Building and pushing Analytics Agent containers..."
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"

# Get ECR repository URLs from Terraform outputs
cd infrastructure
AGENT_REPO=$(terraform output -raw ecr_agent_repository_url)
GUI_REPO=$(terraform output -raw ecr_gui_repository_url)
cd ..

echo "Agent Repository: $AGENT_REPO"
echo "GUI Repository: $GUI_REPO"

# Authenticate Docker to ECR
echo "🔐 Authenticating Docker to ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push agent image
echo "🔨 Building agent image..."
cd agent
docker build -t analytics-agent:latest .
docker tag analytics-agent:latest $AGENT_REPO:latest
echo "📤 Pushing agent image..."
docker push $AGENT_REPO:latest
cd ..

# Build and push GUI image
echo "🔨 Building GUI image..."
cd gui
docker build -t analytics-gui:latest .
docker tag analytics-gui:latest $GUI_REPO:latest
echo "📤 Pushing GUI image..."
docker push $GUI_REPO:latest
cd ..

echo "✅ Build and push completed successfully!"
echo "Agent Image: $AGENT_REPO:latest"
echo "GUI Image: $GUI_REPO:latest"