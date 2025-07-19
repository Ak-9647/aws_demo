# Technical Guide - Production Analytics Agent

**Author**: Akshay Ramesh  
**License**: MIT

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Infrastructure Components](#infrastructure-components)
3. [Deployment Guide](#deployment-guide)
4. [Configuration](#configuration)
5. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
6. [Security Best Practices](#security-best-practices)

## Architecture Overview

The Production Analytics Agent is built on Amazon Bedrock AgentCore with a microservices architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   AgentCore     │    │   Data Sources  │
│   Frontend      │◄──►│   Runtime       │◄──►│   (S3, RDS)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ECS Fargate   │    │   Lambda/ECS    │    │   CloudWatch    │
│   (GUI)         │    │   (Agent)       │    │   (Monitoring)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

1. **AgentCore Runtime**: Hosts the LangGraph-based analytics agent
2. **Streamlit GUI**: Web interface for user interactions
3. **VPC Infrastructure**: Secure networking with public/private subnets
4. **ECR Repositories**: Container image storage
5. **S3 Bucket**: Encrypted storage for logs and data
6. **IAM Roles**: Least-privilege security model

## Infrastructure Components

### VPC Configuration
- **CIDR**: 10.0.0.0/16
- **Public Subnets**: 10.0.1.0/24, 10.0.2.0/24 (us-west-2a, us-west-2b)
- **Private Subnets**: 10.0.10.0/24, 10.0.11.0/24 (us-west-2a, us-west-2b)
- **NAT Gateways**: High availability across AZs
- **Internet Gateway**: Public internet access

### Security Groups
```hcl
# Agent Security Group (Private)
ingress {
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["10.0.0.0/16"]
}

# GUI Security Group (Public)
ingress {
  from_port   = 8501
  to_port     = 8501
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}
```

### IAM Roles

#### AgentCore Runtime Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "bedrock.amazonaws.com",
          "ecs-tasks.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Attached Policies**:
- S3 access to logs bucket
- Bedrock model invocation
- CloudWatch logs

## Deployment Guide

### Prerequisites
- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- Docker installed and running
- Python 3.13+

### Step 1: Infrastructure Deployment
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

**Expected Resources Created**: 35 resources including VPC, subnets, ECR, S3, IAM roles

### Step 2: Container Build & Push
```bash
# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build and push containers
./scripts/build-and-push.sh $AWS_ACCOUNT_ID us-west-2
```

### Step 3: AgentCore Deployment
1. Navigate to AWS Console → Bedrock → AgentCore → Agent Runtime
2. Click "Host Agent"
3. Configure:
   - **Image**: Use ECR URI from Terraform outputs
   - **IAM Role**: Use AgentCore Runtime role ARN
   - **CPU/Memory**: 1 vCPU, 2GB RAM (recommended)
   - **VPC**: Use created VPC and private subnets

### Step 4: Endpoint Creation
1. Create endpoint in AgentCore console
2. Test in Agent Sandbox:
```json
{
  "query": "Analyze sales data for Q4 2024"
}
```

### Step 5: GUI Deployment (Optional)
```bash
# Deploy to ECS Fargate
cd gui
docker run -p 8501:8501 \
  -e AGENT_ENDPOINT_URL="https://your-agentcore-endpoint" \
  analytics-gui:latest
```

## Configuration

### Environment Variables

#### Agent Configuration
```bash
# Agent Runtime
AWS_REGION=us-west-2
S3_BUCKET_NAME=production-analytics-agent-agent-logs-839dae02
LOG_LEVEL=INFO
```

#### GUI Configuration
```bash
# Streamlit GUI
AGENT_ENDPOINT_URL=https://your-agentcore-endpoint
AWS_REGION=us-west-2
STREAMLIT_SERVER_PORT=8501
```

### LangGraph Agent Configuration
```python
# agent/main.py
class AgentConfig:
    MAX_ITERATIONS = 10
    TIMEOUT_SECONDS = 300
    MEMORY_SIZE = "2GB"
    MODEL_NAME = "anthropic.claude-3-sonnet-20240229-v1:0"
```

## Monitoring & Troubleshooting

### CloudWatch Logs
- **Agent Logs**: `/aws/lambda/production-analytics-agent`
- **GUI Logs**: `/aws/ecs/production-analytics-gui`

### Key Metrics to Monitor
1. **Agent Response Time**: < 30 seconds
2. **Error Rate**: < 1%
3. **Memory Usage**: < 80%
4. **CPU Utilization**: < 70%

### Common Issues

#### Agent Not Responding
```bash
# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/bedrock/agentcore"

# Check agent health
curl -X POST https://your-endpoint/health
```

#### Container Build Failures
```bash
# Check Docker daemon
docker info

# Rebuild with verbose output
docker build --no-cache -t analytics-agent:debug ./agent/
```

#### Permission Errors
```bash
# Verify IAM role permissions
aws iam get-role --role-name production-analytics-agent-agentcore-runtime-role
aws iam list-attached-role-policies --role-name production-analytics-agent-agentcore-runtime-role
```

## Security Best Practices

### Network Security
- All agent traffic flows through private subnets
- NAT Gateways for outbound internet access
- Security groups with minimal required ports

### IAM Security
- Least-privilege principle applied
- No hardcoded credentials
- Role-based access control

### Data Security
- S3 bucket encryption at rest (AES-256)
- VPC endpoints for AWS service communication
- CloudTrail logging enabled

### Container Security
- Multi-stage Docker builds
- Minimal base images
- Regular security scanning with ECR

## Performance Optimization

### Agent Performance
```python
# Optimize LangGraph workflow
workflow = StateGraph(dict)
workflow.add_node("analytics", analytics_handler, parallel=True)
workflow.add_node("visualization", viz_handler, parallel=True)
```

### Infrastructure Scaling
```hcl
# Auto Scaling Configuration
resource "aws_appautoscaling_target" "agent" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/production-analytics/agent"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}
```

### Cost Optimization
- Use Spot instances for non-critical workloads
- Implement lifecycle policies for ECR images
- Monitor and optimize Bedrock model usage

## API Reference

### Agent Endpoints
```bash
# Health Check
GET /health

# Analytics Query
POST /analyze
{
  "query": "string",
  "context": "object",
  "options": {
    "format": "json|text",
    "include_visualization": boolean
  }
}
```

### Response Format
```json
{
  "status": "success|error",
  "data": {
    "analysis": "string",
    "visualization": "base64_image",
    "metadata": {
      "processing_time": "float",
      "model_used": "string",
      "tokens_consumed": "integer"
    }
  },
  "error": "string|null"
}
```

## Development Workflow

### Local Development
```bash
# Start local development environment
docker-compose up -d

# Run tests
python -m pytest tests/

# Format code
black agent/ gui/
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy Analytics Agent
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy Infrastructure
        run: |
          terraform init
          terraform apply -auto-approve
      - name: Build and Push
        run: ./scripts/build-and-push.sh
```

## Troubleshooting Guide

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run agent locally
python agent/main.py --debug
```

### Performance Profiling
```python
# Add to agent/main.py
import cProfile
import pstats

def profile_handler(event, context):
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = handler(event, context)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

---

For additional support, please refer to the [AWS Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock/) or create an issue in this repository.