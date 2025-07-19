#!/bin/bash

# Complete Deployment Script for Production Analytics Agent
# Author: Akshay Ramesh
# License: MIT

set -e

echo "🚀 Starting Production Analytics Agent Deployment"
echo "Author: Akshay Ramesh"
echo "Repository: https://github.com/Ak-9647/aws_demo"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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
print_status "Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check Terraform
if ! command -v terraform &> /dev/null; then
    print_error "Terraform not found. Please install Terraform first."
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker daemon
if ! docker info &> /dev/null; then
    print_error "Docker daemon not running. Please start Docker first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

print_success "All prerequisites met!"

# Get AWS account information
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-west-2}

print_status "Deploying to AWS Account: $AWS_ACCOUNT_ID"
print_status "AWS Region: $AWS_REGION"

# Step 1: Deploy Infrastructure
print_status "📦 Deploying AWS Infrastructure..."
cd infrastructure

# Initialize Terraform
print_status "Initializing Terraform..."
terraform init

# Plan deployment
print_status "Planning infrastructure deployment..."
terraform plan -out=tfplan

# Apply infrastructure
print_status "Applying infrastructure changes..."
terraform apply tfplan

# Capture outputs
print_status "Capturing Terraform outputs..."
terraform output -json > ../terraform-outputs.json

cd ..
print_success "Infrastructure deployment complete!"

# Step 2: Build and Push Containers
print_status "🐳 Building and pushing containers..."

# Make script executable
chmod +x scripts/build-and-push.sh

# Build and push
./scripts/build-and-push.sh $AWS_ACCOUNT_ID $AWS_REGION

print_success "Container build and push complete!"

# Step 3: Display deployment information
print_status "📋 Deployment Summary:"
echo ""
echo "=================================="
echo "DEPLOYMENT INFORMATION"
echo "=================================="
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo ""

# Extract key information from Terraform outputs
if [ -f terraform-outputs.json ]; then
    AGENT_IMAGE=$(cat terraform-outputs.json | jq -r '.ecr_agent_repository_url.value')
    GUI_IMAGE=$(cat terraform-outputs.json | jq -r '.ecr_gui_repository_url.value')
    IAM_ROLE=$(cat terraform-outputs.json | jq -r '.agentcore_runtime_role_arn.value')
    S3_BUCKET=$(cat terraform-outputs.json | jq -r '.s3_bucket_name.value')
    VPC_ID=$(cat terraform-outputs.json | jq -r '.vpc_id.value')
    
    echo "🐳 Container Images:"
    echo "  Agent: $AGENT_IMAGE:latest"
    echo "  GUI: $GUI_IMAGE:latest"
    echo ""
    echo "🔐 IAM Role for AgentCore:"
    echo "  $IAM_ROLE"
    echo ""
    echo "📦 S3 Bucket for Logs:"
    echo "  $S3_BUCKET"
    echo ""
    echo "🌐 VPC ID:"
    echo "  $VPC_ID"
    echo ""
fi

echo "=================================="
echo "NEXT STEPS"
echo "=================================="
echo "1. 🎯 Deploy to Bedrock AgentCore:"
echo "   - Go to AWS Console → Bedrock → AgentCore → Agent Runtime"
echo "   - Click 'Host Agent'"
echo "   - Use the Agent Image URI and IAM Role ARN above"
echo ""
echo "2. 🔗 Create AgentCore Endpoint:"
echo "   - Create endpoint in AgentCore console"
echo "   - Test in Agent Sandbox"
echo ""
echo "3. 🖥️  Access Streamlit GUI:"
echo "   - Run locally: cd gui && streamlit run app.py"
echo "   - Or deploy to ECS Fargate"
echo ""
echo "4. 📚 Documentation:"
echo "   - Deployment Guide: docs/DEPLOYMENT_GUIDE.md"
echo "   - User Guide: docs/USER_GUIDE.md"
echo "   - Technical Guide: docs/TECHNICAL_GUIDE.md"
echo "   - Kiro Usage Guide: docs/KIRO_USAGE_GUIDE.md"
echo ""
echo "=================================="

print_success "🎉 Deployment completed successfully!"
print_status "Repository: https://github.com/Ak-9647/aws_demo"
print_status "Author: Akshay Ramesh"

# Clean up
rm -f terraform-outputs.json

echo ""
print_status "Happy analyzing! 🚀"