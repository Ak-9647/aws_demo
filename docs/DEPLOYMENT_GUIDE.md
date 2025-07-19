# Deployment Guide - Production Analytics Agent

**Author**: Akshay Ramesh  
**License**: MIT

## Quick Start Deployment

### Prerequisites Checklist
- [ ] AWS CLI configured with admin permissions
- [ ] Terraform >= 1.0 installed
- [ ] Docker installed and running
- [ ] Git configured
- [ ] Kiro IDE (optional but recommended)

### 1-Click Deployment Script
```bash
#!/bin/bash
# deploy.sh - Complete deployment script

set -e

echo "🚀 Starting Production Analytics Agent Deployment"

# Step 1: Deploy Infrastructure
echo "📦 Deploying AWS Infrastructure..."
cd infrastructure
terraform init
terraform plan
terraform apply -auto-approve
cd ..

# Step 2: Build and Push Containers
echo "🐳 Building and pushing containers..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
./scripts/build-and-push.sh $AWS_ACCOUNT_ID us-west-2

# Step 3: Get deployment info
echo "📋 Deployment Information:"
cd infrastructure
terraform output
cd ..

echo "✅ Infrastructure deployment complete!"
echo "🔗 Next: Deploy to Bedrock AgentCore using the AWS Console"
```

## Detailed Deployment Steps

### Phase 1: Infrastructure Deployment

#### Step 1.1: Initialize Terraform
```bash
cd infrastructure
terraform init
```

**Expected Output:**
```
Initializing the backend...
Initializing provider plugins...
- Installing hashicorp/aws v5.100.0...
- Installing hashicorp/random v3.7.2...
Terraform has been successfully initialized!
```

#### Step 1.2: Plan Infrastructure
```bash
terraform plan
```

**Review the plan** - Should show 35 resources to be created:
- 1 VPC with subnets and networking
- 2 ECR repositories
- 1 S3 bucket with encryption
- Multiple IAM roles and policies
- NAT gateways and route tables

#### Step 1.3: Apply Infrastructure
```bash
terraform apply -auto-approve
```

**Expected Duration:** 3-5 minutes

**Critical Outputs to Note:**
```bash
agentcore_runtime_role_arn = "arn:aws:iam::ACCOUNT:role/production-analytics-agent-agentcore-runtime-role"
ecr_agent_repository_url = "ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/production-analytics-agent-agent"
ecr_gui_repository_url = "ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/production-analytics-agent-gui"
```

### Phase 2: Container Build & Push

#### Step 2.1: Authenticate Docker to ECR
```bash
aws ecr get-login-password --region us-west-2 | \
docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-west-2.amazonaws.com
```

#### Step 2.2: Build Agent Container
```bash
cd agent
docker build -t analytics-agent:latest .
docker tag analytics-agent:latest ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/production-analytics-agent-agent:latest
docker push ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/production-analytics-agent-agent:latest
cd ..
```

#### Step 2.3: Build GUI Container
```bash
cd gui
docker build -t analytics-gui:latest .
docker tag analytics-gui:latest ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/production-analytics-agent-gui:latest
docker push ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/production-analytics-agent-gui:latest
cd ..
```

**Or use the automated script:**
```bash
./scripts/build-and-push.sh $(aws sts get-caller-identity --query Account --output text) us-west-2
```

### Phase 3: Bedrock AgentCore Deployment

#### Step 3.1: Access AgentCore Console
1. Open AWS Console
2. Navigate to **Amazon Bedrock** → **AgentCore** → **Agent Runtime**
3. Click **"Host Agent"**

#### Step 3.2: Configure Agent Runtime
Fill in the following configuration:

**Basic Configuration:**
- **Agent Name**: `production-analytics-agent`
- **Description**: `Natural language analytics agent built with LangGraph`

**Container Configuration:**
- **Image URI**: `ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/production-analytics-agent-agent:latest`
- **Port**: `8080` (default)

**Compute Configuration:**
- **CPU**: `1 vCPU` (1024 CPU units)
- **Memory**: `2 GB` (2048 MB)

**IAM Configuration:**
- **Execution Role**: Use the AgentCore Runtime role ARN from Terraform outputs
- **Task Role**: Same as execution role

**Network Configuration (Optional):**
- **VPC**: Select the created VPC
- **Subnets**: Select private subnets
- **Security Groups**: Default or create custom

#### Step 3.3: Deploy Agent
1. Click **"Create Agent Runtime"**
2. Wait for status to change to **"Active"** (5-10 minutes)
3. Note the **Runtime ARN** for endpoint creation

### Phase 4: Endpoint Creation & Testing

#### Step 4.1: Create Endpoint
1. In AgentCore console, go to **"Endpoints"**
2. Click **"Create Endpoint"**
3. Configure:
   - **Endpoint Name**: `analytics-agent-endpoint`
   - **Agent Runtime**: Select your created runtime
   - **Auto Scaling**: Enable with min=1, max=5

#### Step 4.2: Test Agent
1. Go to **"Agent Sandbox"**
2. Select your endpoint
3. Test with sample query:
```json
{
  "query": "Hello, can you analyze some sample data?"
}
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": {
    "message": "Hello! I received your analytics query: 'Hello, can you analyze some sample data?'",
    "status": "success",
    "agent_version": "1.0.0"
  }
}
```

### Phase 5: GUI Deployment (Optional)

#### Option A: Local Development
```bash
cd gui
pip install -r requirements.txt
streamlit run app.py --server.port=8501
```

#### Option B: ECS Fargate Deployment
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name analytics-gui-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster analytics-gui-cluster \
  --service-name analytics-gui \
  --task-definition analytics-gui:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

## Environment-Specific Deployments

### Development Environment
```bash
# Use smaller resources
export TF_VAR_environment="dev"
export TF_VAR_instance_type="t3.micro"

# Deploy with development settings
terraform apply -var-file="dev.tfvars"
```

### Staging Environment
```bash
# Use staging configuration
export TF_VAR_environment="staging"
export TF_VAR_instance_type="t3.small"

# Deploy with staging settings
terraform apply -var-file="staging.tfvars"
```

### Production Environment
```bash
# Use production configuration
export TF_VAR_environment="prod"
export TF_VAR_instance_type="t3.medium"

# Deploy with production settings
terraform apply -var-file="prod.tfvars"
```

## Monitoring & Verification

### Health Checks
```bash
# Check infrastructure
terraform show

# Check containers
docker images | grep analytics

# Check AWS resources
aws ecr describe-repositories
aws s3 ls | grep analytics-agent
aws iam list-roles | grep analytics-agent
```

### CloudWatch Monitoring
1. **Agent Logs**: `/aws/bedrock/agentcore/production-analytics-agent`
2. **Infrastructure Metrics**: VPC Flow Logs, ECS metrics
3. **Custom Metrics**: Agent response time, error rates

### Performance Testing
```bash
# Load test the endpoint
curl -X POST https://your-agentcore-endpoint.amazonaws.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Test analytics query"}'

# Monitor response times
for i in {1..10}; do
  time curl -X POST https://your-endpoint/analyze \
    -H "Content-Type: application/json" \
    -d '{"query": "Performance test '$i'"}'
done
```

## Troubleshooting Common Issues

### Issue 1: Terraform Apply Fails
**Symptoms:** Permission denied or resource conflicts
**Solution:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify permissions
aws iam get-user

# Clean up and retry
terraform destroy
terraform apply
```

### Issue 2: Docker Build Fails
**Symptoms:** Package installation errors
**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t analytics-agent ./agent/

# Check base image
docker pull public.ecr.aws/lambda/python:3.13-arm64
```

### Issue 3: AgentCore Deployment Fails
**Symptoms:** Container won't start or health checks fail
**Solution:**
```bash
# Check container logs
aws logs describe-log-groups
aws logs get-log-events --log-group-name "/aws/bedrock/agentcore/..."

# Test container locally
docker run -p 8080:8080 analytics-agent:latest

# Verify IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn "arn:aws:iam::ACCOUNT:role/agentcore-runtime-role" \
  --action-names "bedrock:InvokeModel"
```

### Issue 4: Endpoint Not Responding
**Symptoms:** Timeout or connection errors
**Solution:**
```bash
# Check endpoint status
aws bedrock-agent get-agent-runtime --runtime-id "your-runtime-id"

# Verify network connectivity
aws ec2 describe-vpc-endpoints

# Test from within VPC
aws ssm start-session --target "instance-id"
curl http://internal-endpoint/health
```

## Rollback Procedures

### Emergency Rollback
```bash
# 1. Disable endpoint
aws bedrock-agent update-endpoint --endpoint-id "xxx" --status DISABLED

# 2. Rollback to previous container version
docker tag analytics-agent:previous analytics-agent:latest
./scripts/build-and-push.sh ACCOUNT us-west-2

# 3. Update agent runtime
aws bedrock-agent update-agent-runtime --runtime-id "xxx" --image-uri "previous-image"
```

### Infrastructure Rollback
```bash
# Rollback Terraform changes
terraform plan -destroy
terraform destroy -target="resource.name"

# Restore from backup
terraform import aws_s3_bucket.agent_logs "backup-bucket-name"
```

## Cost Optimization

### Resource Optimization
```bash
# Use Spot instances for development
export TF_VAR_use_spot_instances="true"

# Implement lifecycle policies
aws s3api put-bucket-lifecycle-configuration \
  --bucket analytics-agent-logs \
  --lifecycle-configuration file://lifecycle.json
```

### Monitoring Costs
```bash
# Set up billing alerts
aws budgets create-budget \
  --account-id ACCOUNT \
  --budget file://budget.json

# Monitor usage
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## Security Hardening

### Post-Deployment Security
```bash
# Enable GuardDuty
aws guardduty create-detector --enable

# Enable Config
aws configservice put-configuration-recorder \
  --configuration-recorder file://config-recorder.json

# Enable CloudTrail
aws cloudtrail create-trail \
  --name analytics-agent-trail \
  --s3-bucket-name cloudtrail-logs-bucket
```

### Access Control
```bash
# Create read-only role for monitoring
aws iam create-role --role-name AnalyticsAgentReadOnly \
  --assume-role-policy-document file://readonly-trust-policy.json

# Attach monitoring policies
aws iam attach-role-policy \
  --role-name AnalyticsAgentReadOnly \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
```

## Maintenance & Updates

### Regular Maintenance Tasks
1. **Weekly**: Review CloudWatch logs and metrics
2. **Monthly**: Update container images and dependencies
3. **Quarterly**: Review and update IAM policies
4. **Annually**: Conduct security audit and penetration testing

### Update Procedures
```bash
# Update agent code
git pull origin main
./scripts/build-and-push.sh ACCOUNT us-west-2

# Update infrastructure
terraform plan
terraform apply

# Update dependencies
pip-audit --fix
docker scout cves analytics-agent:latest
```

---

This deployment guide provides comprehensive instructions for deploying the Production Analytics Agent. For additional support or questions, please refer to the [Technical Guide](TECHNICAL_GUIDE.md) or create an issue in the repository.